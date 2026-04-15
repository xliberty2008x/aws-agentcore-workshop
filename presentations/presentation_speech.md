# Повний спіч для презентації Amazon Bedrock AgentCore

**Загальна тривалість:** 30-40 хвилин
**Аудиторія:** Junior/Mid розробники
**Мова:** Українська з англійськими технічними термінами

---

## Слайд 1: Титульна сторінка

**[00:00 - 00:30]**

Доброго дня всім! Сьогодні ми поговоримо про Amazon Bedrock AgentCore - модульну платформу для AI агентів від AWS.

Це не просто черговий інструмент для роботи з LLM, а комплексне рішення для деплою production-ready агентів з enterprise-grade безпекою та масштабованістю.

Протягом наступних 30-40 хвилин ми розглянемо п'ять ключових компонентів платформи та зрозуміємо, чому AgentCore може значно спростити ваш шлях від локального прототипу до промислового рішення.

---

## Слайд 2: Що таке AgentCore?

**[00:30 - 02:00]**

Отже, що таке AgentCore?

AgentCore - це модульна agentic платформа, яка покриває повний життєвий цикл AI агента:

- Побудову - ви пишете логіку агента
- Розгортання - платформа деплоїть у production
- Управління та governance - централізований контроль безпеки та доступу

На слайді ви бачите офіційну діаграму від AWS, яка показує архітектуру платформи.

Три ключові характеристики, які відрізняють AgentCore:

**По-перше, Enterprise-grade безпека** - це рішення для корпоративних потреб з повним контролем доступу, аудитом, та шифруванням.

**По-друге, Framework-agnostic** - ви можете використовувати LangGraph, CrewAI, LlamaIndex, Strands, або написати власний фреймворк. AgentCore не нав'язує конкретний інструмент.

**По-третє, Model-agnostic** - Claude, Gemini, GPT-4, моделі з Bedrock - будь-яка LLM працює з платформою.

Це означає, що ви не прив'язані до екосистеми одного вендора і можете змінювати стек без переписування інфраструктурного коду.

---

## Слайд 3: 9 модульних сервісів

**[02:00 - 04:00]**

AgentCore складається з 9 незалежних модульних сервісів. Ви можете використовувати їх разом або вибірково, залежно від ваших потреб.

Швидко пройдемося по кожному:

**Runtime** - serverless середовище, де живе ваш агент. Ви не управляєте серверами, контейненами або Lambda functions вручну.

**Memory** - короткострокова та довгострокова пам'ять. Агент пам'ятає контекст розмови та user preferences між сесіями.

**Gateway** - перетворює зовнішні APIs та Lambda в MCP-compatible tools. Це unified interface для всіх інструментів вашого агента.

**Identity** - централізоване управління автентифікацією та авторизацією. Як inbound - хто може викликати агента, так і outbound - до яких ресурсів агент має доступ від імені користувача.

**Code Interpreter** - ізольоване виконання коду в sandbox середовищі. Агент може запускати Python для calculations або data analysis безпечно.

**Browser** - агент може взаємодіяти з веб-додатками, скрейпити сторінки, робити screenshots.

**Observability** - централізований моніторинг та трейсинг через OpenTelemetry. Ви бачите весь lifecycle агента - від reasoning до tool invocations.

**Evaluations** - оцінка якості відповідей агента за різними метриками.

**Policy** - контроль доступу. Ви описуєте rules у декларативному форматі.

Ключовий месседж - ці модулі працюють разом, але ви не зобов'язані використовувати всі. Можна почати з Runtime та Gateway, а потім додати Memory чи Observability за потреби.

---

## Слайд 4: Use Cases

**[04:00 - 05:30]**

Давайте подивимося на три основні категорії use cases для AgentCore.

**Автономні агенти** - найпопулярніший сценарій. Customer support bots, які можуть читати knowledge base, відповідати на питання, та ескалейтувати складні кейси. Workflow automation агенти для internal processes - наприклад, approval workflows для invoices або travel requests. Research assistants, які збирають інформацію з різних джерел та готують summaries.

**MCP сервери** - якщо у вас є APIs, які ви хочете зробити доступними для агентів через стандартизований протокол. Замість того щоб писати custom integration для кожного агента, ви створюєте один MCP server через Gateway, і всі агенти можуть його використовувати.

