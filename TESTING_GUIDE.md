# TESTING_GUIDE.md

This guide bridges your existing `workshop_google_docs_rag_e2e.ipynb` with the Level 2 testing requirements for the AgentCore + AWS Cognito + AgentCore Gateway + AgentCore Runtime flow using Google Docs OAuth.

---

## 1. Dataset Usage Strategy

In this workshop notebook, the dataset is effectively controlled by the Google Docs `documentId` that is passed into the Runtime payload:

- `payload1['doc_id'] = os.environ['GOOGLE_DOC_ID']`
- `payload2['doc_id'] = os.environ['GOOGLE_DOC_ID']`

So, to switch datasets, you typically only need to set (or override) the environment variable `GOOGLE_DOC_ID` before running the Runtime invoke cells.

### Type 1: Baseline Dataset (Стандартний документ)

- **What it is:** The original Google Doc from the workshop (the one containing the expected incident-response / workshop content).
- **How to use it:** Set `GOOGLE_DOC_ID` to the workshop document ID (the real one you were given in the workshop).
- **General expected outcome:** Tool calls succeed and the agent returns content grounded in the document (normal positive RAG flow).

### Type 2: Empty Dataset (Порожній документ)

- **What it is:** A blank Google Doc (no meaningful text).
- **How to use it:** Create/obtain a blank Google Doc, then set `GOOGLE_DOC_ID` to its document ID.
- **General expected outcome:** Tool call still succeeds at the API/adapter level, but the agent returns an “empty document” / “no text” style outcome (in this workshop runtime this typically maps to an empty-document handling path).

### Type 3: Irrelevant Dataset (Нерелевантний документ)

- **What it is:** A Google Doc that contains unrelated text (not incident response).
- **How to use it:** Create/obtain a document with unrelated content, then set `GOOGLE_DOC_ID` to that doc’s document ID.
- **General expected outcome:** The tool call succeeds, but the answer either does not find matching evidence or produces an answer that does not align with the expected incident-response facts (this is a “semantic mismatch” test).

### Type 4: Invalid ID Dataset (Некоректний ID документа)

- **What it is:** A fake / incorrect `documentId` string that does not correspond to an actual Google Doc.
- **How to use it:** Set `GOOGLE_DOC_ID` to an invalid value (example format: `fake-doc-id-12345`), and re-run Runtime invoke.
- **General expected outcome:** The Google Docs tool call fails (commonly “not found” / invalid document), and the agent should respond with a **graceful failure** message rather than crashing.

---

## 2. How to Interpret Errors and Deviations

Use this section during notebook runs to decide whether you found a real defect or you’re seeing an expected failure mode.

### HTTP `401 Unauthorized` / `403 Forbidden`

This almost always points to a problem with **Inbound Authentication (Cognito JWT)**.

- The token is likely invalid, expired, or malformed.
- The system is correctly rejecting an unauthorized user.

In the notebook, this may surface as an HTTP error (and sometimes as a raised `RuntimeError` because the notebook checks `if not respX.ok: raise RuntimeError(...)`).

### HTTP `502 Bad Gateway` / `504 Gateway Timeout`

This indicates a problem with the **Gateway or AgentCore Runtime infrastructure** itself.

- The Gateway might not be able to reach the Runtime.
- The runtime call may have exceeded response time expectations.

Treat these as backend/infrastructure errors rather than tool-logic failures.

### Agent responds with `"I couldn't access the document..."` or similar

This is usually a **graceful failure** and is a GOOD outcome for many negative tests.

In this workshop runtime, you may see messages like:
- `ERROR: MCP get_google_doc failed: ...`
- `ERROR: MCP get_google_doc returned isError=true. ...`
- or an “empty document” style message

What matters: the notebook should not crash unexpectedly, and the user-facing response should clearly indicate the tool/document access problem (often triggered by invalid `documentId`, revoked Google consent, or tool/API errors).

### Agent responds with incorrect or “hallucinated” information

This points to a problem with the **LLM reasoning** or the system prompt/tooling contract.

