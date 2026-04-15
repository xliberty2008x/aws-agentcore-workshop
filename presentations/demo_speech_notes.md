# Нотатки Для Демо Ноутбука

Використовуй цей файл як короткий live-demo script для `output/jupyter-notebook/workshop_google_docs_rag_e2e_demo.ipynb`.

## Cell 3: Bootstrap і конфігурація
Тут ми знаходимо корінь проєкту і підключаємо `WorkshopE2EDemo`, щоб ноутбук працював із реальним репозиторієм, а не з прихованим локальним станом. Одразу показуємо AWS profile, region, OAuth return URL і назви ресурсів, щоб аудиторія бачила, в якому середовищі ми запускаємо демо.

## Cell 5: AWS caller identity
Ця клітинка підтверджує, що ноутбук працює з правильним AWS identity і правильним регіоном перед створенням будь-яких ресурсів. Це швидка перевірка на початку демо: якщо тут щось не так, далі йти не треба.

## Cell 8: Step 1, Inbound auth через Cognito
Тут ми робимо inbound auth видимим: спочатку показуємо сам запит, тобто user pool, app client і demo user. Потім показуємо реальний результат із AWS, де видно Cognito IDs і access token, який далі використовується як JWT для Gateway і Runtime.

## Cell 11: Step 2A, Google OAuth provider
У цій клітинці ми реєструємо Google як outbound OAuth provider всередині AgentCore Identity. Найважливіший результат тут це `callback_url`, бо саме його треба додати в Google OAuth client redirect URIs.

## Cell 13: Step 2B, Gateway
Тут ми створюємо AgentCore Gateway з MCP і custom JWT authorizer на базі Cognito discovery URL. На виході отримуємо gateway URL і бачимо, що gateway дійшов до стану `READY`.

## Cell 15: Step 2C, Google Docs target і smoke test
У цій клітинці ми підключаємо до gateway Google Docs OpenAPI target і прив’язуємо його до Google OAuth provider. Одразу після цього запускаємо smoke test, щоб показати, що outbound OAuth path живий і gateway вміє повернути authorization challenge.

## Cell 18: Step 3, локальний ReAct агент
Перед AWS runtime ми показуємо той самий агентний патерн локально, але з mock tool і локальним checkpointer. Це дає зрозумілу базову модель того, як агент думає і викликає tools, без додаткової cloud-складності.

## Cell 19: Step 3, invoke локального агента
Тут ми відправляємо реальний локальний prompt і друкуємо повну траєкторію, включно з tool calls і повідомленнями агента. Сенс цієї клітинки в тому, щоб показати ReAct loop ще до переходу в задеплоєний runtime.

## Cell 22: Step 4, deploy runtime
У цьому кроці ми пакуємо runtime, показуємо deployment inputs і деплоїмо застосунок в AgentCore Runtime. Важливість у тому, що на виході ми бачимо справжній runtime ARN, role і artifact path, а не абстрактну схему на словах.

## Cell 25: Step 5A, перший runtime invoke і callback server
Спочатку ми підіймаємо локальний callback server для OAuth redirect, а потім показуємо точний runtime payload, який відправляємо. Перший invoke зазвичай повертає consent challenge, і це добре для демо, бо outbound OAuth стає видимою частиною флоу, а не прихованою магією.

## Cell 26: ручний consent крок
Якщо consent ще не виданий, у цей момент треба відкрити `authorization_url` і завершити Google login flow. Для аудиторії головна ідея тут така: runtime коректно зупинився на очікуванні user consent і продовжить роботу після callback на localhost.

## Cell 28: Step 5B, завершення consent і другий invoke
Після consent ми завершуємо OAuth session в AgentCore і формуємо другий runtime payload. Фінальний результат тут є головним доказом всього демо: агент повертає детерміновану відповідь із sources і tool trace, тобто Runtime, Identity, Gateway, Google OAuth і Google Docs реально відпрацювали end-to-end.

## Cell 31: Step 6, cleanup
Ця клітинка спеціально залишена закоментованою, бо під час live demo зазвичай краще не видаляти середовище одразу. Якщо буде потрібно, її можна розкоментувати пізніше і показати, що cleanup теж є частиною production-ready flow, а не забутою частиною воркшопу.