**Agent платформи** - якщо ви будуєте platform as a service для AI агентів. AgentCore надає централізований governance - ви контролюєте security policies, observability, та compliance в одному місці. Multi-tenant deployment з ізоляцією між різними командами або клієнтами. Enterprise security built-in.

Тепер перейдемо до детального розгляду кожного ключового компонента, починаючи з Runtime.

---

## Слайд 5: AgentCore Runtime - Overview

**[05:30 - 07:00]**

Runtime - це серце AgentCore. Secure, serverless середовище, спеціально створене для AI агентів.

На діаграмі ви бачите flow: developer пише код агента з будь-яким фреймворком та моделлю, додає простий decorator, запускає `configure` та `launch` - і ваш локальний код деплоїться у AWS.

Ключова перевага, яку я хочу підкреслити: **Локальний код стає production deployment за кілька рядків**.

Немає складних Dockerfile, Kubernetes manifests, Lambda configurations. Ви пишете звичайну Python функцію, обгортаєте її в `BedrockAgentCoreApp`, і платформа робить все інше - packaging, deployment, scaling, monitoring.

Це величезна різниця порівняно з традиційним підходом, де перехід від Jupyter notebook до production вимагає тижнів роботи DevOps team.

З Runtime ви фокусуєтеся на business logic агента, а не на інфраструктурі. Саме тому це називається "production-ready platform" - production перестає бути болючою частиною процесу.

Давайте подивимося детальніше на можливості Runtime.

---

## Слайд 6: Runtime - Ключові можливості (1/2)

**[07:00 - 09:00]**

Перша половина ключових можливостей Runtime. Я пройдуся по кожній.

**Framework Agnostic** - LangGraph, CrewAI, Strands, Custom frameworks - все працює. Платформа не нав'язує конкретний orchestration tool. Ваша команда використовує LangGraph? Чудово. Хтось інший пише custom state machine? Теж працює.

**Model Flexibility** - Claude від Anthropic, Gemini від Google, GPT-4 від OpenAI, моделі з Amazon Bedrock - будь-яка LLM. Ви не прив'язані до одного model provider. Можете A/B тестувати різні моделі або використовувати дешевшу модель для простих tasks, а потужнішу для складних.

**Protocol Support** - MCP (Model Context Protocol) та A2A (Agent-to-Agent communication). MCP для tool calling, A2A для multi-agent orchestration. Обидва протоколи підтримуються natively.

**Session Isolation** - кожна user session запускається в окремій microVM. Це означає повну ізоляцію на рівні CPU, memory, filesystem. Якщо у одного користувача агент падає або споживає багато ресурсів, це не впливає на інших користувачів.

**Extended Execution** - до 8 годин для асинхронних workloads. Це не типові 15 хвилин Lambda limit. Якщо ваш агент робить довгий research task або complex data processing, він може працювати години.

**Consumption Pricing** - ви платите тільки за фактичне використання, не за простой Якщо агент чекає на відповідь від external API, ви не платите за цей час. Це важливо для cost optimization.

---

## Слайд 7: Runtime - Ключові можливості (2/2)

**[09:00 - 10:30]**

Друга половина features, які роблять Runtime потужним.

**Built-in Auth** - інтеграція з Identity Providers. Cognito, Okta, Azure Entra ID - ви не пишете authentication layer з нуля. Підключаєте свій IdP, і Runtime автоматично валідує JWT tokens.

**Agent Observability** -  Це не просто application logs. Ви бачите, як агент "думає" - які reasoning steps він робить, які інструменти викликає, що отримує у відповідь. Це критично для debugging складних agentic workflows.

**100MB Payloads** - підтримка multimodal content. Ви можете передавати великі зображення, документи, відео. Це не обмеження в 6MB як у API Gateway. AgentCore створений для роботи з rich media.

**Bidirectional Streaming** - WebSocket для real-time взаємодії. User пише повідомлення, агент починає відповідати ще до того як закінчив reasoning. Це покращує user experience - користувач бачить progress, а не чекає 30 секунд на повну відповідь.

Всі ці features "працюють з коробки" - ви не конфігуруєте їх руками, вони частина платформи.

---

## Слайд 8: Runtime - Simple Integration

**[10:30 - 12:00]**

А тепер найважливіше - як це виглядає в коді?

На слайді ви бачите мінімальний приклад. **Три рядки коду для production deployment**.

