import json
import os
import re
import urllib.parse
from typing import Any

import boto3
import requests
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from botocore.exceptions import ClientError
from langchain_google_genai import ChatGoogleGenerativeAI

app = BedrockAgentCoreApp()
APP_VERSION = "2026-02-25-doc-only-deterministic-v2"

GATEWAY_URL = os.environ["GATEWAY_URL"]
GOOGLE_DOCS_TOOL_NAME = os.environ["GOOGLE_DOCS_TOOL_NAME"]
MCP_VERSION = os.environ.get("GATEWAY_MCP_VERSION", "2025-11-25")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
GOOGLE_MODEL_ID = os.environ.get("GOOGLE_MODEL_ID", "gemini-3-flash-preview")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip()
DOC_CONTEXT_MAX_CHARS = int(os.environ.get("DOC_CONTEXT_MAX_CHARS", "12000"))
GOOGLE_MAX_OUTPUT_TOKENS = int(os.environ.get("GOOGLE_MAX_OUTPUT_TOKENS", "512"))

ac_runtime = boto3.client("bedrock-agentcore", region_name=AWS_REGION)
if not GOOGLE_API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY environment variable.")

llm = ChatGoogleGenerativeAI(
    model=GOOGLE_MODEL_ID,
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
    max_output_tokens=GOOGLE_MAX_OUTPUT_TOKENS,
)

AGENT_CTX: dict[str, Any] = {
    "doc_id": "",
    "access_token": "",
    "oauth_session_uri": "",
    "mcp_session_id": "",
    "consent_pending": "0",
    "max_doc_calls": 1,
    "doc_call_count": 0,
    "doc_cached_result": "",
    "last_authorization_url": "",
    "last_oauth_session_uri": "",
    "oauth_return_url": "",
    "force_authentication": "0",
}


