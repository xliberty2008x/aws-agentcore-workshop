# AWS AgentCore Workshop

Практичний репозиторій воркшопу з фокусом на E2E сценарій:
- AgentCore Runtime
- Inbound Auth (Cognito JWT)
- Gateway + OAuth outbound
- Tool calling + Observability

## Швидкий старт
1. Demo notebook для презентації: `output/jupyter-notebook/workshop_google_docs_rag_e2e_demo.ipynb`
2. Повний workshop notebook: `workshop_google_docs_rag_e2e.ipynb`
3. Runtime код для деплою: `runtime_app_agentcore_full.py`
4. Домашнє завдання: `HW_ASSIGNMENT.md`

## Test Document
Для 1-в-1 повторення воркшопу використовуйте цей Google Doc:
- [Workshop test document](https://docs.google.com/document/d/1vggeCZ61QagUCnDb4UL1DxUU0JdAQFUl_4ONtGPcHyg/edit?usp=sharing)

Що зробити:
- Відкрити документ і зробити `Make a copy`.
- Вказати `GOOGLE_DOC_ID` у `.env` як id вашої копії.
- Переконатися, що Google-акаунт, яким ви проходите consent, має доступ до цієї копії.

## Структура проєкту
- `output/jupyter-notebook/workshop_google_docs_rag_e2e_demo.ipynb` — короткий demo notebook для screen-share.
- `workshop_google_docs_rag_e2e.ipynb` — повний E2E notebook.
- `runtime_app_agentcore_full.py` — runtime app для AgentCore deploy.
- `workshop_helpers/` — helper-модулі для demo flow, deploy, invoke і consent orchestration.
- `HW_ASSIGNMENT.md` — домашнє завдання та чекліст для ментора.
- `docs/` — теорія, шпаргалки та додаткові інструкції.
- `presentations/` — презентації та супутні матеріали.
- `archive/` — legacy/історичні артефакти, винесені з основного потоку.

## Docs
- [Агентський кодінг (MCP setup)](docs/агентський%20кодінг.md)
- [Workshop cheatsheet](docs/workshop-cheatsheet.md)
- [Google OAuth setup for E2E](docs/google-oauth-setup-for-e2e.md)

## Примітки
- Локальні секрети/сесії винесені в `.env`, `.gateway_auth.env` та інші локальні файли (ігноруються через `.gitignore`).
- Runtime/build артефакти (`tmp/`, `__pycache__/`) прибираються з робочого дерева як тимчасові.
- Локальний state/секрети для AgentCore CLI та runtime (наприклад `.bedrock_agentcore*`, identity env/json, `vertex-credentials.json`) винесені в `local/` і не трекаються git.