```python
from bedrock_agentcore import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    return your_agent_logic(payload)

app.run()
```

Після цього ви запускаєте `agentcore configure` для setup AWS resources та `agentcore launch` для deployment. Платформа пакує ваш код, створює Docker image, деплоїть у Runtime, налаштовує networking, security, observability.

Тепер перейдемо до Identity - як контролювати хто має доступ до агента та до яких ресурсів агент має доступ.

---

## Слайд 9: AgentCore Identity - Overview

**[12:00 - 13:30]**

Identity - це комплексний сервіс для управління автентифікацією та авторизацією.

Фундаментальна проблема, яку він вирішує: **Безпечний доступ агентів до user-specific даних**.

Уявіть: ваш агент читає Google Docs користувача. Як забезпечити, що агент бачить тільки ті документи, до яких користувач має доступ? Не більше, не менше. Це non-trivial проблема.

AgentCore Identity базується на ключовому принципі: **Delegation, not Impersonation**.

Що це означає? Агент НЕ прикидається користувачем. Агент автентифікується як він сам (як окрема identity).

Це важливо для audit trails. Ви завжди знаєте: це агент викликав API, але від імені конкретного користувача. У logs ви бачите обидві identities.

На діаграмі показано flow: User викликає Agent, Agent має свою власну identity ("Who is this agent?"), але також несе user context для outbound calls до зовнішніх ресурсів.

Identity має два напрямки: Inbound та Outbound. Зараз розглянемо кожен детальніше.

---

## Слайд 10: Inbound Authentication

**[13:30 - 15:00]**

Inbound Authentication відповідає на два питання:

**"Who is this user?"** - хто викликає мого агента?

**"Is user allowed to call this agent?"** - чи має цей користувач permission викликати цього конкретного агента?

На діаграмі ви бачите повний flow:

1. User логіниться у вашу application через Identity Provider (наприклад, Cognito)
2. Application отримує JWT access token
3. Application викликає AgentCore Runtime з цим token у Authorization header
4. Runtime валідує token через JWKS (JSON Web Key Set)
5. Runtime перевіряє claims у token - issuer, expiration, audience
6. Runtime перевіряє `allowedClients` - чи є цей client_id у whitelist
7. Якщо все ok - invoke проходить, якщо ні - отримуєте 401 Unauthorized

Ключовий момент: ви не пишете цю логіку вручну. Ви просто конфігуруєте у AgentCore це можна робити як через код так і через UI

Платформа робить всю валідацію автоматично.

Підтримка різних IdP - Cognito, Okta, Azure Entra ID, Auth0, будь-який OIDC-compliant provider.

---

## Слайд 11: Outbound Authentication

**[15:00 - 16:30]**

Outbound Authentication - це коли агент викликає зовнішні ресурси.

Питання: **"Чи дозволено агенту викликати ресурси на правах юзера"**

Два основні типи:

**AWS Resources** - використовуємо IAM execution roles. Ваш агент має IAM role з permissions для доступу до S3, DynamoDB, або інших AWS сервісів. Це standard AWS security model.

**External Services** - Google, Salesforce, Stripe, будь-який third-party API. Тут використовуємо OAuth 2.0.

Два варіанти OAuth:

- **2-legged (client credentials)** - агент автентифікується як application. Доступ до ресурсів, які належать application, не конкретному user.
- **3-legged (authorization code)** - user дає explicit consent. Агент отримує user-scoped access token. Це той сценарій, який ми бачили в use case - агент читає Google Docs користувача.

На слайді ви бачите приклад use case: **Агент читає Google Docs користувача**.

Як це працює практично:

1. User викликає агента
2. Агент намагається прочитати Google Doc
3. Gateway перевіряє - чи є у нас OAuth token для цього user?
4. Якщо немає - повертає `authorization_url`
5. User відкриває цей URL у browser, логіниться в Google, дає consent
6. Google redirects back до AgentCore
7. AgentCore зберігає encrypted access token
8. Наступний виклик агента вже має доступ до Google Docs

Весь цей flow управляється платформою. Ви не пишете OAuth redirect logic, token refresh, secure storage.

---

## Слайд 13: Identity Benefits

**[17:30 - 18:30]**

Три ключові переваги AgentCore Identity.

**Zero Trust Security** - принцип least privilege. Кожен component має мінімально необхідні permissions. User має доступ тільки до тих агентів, які йому потрібні. Агент має доступ тільки до тих resources, які необхідні для виконання task. Немає "admin" users з доступом до всього.