def mcp_request(
    bearer_token: str,
    method: str,
    params: dict[str, Any],
    mcp_session_id: str | None = None,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": MCP_VERSION,
    }
    if mcp_session_id and not mcp_session_id.startswith("urn:ietf:params:oauth:request_uri:"):
        headers["x-mcp-session-id"] = mcp_session_id

    response = requests.post(
        GATEWAY_URL,
        headers=headers,
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def extract_mcp_text(payload: dict[str, Any]) -> str:
    content = payload.get("result", {}).get("content", [])
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(str(item.get("text", "")))
    return "\n".join(parts).strip()


def parse_google_doc_payload(mcp_payload: dict[str, Any]) -> dict[str, Any]:
    merged = extract_mcp_text(mcp_payload)
    if not merged:
        return {}
    try:
        obj = json.loads(merged)
    except Exception:
        return {}

    if isinstance(obj, dict) and "body" in obj and isinstance(obj["body"], str):
        try:
            return json.loads(obj["body"])
        except Exception:
            return {"raw_body": obj["body"]}
    return obj if isinstance(obj, dict) else {}


def _collect_text_runs(node: Any, out: list[str]) -> None:
    if isinstance(node, dict):
        text_run = node.get("textRun")
        if isinstance(text_run, dict):
            content = str(text_run.get("content", "")).strip()
            if content:
                out.append(content)
        for value in node.values():
            _collect_text_runs(value, out)
        return

    if isinstance(node, list):
        for item in node:
            _collect_text_runs(item, out)


def extract_google_doc_text(doc: dict[str, Any]) -> str:
    chunks: list[str] = []
    # Parse across the whole document object, not only body.content,
    # because newer Google Docs payloads can keep text under tabs.
    _collect_text_runs(doc, chunks)
    return "\n".join(chunks)


def extract_elicitation_url(payload: dict[str, Any]) -> str | None:
    try:
        return payload["error"]["data"]["elicitations"][0]["url"]
    except Exception:
        return None


def extract_request_uri_from_url(url: str | None) -> str | None:
    if not url:
        return None
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    values = query.get("request_uri")
    if not values:
        return None
    return urllib.parse.unquote(values[0])


def build_authorization_url(request_uri: str | None) -> str:
    if not request_uri:
        return ""
    encoded = urllib.parse.quote(request_uri, safe="")
    return f"https://bedrock-agentcore.{AWS_REGION}.amazonaws.com/identities/oauth2/authorize?request_uri={encoded}"


def complete_oauth_session(access_token: str, oauth_session_uri: str) -> None:
    ac_runtime.complete_resource_token_auth(
        userIdentifier={"userToken": access_token},
        sessionUri=oauth_session_uri,
    )


def message_to_text(msg: Any) -> str:
    content = getattr(msg, "content", msg)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if "text" in item:
                    parts.append(str(item["text"]))
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def parse_tool_output(tool_text: str) -> dict[str, str]:
    out = {
        "kind": "other",
        "authorization_url": "",
        "oauth_session_uri": "",
        "document_text": "",
        "source_url": "",
    }

    if tool_text.startswith("CONSENT_REQUIRED"):
        out["kind"] = "consent"
        auth = re.search(r"authorization_url:\s*(https?://\S+)", tool_text)
        sess = re.search(r"oauth_session_uri:\s*(\S+)", tool_text)
        out["authorization_url"] = auth.group(1) if auth else ""
        out["oauth_session_uri"] = sess.group(1) if sess else ""
        return out

    if tool_text.startswith("ERROR:"):
        out["kind"] = "error"
        return out

    if tool_text.startswith("EMPTY_DOCUMENT"):
        out["kind"] = "empty"
        src = re.search(r"SOURCE:\s*(https?://\S+)", tool_text)
        out["source_url"] = src.group(1) if src else ""
        return out

    if tool_text.startswith("DOCUMENT_TEXT:"):
        out["kind"] = "document"
        source_split = tool_text.split("\n\nSOURCE:", 1)
        body = source_split[0].replace("DOCUMENT_TEXT:\n", "", 1)
        out["document_text"] = body.strip()
        if len(source_split) > 1:
            out["source_url"] = source_split[1].strip()
        return out

    return out


def get_google_doc() -> str:
    doc_id = AGENT_CTX.get("doc_id", "")
    token = AGENT_CTX.get("access_token", "")
    oauth_session_uri = AGENT_CTX.get("oauth_session_uri", "")
    mcp_session_id = AGENT_CTX.get("mcp_session_id", "")
    consent_pending = AGENT_CTX.get("consent_pending", "0") == "1"
    oauth_return_url = str(AGENT_CTX.get("oauth_return_url", "")).strip()
    force_authentication = AGENT_CTX.get("force_authentication", "0") == "1"
    max_doc_calls = int(AGENT_CTX.get("max_doc_calls", 1))
    doc_call_count = int(AGENT_CTX.get("doc_call_count", 0))
    cached = str(AGENT_CTX.get("doc_cached_result", ""))

    if not doc_id:
        return "ERROR: doc_id is empty in agent context."
    if not token:
        return "ERROR: user_access_token is empty in agent context."

    if consent_pending:
        auth_url = AGENT_CTX.get("last_authorization_url", "")
        req_uri = AGENT_CTX.get("last_oauth_session_uri", "")
        return (
            "CONSENT_REQUIRED\n"
            f"authorization_url: {auth_url}\n"
            f"oauth_session_uri: {req_uri}"
        )

    if doc_call_count >= max_doc_calls:
        if cached:
            return cached
        return f"ERROR: get_google_doc call budget reached ({max_doc_calls})."

    if oauth_session_uri:
        try:
            complete_oauth_session(token, oauth_session_uri)
            AGENT_CTX["consent_pending"] = "0"
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            msg = exc.response.get("Error", {}).get("Message", str(exc))
            return (
                "ERROR: complete_resource_token_auth failed.\n"
                f"code: {code}\n"
                f"message: {msg}"
            )

    params: dict[str, Any] = {
        "name": GOOGLE_DOCS_TOOL_NAME,
        "arguments": {"documentId": doc_id},
    }
    meta_cfg: dict[str, Any] = {}
    if oauth_return_url:
        meta_cfg["returnUrl"] = oauth_return_url
    if force_authentication:
        meta_cfg["forceAuthentication"] = True
    # Always request USER_FEDERATION metadata for OAuth targets.
    # If returnUrl is omitted, Gateway uses target defaultReturnUrl.
    params["_meta"] = {
        "aws.bedrock-agentcore.gateway/credentialProviderConfiguration": {
            "oauthCredentialProvider": meta_cfg
        }
    }

    try:
        payload = mcp_request(
            token,
            "tools/call",
            params,
            mcp_session_id=mcp_session_id,
        )
    except requests.HTTPError as exc:
        status = getattr(exc.response, "status_code", "unknown")
        body = (getattr(exc.response, "text", "") or "")[:800]
        return (
            "ERROR: MCP HTTP failure while calling Google Docs tool.\n"
            f"status: {status}\n"
            f"body: {body}"
        )
    except requests.RequestException as exc:
        return f"ERROR: MCP network failure while calling Google Docs tool: {exc}"
    AGENT_CTX["doc_call_count"] = doc_call_count + 1

    if "error" in payload and payload["error"].get("code") == -32042:
        auth_url = extract_elicitation_url(payload) or ""
        req_uri = extract_request_uri_from_url(auth_url) or ""
        AGENT_CTX["consent_pending"] = "1"
        AGENT_CTX["last_authorization_url"] = auth_url
        AGENT_CTX["last_oauth_session_uri"] = req_uri
        return (
            "CONSENT_REQUIRED\n"
            f"authorization_url: {auth_url}\n"
            f"oauth_session_uri: {req_uri}"
        )

    if "error" in payload:
        return f"ERROR: MCP get_google_doc failed: {payload['error']}"

    raw_text = extract_mcp_text(payload)
    if bool((payload.get("result") or {}).get("isError")):
        return (
            "ERROR: MCP get_google_doc returned isError=true.\n"
            f"message: {raw_text[:800]}"
        )

    doc_payload = parse_google_doc_payload(payload)
    if not doc_payload:
        return (
            "ERROR: Could not parse Google Docs tool response.\n"
            f"raw: {raw_text[:800]}"
        )

    doc_text = extract_google_doc_text(doc_payload)
    source_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    if not doc_text:
        result_text = f"EMPTY_DOCUMENT\nSOURCE: {source_url}"
        AGENT_CTX["doc_cached_result"] = result_text
        return result_text

    result_text = f"DOCUMENT_TEXT:\n{doc_text}\n\nSOURCE: {source_url}"
    AGENT_CTX["doc_cached_result"] = result_text
    return result_text


def _session_from_context(context: Any) -> str:
    if context is None:
        return ""
    if isinstance(context, dict):
        return str(context.get("session_id") or context.get("sessionId") or "")
    return str(getattr(context, "session_id", None) or getattr(context, "sessionId", None) or "")


@app.entrypoint
def invoke(payload: dict, context=None):
    thread_id = str(payload.get("thread_id") or "").strip() or _session_from_context(context) or "runtime-default-thread"

    AGENT_CTX["doc_id"] = str(payload.get("doc_id", "")).strip()
    AGENT_CTX["access_token"] = str(payload.get("user_access_token", "")).strip()
    AGENT_CTX["oauth_session_uri"] = str(payload.get("oauth_session_uri", "")).strip()
    AGENT_CTX["mcp_session_id"] = str(payload.get("mcp_session_id", "")).strip() or thread_id
    AGENT_CTX["consent_pending"] = "0"
    AGENT_CTX["oauth_return_url"] = str(payload.get("oauth_return_url", "")).strip()
    AGENT_CTX["force_authentication"] = "1" if bool(payload.get("force_authentication", False)) else "0"

    try:
        AGENT_CTX["max_doc_calls"] = max(1, min(3, int(payload.get("max_doc_calls", 1))))
    except (TypeError, ValueError):
        AGENT_CTX["max_doc_calls"] = 1

    AGENT_CTX["doc_call_count"] = 0
    AGENT_CTX["doc_cached_result"] = ""
    AGENT_CTX["last_authorization_url"] = ""
    AGENT_CTX["last_oauth_session_uri"] = ""

    try:
        max_steps = int(payload.get("max_steps", 5))
    except (TypeError, ValueError):
        max_steps = 5
    recursion_limit = max(2, min(8, max_steps))

    tool_text = get_google_doc()
    parsed = parse_tool_output(tool_text)

    trace = [
        {
            "step": 1,
            "event": "tool_call",
            "tool": "get_google_doc",
            "args": {"documentId": AGENT_CTX.get("doc_id", "")},
        },
        {
            "step": 2,
            "event": "tool_result",
            "tool": "get_google_doc",
            "preview": tool_text[:240] + ("..." if len(tool_text) > 240 else ""),
        },
    ]

    authorization_url = ""
    oauth_session_uri = ""
    consent_required = False

    if parsed["kind"] == "consent":
        oauth_session_uri = parsed.get("oauth_session_uri", "")
        raw_auth = parsed.get("authorization_url", "")
        if not oauth_session_uri:
            oauth_session_uri = extract_request_uri_from_url(raw_auth) or ""
        authorization_url = build_authorization_url(oauth_session_uri) if oauth_session_uri else raw_auth
        consent_required = bool(authorization_url)
        answer = (
            "Google consent required.\n"
            f"authorization_url: {authorization_url}\n"
            f"oauth_session_uri: {oauth_session_uri}\n"
            "Complete consent in browser, then re-run with the same oauth_session_uri."
        )
    elif parsed["kind"] == "error":
        answer = tool_text
    elif parsed["kind"] == "empty":
        src = parsed.get("source_url", "")
        answer = "The document is empty."
        if src:
            answer += f"\n\nSources:\n- {src}"
    elif parsed["kind"] == "document":
        doc_text = parsed.get("document_text", "")
        source_url = parsed.get("source_url", "")
        if not doc_text:
            answer = "ERROR: Document text is empty after parsing tool result."
        else:
            doc_for_model = doc_text[:DOC_CONTEXT_MAX_CHARS]
            prompt = (
                "You are a concise technical assistant. "
                "Answer using only the document context below. "
                "If the answer is not present in the document, say exactly: 'Not found in document.'\n\n"
                f"User question:\n{str(payload.get('prompt', ''))}\n\n"
                f"Document context:\n{doc_for_model}\n\n"
                "Return concise bullets, then add a Sources section. "
                "Do not exceed 180 words."
            )
            llm_resp = llm.invoke(prompt)
            answer = message_to_text(llm_resp).strip()
            if len(answer) > 4000:
                answer = answer[:4000].rstrip() + "\n\n[truncated]"
            if source_url and source_url not in answer:
                answer = f"{answer}\n\nSources:\n- {source_url}"
    else:
        answer = "ERROR: Unexpected tool output format."

    return {
        "app_version": APP_VERSION,
        "recursion_limit": recursion_limit,
        "response": answer,
        "tool_trace": trace,
        "tools_used": ["get_google_doc"],
        "tool_call_counts": {
            "get_google_doc": AGENT_CTX.get("doc_call_count", 0),
        },
        "tool_call_limits": {
            "get_google_doc": AGENT_CTX.get("max_doc_calls", 1),
        },
        "consent_required": consent_required,
        "authorization_url": authorization_url,
        "oauth_session_uri": oauth_session_uri,
        "thread_id": thread_id,
    }


if __name__ == "__main__":
    app.run()