- Infrastructure is likely fine (tool call may have succeeded).
- The “brain” may be using wrong assumptions or not grounding answers correctly.

Mitigation usually involves prompt/tool evidence constraints and/or adjusting how the runtime constructs the evidence context.

### A `RuntimeError` or other Python crash in the notebook output

This indicates a **critical bug in the Python code** of the notebook/agent workflow that needs developer attention.

However, in this workshop notebook you may see `RuntimeError` for negative tests when the HTTP response is not `ok` (for example, `AUTH-002` expected `401/403`). In that case, the status code in the error message is the key:
- If the HTTP status matches the test expectation (e.g., `401` for malformed JWT), it is an expected negative-test outcome.
- If the error message is unrelated to expected HTTP failure modes, treat it as a real defect.

---

## 3. Step-by-Step Test Execution

The steps below reference the notebook blocks by their visible headings and the variables inside Step 5.

### AUTH-001: Valid JWT allows agent invocation

**Objective:** Verify the agent endpoint accepts a valid Cognito access token and returns a successful HTTP response.

**Dataset to Use:** Type 1 (Baseline Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Run `## Step 1 - Inbound auth (Cognito)` (generates `user_access_token` via `get_user_access_token()`).
   2. Run `## Step 2 - Outbound provider + Gateway` (creates OAuth provider + Gateway + target; ensures gateway smoke-test passes).
   3. Run `## Step 4 - Deploy runtime through AgentCore CLI` (deploys `runtime_app_agentcore_full.py`).
   4. Run `## Step 5 - Runtime invoke + consent` **first invoke part** (the cell that builds `payload1` and calls `resp1 = requests.post(...)`).
2. **Modification (if any):**
   - None. Keep the default `GOOGLE_DOC_ID` and keep the generated `user_access_token`.
3. **Execution: which cell to run**
   - Execute the `payload1` invoke cell in `Step 5` (the cell that prints `HTTP status: ...` and `FIRST INVOKE`).
4. **Verification: what to look for**
   - `HTTP status:` should be `200` and the cell should proceed to print `FIRST INVOKE` results.
   - If Google consent has not been granted yet, `authorization_url` may be present (that is OK for this test); the key is that **authentication succeeded** (no `401/403`).

Expected: successful invocation (HTTP `200`); no inbound-auth rejection.

---

### AUTH-002: Malformed JWT rejected

**Objective:** Verify the system rejects malformed/invalid Cognito JWT access tokens.

**Dataset to Use:** Type 1 (Baseline Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Run `## Step 1 - Inbound auth (Cognito)` (so the rest of the notebook has the required AWS/Gateway setup values).
   2. Run `## Step 2 - Outbound provider + Gateway`.
   3. Run `## Step 4 - Deploy runtime through AgentCore CLI`.
2. **Modification (if any):**
   - After `Step 1` generates `user_access_token`, override it with a malformed value before running Step 5.
   - For example, right after the line:
     - `user_access_token = get_user_access_token()`
   - Set:
     - `user_access_token = "malformed.jwt.token"`
3. **Execution: which cell to run**
   - Execute the `payload1` invoke cell in `Step 5` (the one that sets the header `Authorization: f'Bearer {user_access_token}'` and calls `requests.post(...)`).
4. **Verification: what to look for**
   - The cell should fail with an HTTP auth rejection, typically `401 Unauthorized` or `403 Forbidden`.
   - If the notebook raises a `RuntimeError`, check that the error message contains the expected HTTP status and that it matches the interpretation guide:
     - `401/403` -> inbound authentication (Cognito JWT) is rejecting the request.

Expected: request rejected; no tool call / runtime logic should proceed.

---

### GATE-001: Tool identified and routed (positive)

**Objective:** Verify the agent chooses to call the Google Docs tool and the Gateway successfully routes the tool call through to the target.

**Dataset to Use:** Type 1 (Baseline Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Run `## Step 1 - Inbound auth (Cognito)`.
   2. Run `## Step 2 - Outbound provider + Gateway` (gateway + tool registration).
   3. Run `## Step 4 - Deploy runtime through AgentCore CLI`.
2. **Modification (if any):**
   - None for the positive routing test.
3. **Execution: which cell to run**
   - Execute the `Step 5` first-invoke cell (`payload1`, prints `FIRST INVOKE`).
   - If you see `authorization_url`, open it in the browser, complete consent, then execute the next `Step 5` cell (the second-invoke cell that builds `payload2` and calls `resp2 = requests.post(...)`).
4. **Verification: what to look for**
   - In `SECOND INVOKE` results:
     - `consent_required` should be `False` (or `authorization_url` should be empty).
     - `tools_used` should include the workshop runtime tool name (runtime returns `tools_used: ["get_google_doc"]`).
     - `tool_trace` should show `tool_call` / tool events where `tool: "get_google_doc"` is used (the notebook printout shows event/tool names, not the full `args`).
     - `response` should contain a meaningful summary derived from the document and should include a source link that contains your `GOOGLE_DOC_ID`.

Expected: tool routed successfully; response grounded in the baseline Google doc.

---

### GATE-003: Google Docs returns document not found

**Objective:** Verify graceful handling when Google Docs API cannot find the document (wrong `documentId`).

**Dataset to Use:** Type 4 (Invalid ID Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Run `## Step 1 - Inbound auth (Cognito)`.
   2. Run `## Step 2 - Outbound provider + Gateway`.
   3. Run `## Step 4 - Deploy runtime through AgentCore CLI`.
   4. Make sure Google consent for the flow is already granted for your session/thread if possible (otherwise the test may stop at OAuth first and you won’t reach the “document not found” tool call).
2. **Modification (if any):**
   - Set `GOOGLE_DOC_ID` to a fake/incorrect value (Type 4).
   - Do this before running `Step 5`, so both `payload1['doc_id']` and `payload2['doc_id']` are invalid.
3. **Execution: which cell to run**
   - Execute the `Step 5` first-invoke cell (payload1).
   - Then execute the second-invoke cell (payload2) if it runs (unless `SKIP_SECOND_INVOKE=1` is set).
4. **Verification: what to look for**
   - You should not see an unexpected Python crash.
   - The agent response in `FIRST INVOKE` or `SECOND INVOKE` should indicate a graceful failure related to tool/document access (interpretation guide: “agent responds with ‘I couldn't access the document…’ or similar” is a GOOD outcome for negative tests).
   - In this workshop runtime, expected patterns include:
     - `response` starts with `ERROR:` (e.g., `ERROR: MCP get_google_doc failed: ...`)
     - or an explicit empty-document style outcome (if your “invalid dataset” results in empty parse).

Expected: controlled error response; no crash; no consent prompt if already authorized.

---

### OAUTH-001: First-time consent returns authorization_url

**Objective:** Verify the first runtime invoke triggers Google consent and returns `authorization_url`.

**Dataset to Use:** Type 1 (Baseline Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Run `## Step 1 - Inbound auth (Cognito)`.
   2. Run `## Step 2 - Outbound provider + Gateway`.
   3. Run `## Step 4 - Deploy runtime through AgentCore CLI`.
   4. Before running `Step 5`, ensure you are in a “first-time consent” condition:
      - easiest: set a fresh `RUNTIME_THREAD_ID` value (unique string) before running `Step 5`,
      - or delete/recreate resources (heavier) via the cleanup cell and rerun.
2. **Modification (if any):**
   - Optionally set `RUNTIME_THREAD_ID` (env var) to a new value, so you get a new consent challenge.
3. **Execution: which cell to run**
   - Execute the `Step 5` **first-invoke cell** (the one that calls `resp1 = requests.post(...)` for `payload1`).
4. **Verification: what to look for**
   - In the `FIRST INVOKE` output:
     - `authorization_url` should be non-empty.
     - `oauth_session_uri` should be non-empty.
   - The notebook should print: “Open authorization_url in browser, complete consent, then run next cell.”

Expected: first invoke returns a consent URL.

---

### OAUTH-003: Post-consent second call returns document content

**Objective:** After consent is granted, verify the second invoke executes immediately and returns document content.

**Dataset to Use:** Type 1 (Baseline Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Complete all preparation from `OAUTH-001` up through the `FIRST INVOKE` output.
2. **Modification (if any):**
   - None. Use the same session values (do not change `RUNTIME_THREAD_ID` between first and second invoke).
3. **Execution: which cell to run**
   1. Open `authorization_url` from the first invoke result in a browser and complete Google consent.
   2. Return to the notebook and execute the `Step 5` **second-invoke cell** (the one that calls `complete_resource_token_auth(...)` and then `resp2 = requests.post(...)` for `payload2`).
4. **Verification: what to look for**
   - In `SECOND INVOKE` output:
     - `authorization_url` should be empty / not returned again.
     - `consent_required` should be `False`.
     - `tools_used` should include `get_google_doc`.
     - `response` should contain a meaningful summary and source link derived from your baseline document.
     - `answer_mode` should indicate a normal document-based output path (not an error/consent-only mode).

Expected: post-consent execution returns the document content-based answer.

---

### RUNTIME-001: Agent uses tool when needed

**Objective:** Verify the runtime agent uses the Google Docs tool for a doc-grounded request (not direct chat).

**Dataset to Use:** Type 1 (Baseline Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Run `## Step 1 - Inbound auth (Cognito)`.
   2. Run `## Step 2 - Outbound provider + Gateway`.
   3. Run `## Step 4 - Deploy runtime through AgentCore CLI`.
   4. Ensure consent is already granted so the runtime proceeds to tool execution (you can reuse post-OAUTH flow, or run OAUTH-001 first and then come back).
2. **Modification (if any):**
   - Usually none: the default `RUNTIME_PROMPT_1` is doc-specific:
     - `Summarize incident response from this document in 6 bullets and include source.`
   - If needed, you can override prompt via env var `RUNTIME_PROMPT_1` before running `Step 5`.
3. **Execution: which cell to run**
   - Execute the `payload1` invoke cell in `Step 5` (first invoke).
4. **Verification: what to look for**
   - In `FIRST INVOKE` results:
     - `tools_used` should include `get_google_doc`.
     - `tool_call_counts` should show `get_google_doc` was called (>= 1).
     - `tool_trace` should show the `tool: "get_google_doc"` tool call event(s).
     - `response` should be document-based (not “CONSENT_REQUIRED”).

Expected: runtime tool call happens when the prompt is doc-grounded.

---

### RUNTIME-003: Tool failure triggers helpful fallback

**Objective:** Verify that when the tool fails (e.g., invalid doc id), the runtime returns a helpful error/graceful fallback instead of crashing.

**Dataset to Use:** Type 4 (Invalid ID Dataset)

**Steps in the Notebook:**

1. **Preparation: which cells to run**
   1. Run `## Step 1 - Inbound auth (Cognito)`.
   2. Run `## Step 2 - Outbound provider + Gateway`.
   3. Run `## Step 4 - Deploy runtime through AgentCore CLI`.
   4. Ensure consent is already granted (otherwise you may receive consent_required output instead of reaching the tool error).
2. **Modification (if any):**
   - Set `GOOGLE_DOC_ID` to an invalid/fake document id (Type 4) before running Step 5.
3. **Execution: which cell to run**
   - Execute the `payload1` invoke cell in `Step 5` (first invoke).
   - Then execute the second-invoke cell if it runs.
4. **Verification: what to look for**
   - The notebook should not crash unexpectedly (HTTP call should still return a response you can inspect, even if it’s an error payload).
   - In `FIRST INVOKE` or `SECOND INVOKE` results:
     - `answer_mode` should be an error path (or `response` should start with `ERROR:`).
     - The response should indicate document/tool access failure (graceful failure).
   - If you see a message like “couldn’t access the document” / “ERROR: MCP get_google_doc failed …”, interpret it as a GOOD negative outcome per the interpretation guide.

Expected: graceful failure with a helpful message; no unhandled exception/crash.