**Cross-Platform** - працює не тільки з AWS. Ви можете інтегрувати з іншими clouds - GCP, Azure. Можете підключати on-premise resources.
**Audit Trails** - Кожен authentication attempt, кожен API call логується. Ви бачите who, when, what. Це критично для enterprise compliance requirements - SOC 2, HIPAA, GDPR. Ви можете показати auditors повний trail хто і коли мав доступ до sensitive data.

Тепер перейдемо до Memory - як зробити агента stateful.

---

## Слайд 14: AgentCore Memory - Overview

**[18:30 - 20:00]**

Memory вирішує фундаментальну проблему: AI агенти за замовчуванням stateless.

Кожен запит до LLM - це fresh start. Модель не пам'ятає попередню розмову, якщо ви не передаєте весь history у prompt. Це працює для simple use cases, але не масштабується.

AgentCore Memory - це сервіс для збереження контексту.

Два типи пам'яті:

**Short-term Memory** - turn-by-turn у межах однієї сесії. User каже: "Яка погода в Києві" Агент відповідає. User каже: "А завтра?" Агент розуміє, що "завтра" означає Київ, бо пам'ятає контекст.

Це зберігається в conversation history. Весь prompt + ланцюг відповідей для поточної сесії.

**Long-term Memory** - user preferences між сесіями. User каже: "Я полюбляю місця біля вікна" Агент зберігає це як fact. Через тиждень, коли user бронює наступний flight, агент automatically пропонує window seat, навіть якщо user не згадав про це.

Це не просто RAG over conversation history. Це intelligent extraction ключових facts, preferences, summaries.

Memory не просто зберігає - вона структурує інформацію так, щоб агент міг ефективно її використовувати.

---

## Слайд 16: Memory Use Cases

**[21:00 - 22:00]**

Чотири concrete use cases для Memory.

**Conversational agents** - customer support з historical context. User звертається вдруге з тією ж проблемою. Агент каже: "Я вже бачу що ви звертались раніше" Це сильно покращує досвід користувача.

**Task-oriented agents** - Invoice approval процес розтягується на кілька днів. User каже агенту: "Апрувни інвойс." Агент: "Зроблю" Через два дні user питає: "What's the status?" Агент: "Інвойс в черзі" Агент пам'ятає контекст task.

**Multi-agent systems** - shared memory для coordination. У вас є research agent та writing agent. Research agent збирає facts, пише їх у shared memory. Writing agent читає ці facts та пише article. Agents coordinate через memory, не через direct communication.

**Autonomous agents** - learning from past experiences. Агент робить помилку, ви даєте feedback. Агент зберігає це у long-term memory. Наступного разу агент не повторює цю помилку, бо "запам'ятав" lesson.

Memory - це те, що робить агента truly intelligent в довгостроковій перспективі.

---

## Слайд 17: AgentCore Gateway - Overview

**[22:00 - 23:30]**

Переходимо до Gateway - можливо найскладнішого, але дуже потужного компоненту.

Gateway вирішує проблему: як зробити зовнішні APIs доступними для агентів через unified interface?

У вас може бути 10 різних APIs - Google Docs, Slack, Stripe, internal REST APIs. Кожен має свою authentication, свій schema, свій error handling.

Без Gateway: ви пишете custom integration для кожного API у кожному агенті.

**З Gateway: ви перетворюєте всі ці APIs у MCP servers**. MCP - Model Context Protocol - це стандартизований протокол для tool calling.

Агент бачить unified interface. Замість "як викликати Google Docs API з OAuth?" агент просто каже: "listTools" - отримує список доступних tools. "invokeTool('read_google_doc', {doc_id: 'xxx'})" - викликає tool.

Gateway під капотом робить всю складну роботу:

- OAuth token management
- API schema transformation
- Error handling та retry logic
- Rate limiting
- Logging та monitoring


---

## Слайд 18: Gateway - Як працює

**[23:30 - 25:00]**

Gateway працює через концепцію **Gateway Target**.

Три типи targets:

**1. Lambda ARNs** - ви пишете custom Lambda function з будь-якою логікою. Gateway викликає цю Lambda як tool.

**2. API specifications** - Ви просто даєте Gateway API schema, і він автоматично генерує MCP tools. Наприклад, OpenAPI spec для Google Docs API → Gateway створює tool `read_document`, `list_documents`, etc. Без написання коду.

