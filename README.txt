
=== Установка через https://render.com ===

1. Создай аккаунт на https://render.com (бесплатно)
2. Создай новый Web Service → Upload ZIP → Выбери этот архив
3. Укажи:
   - Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
   - Python Version: 3.10+
4. После запуска получишь ссылку типа:
   https://your-service-name.onrender.com/gpt

5. Эту ссылку вставь в "Webhook URL" в Яндекс.Диалоге.

Готово. Алиса будет передавать фразы, а сервер — отвечать через GPT.

(В этой версии используется заглушка. Настоящее подключение GPT будет встроено при следующем шаге.)
