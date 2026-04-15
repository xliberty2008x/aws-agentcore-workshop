# Workshop Goal (3-5 lines)
- Build a beginner-friendly LangGraph agent locally with mock tools and mock RAG behavior.
- Show how the same agent is wrapped and deployed with AgentCore Runtime on AWS.
- Demonstrate core AgentCore services through one realistic scenario: docs retrieval + Lambda deployment workflow.
- Teach participants how to test locally, deploy safely, and invoke/debug in cloud.
- End with a working cloud invocation and observable execution path.

## Request Flow (local -> cloud) (6-10 bullets)
- User sends a request in local notebook/CLI.
- LangGraph entry node receives input and initializes state.
- Agent decides whether to answer directly, call a tool, or use retrieval.
- If retrieval is needed, local mock RAG is queried first.
- Tool outputs + retrieval context are merged into graph state.
- Agent returns response locally for debugging and validation.
- Same workflow is wrapped by AgentCore Runtime entrypoint for cloud hosting.
- Cloud invocation repeats the same graph logic, now using AWS-hosted services.

## Decision Flow (how the agent chooses tools/RAG) (6-10 bullets)
- Classify query intent: factual lookup, live data, or computation.
- If answer likely in knowledge base, run RAG retrieval first.
- If query requires fresh/external data, call web/API tool.
- If query requires numeric transformation, call Python/Code Interpreter tool.
- If retrieved context confidence is low, augment with tool call.
- Merge evidence from RAG and tools into final reasoning context.
- Generate final answer with short citations/explanations.
- Log selected path (RAG-only, tool-only, hybrid) for observability.

## Persistence Flow (thread/session/memory) (6-10 bullets)
- Local prototype uses a LangGraph checkpointer for thread state.
- Same `thread_id` in local runs should resume prior state.
- New `thread_id` in local runs should start with isolated state.
- In cloud, AgentCore Runtime uses `session_id` for continuity.
- Same `session_id` should continue conversation context.
- New `session_id` should isolate context from previous users/sessions.
- AgentCore Memory can store durable facts/preferences across sessions.
- Optional `actor_id`/user identity can scope memory by user.

## Service Mapping Table
| Need | Local (LangGraph) | AgentCore Service |
| --- | --- | --- |
| Runtime hosting | Run graph via local Python entrypoint | AgentCore Runtime |
| Conversation persistence | Local checkpointer/thread state | AgentCore Memory + Runtime session handling |
| Authentication/authorization | Local `.env` / dev credentials | AgentCore Identity |
| External API/tool exposure | Local Python tools or stubs | AgentCore Gateway |
| Web and code execution tools | Local tool mocks / local Python execution | AgentCore Browser / AgentCore Code Interpreter |

## Open Gaps To Fill (you complete)
- Final workshop use case/domain: [Actually one of the ideas is make the simplest financial, but I think about to make agent which can actually create and deploy lambda functions and the RAG will be not the Vector Db but MCP server to query the AWS docs. Actually we will not need to create those mcp servers as they already exist and could be reusable]
- Mock dataset type and source: [we can mock the python functions locally]
- Core tools in MVP (exact list): [MCP Servers: docs from AWS and Server to actually deploy the lambda function]
- Which AgentCore features are in-scope for workshop day 1-2: [Identity, Python, RunTime, Observation, actually all core features. WHY ARE U ASKING ME SUCH QUESTION, I DO NOT EVEN SUPPOSE TO KNOW THOSE FEATURES]
- Demo success criteria for final live run: [The lambda function succsessfully deployed, connected to GateWay and working]