**3. MCP Transport** - Streamable HTTP. Якщо у вас вже є MCP server, Gateway може proxy calls до нього.


---

## Слайд 19: Gateway - Авторизація

**[25:00 - 26:00]**

Gateway також управляє authentication - як inbound, так і outbound.

**Inbound** - User → App → Agent → Gateway. OAuth token передається від user через agent до Gateway. Gateway валідує: чи має цей user доступ до цього Gateway? Чи дозволено викликати ці tools?


**Outbound** - Gateway → External resources. Gateway використовує credentials для виклику backend APIs.

Три типи credentials:

- **API Key** → REST endpoint. Просто статичний key.
- **IAM** → Lambda function. AWS signature.
- **OAuth token** → 3rd party services. Для Google, Salesforce, etc.

На діаграмі: Gateway викликає різні backends з різними auth mechanisms.

Gateway інтегрується з AgentCore Identity для централізованого управління credentials.

Observability через CloudTrail - кожен call логується. Ви бачите audit trail.

---

## Слайд 20: Gateway - Tool Discovery

**[26:00 - 27:30]**

Проблема масштабу: у production системі може бути сотні tools.

На слайді приклад: Target 1 має 250 tools, Target 2 має 100 tools, Target 3 має 10 tools. Total 360 tools.

**Without search**: агент викликає `listTools` → отримує всі 360 tools. LLM повинна обробити descriptions всіх 360 tools у prompt. Це:

- Дорого (tokens)
- Повільно (latency)
- Неефективно (LLM gublиться серед irrelevant tools)

**Using search**: агент каже `search("draft a new advertisement")` → Gateway робить semantic search через vector embeddings → повертає 4 most relevant tools.

Як це працює:

1. Коли ви створюєте Gateway Target, платформа automatically генерує embeddings для кожного tool description
2. Ці embeddings зберігаються у vector database
3. Коли агент робить search query, Gateway embedить query та шукає k-nearest neighbors
4. Повертає тільки relevant tools


---

## Слайд 21: Gateway Benefits

**[27:30 - 28:30]**

П'ять ключових переваг Gateway.

fully managed. Ви не deploy Gateway server, не менеджете скейлінг. AWS робить це за вас.

**Unified Interface** - MCP protocol для всіх tools. Агент не знає, що під капотом - Lambda, REST API, або gRPC service. Для агента все виглядає як MCP tools.

**Built-in Auth** - OAuth lifecycle management. Gateway зберігає token securely, автоматично refresh коли expired, handle revocation. Ви не пишете цю логіку.

**Auto Scaling** - no capacity planning. 10 requests per second або 10,000 requests per second - Gateway scales automatically.

**Enterprise Security** - encryption,  Audit logging. Access controls через IAM policies. Built-in security best practices.

Gateway - це те, що дозволяє швидко додавати нові integrations без переписування infrastructure code кожного разу.

---

## Слайд 23: Наступний воркшоп

**[30:00 - 32:00]**

Дякую за увагу!

Ми розглянули фундаментальні концепції AgentCore - Runtime, Identity, Memory, та Gateway.

Але теорія - це тільки початок. **Наступний воркшоп буде повністю практичним**.

Ми будемо hands-on будувати реальний AI агент:

**По-перше**, створимо локального ReAct агента з LangGraph - це той самий агент, про який ми говорили. Він буде розмовляти, reasoning робити, tools викликати. Протестуємо його локально.

**По-друге**, деплоїмо цей агент у AgentCore рядків там буде значно більше ніж 3 адже ноутбук е2е і довелось покрити багато edge кейсів. Локальний код стане production service.

**По-третє**, підключимо OAuth авторизацію - трьохстороння авторизація з Google. User дає consent, агент отримує доступ до Google Docs конкретного користувача.

**По-четверте**, інтеграція з Gateway - агент буде читати реальні Google Docs, робити RAG over documents, відповідати на питання на основі контенту.

**І нарешті**, додамо persistence - session management, щоб агент пам'ятав контекст між викликами.

Повний цикл від нуля до production-ready агента за один воркшоп.

Це буде jupyter notebook з покроковими інструкціями - ви зможете запускати кожну комірку, бачити результати, експериментувати.

До зустрічі на наступному воркшопі! 🚀

