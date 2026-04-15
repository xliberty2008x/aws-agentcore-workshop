import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage, ToolMessage

import runtime_app_agentcore_full as runtime_app


def mock_react_state(tool_output: str, final_text: str = "Tool completed.") -> dict[str, list]:
    return {
        "messages": [
            AIMessage(
                content="Calling tool",
                tool_calls=[
                    {
                        "name": "get_google_doc",
                        "args": {},
                        "id": "call-1",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(content=tool_output, tool_call_id="call-1", name="get_google_doc"),
            AIMessage(content=final_text),
        ]
    }


class RuntimeAppTests(unittest.TestCase):
    def test_extract_google_doc_text_normalizes_runs(self) -> None:
        payload = {
            "body": {
                "content": [
                    {"paragraph": {"elements": [{"textRun": {"content": "Hello "}}]}},
                    {"paragraph": {"elements": [{"textRun": {"content": "world\n\n"}}]}},
                    {"paragraph": {"elements": [{"textRun": {"content": "Line 2"}}]}},
                ]
            }
        }

        text = runtime_app.extract_google_doc_text(payload)

        self.assertEqual(text, "Hello world\n\nLine 2")

    def test_build_structured_answer_for_summary(self) -> None:
        doc_text = (
            "Detection starts from monitoring alerts and customer reports.\n"
            "On-call engineers create tickets and assign severity.\n"
            "Responders mitigate impact and coordinate communication.\n"
        )

        answer = runtime_app.build_structured_answer(
            prompt="Summarize incident response in 6 bullets",
            doc_text=doc_text,
            source_url="https://docs.google.com/document/d/test/edit",
        )

        self.assertEqual(answer["kind"], "bullet_summary")
        self.assertEqual(len(answer["bullets"]), 3)
        self.assertEqual(
            answer["sources"],
            ["https://docs.google.com/document/d/test/edit"],
        )

    def test_build_structured_answer_returns_not_found_for_irrelevant_query(self) -> None:
        answer = runtime_app.build_structured_answer(
            prompt="What does the document say about Kubernetes autoscaling?",
            doc_text="This document only covers incident response roles and process.",
            source_url="https://docs.google.com/document/d/test/edit",
        )

        self.assertEqual(answer["kind"], "not_found")
        self.assertEqual(answer["bullets"], [])

    def test_invoke_returns_structured_answer_payload(self) -> None:
        fake_tool_output = (
            "DOCUMENT_TEXT:\n"
            "Detection starts from monitoring alerts and customer reports.\n"
            "On-call engineers create tickets and assign severity.\n\n"
            "SOURCE: https://docs.google.com/document/d/test/edit"
        )

        with (
            patch.object(
                runtime_app,
                "run_react_agent",
                return_value=mock_react_state(fake_tool_output, final_text="Here is the summary."),
            ),
            patch.object(
                runtime_app,
                "get_settings",
                return_value={"DOC_CONTEXT_MAX_CHARS": 12000, "AWS_REGION": "us-east-1"},
            ),
        ):
            payload = runtime_app.invoke(
                {
                    "prompt": "Summarize incident response in 6 bullets",
                    "doc_id": "test-doc",
                    "user_access_token": "token",
                }
            )

        self.assertEqual(payload["answer_mode"], "deterministic_extractive")
        self.assertEqual(payload["answer"]["kind"], "bullet_summary")
        self.assertTrue(payload["answer"]["bullets"])
        self.assertIn("Sources:", payload["response"])
        self.assertEqual(payload["tool_call_counts"], {"get_google_doc": 1})
        self.assertEqual(payload["tools_used"], ["get_google_doc"])
        self.assertEqual(payload["tool_trace"][0]["event"], "tool_call")
        self.assertEqual(payload["tool_trace"][1]["event"], "tool_result")

    def test_invoke_returns_consent_payload_when_gateway_needs_consent(self) -> None:
        mock_response = (
            "CONSENT_REQUIRED\n"
            "authorization_url: https://example.com/auth\n"
            "oauth_session_uri: urn:ietf:params:oauth:request_uri:test"
        )

        with (
            patch.object(
                runtime_app,
                "run_react_agent",
                return_value=mock_react_state(mock_response, final_text="Consent required."),
            ),
            patch.object(
                runtime_app,
                "get_settings",
                return_value={"DOC_CONTEXT_MAX_CHARS": 12000, "AWS_REGION": "us-east-1"},
            ),
        ):
            payload = runtime_app.invoke(
                {
                    "prompt": "Summarize incident response in 6 bullets",
                    "doc_id": "test-doc",
                    "user_access_token": "token",
                }
            )

        self.assertTrue(payload["consent_required"])
        self.assertIn("bedrock-agentcore", payload["authorization_url"])
        self.assertIn("request_uri%3Atest", payload["authorization_url"])
        self.assertEqual(payload["oauth_session_uri"], "urn:ietf:params:oauth:request_uri:test")
        self.assertEqual(payload["answer"]["kind"], "consent")

    def test_invoke_returns_error_when_tool_fails(self) -> None:
        with (
            patch.object(
                runtime_app,
                "run_react_agent",
                return_value=mock_react_state("ERROR: http failure", final_text="Tool failed."),
            ),
            patch.object(
                runtime_app,
                "get_settings",
                return_value={"DOC_CONTEXT_MAX_CHARS": 12000, "AWS_REGION": "us-east-1"},
            ),
        ):
            payload = runtime_app.invoke(
                {
                    "prompt": "Summarize incident response in 6 bullets",
                    "doc_id": "test-doc",
                    "user_access_token": "token",
                }
            )

        self.assertEqual(payload["answer_mode"], "error")
        self.assertEqual(payload["answer"]["kind"], "error")


if __name__ == "__main__":
    unittest.main()
