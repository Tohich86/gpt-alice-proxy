from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

# Фразы, при которых мы не шлём запрос в OpenAI
TRIGGER_PHRASES = {
    "спроси gpt", "спроси гпт", "запусти чат", "запусти gpt",
    "командный центр", "алиса, gpt", "алиса, командный центр"
}
# Фразы выхода
EXIT_PHRASES = {"пока", "до свидания", "выход", "завершить"}

SYSTEM_PROMPT = (
    "Вы — полезный ассистент Алисы. Отвечайте на вопросы по-русски "
    "коротко и понятно, без лишних слов."
)

@app.post("/gpt")
async def gpt_proxy(req: Request):
    try:
        data = await req.json()
        prompt = data.get("request", {}) \
                     .get("original_utterance", "") \
                     .strip()
        lower = prompt.lower()

        print("Получен запрос:", repr(prompt))

        # Если фраза — просто триггер или пустая
        if not prompt or lower in TRIGGER_PHRASES:
            return alice_response("Скажите, что вы хотите узнать у GPT.")

        # Если пользователь хочет выйти — закрываем сессию
        if lower in EXIT_PHRASES:
            return {
                "response": {
                    "text": "До новых встреч!",
                    "end_session": True
                },
                "version": "1.0"
            }

        # Проверка ключа
        if not OPENAI_API_KEY:
            return alice_response(
                "Ошибка: API-ключ не задан. "
                "Проверьте переменные окружения Render → Environment."
            )

        # Отправляем запрос в OpenAI
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system",  "content": SYSTEM_PROMPT},
                        {"role": "user",    "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            )

        # Проверяем статус
        if resp.status_code != 200:
            print("OpenAI error:", resp.status_code, resp.text)
            return alice_response(
                f"Ошибка от OpenAI: {resp.status_code}. Попробуйте позже."
            )

        data = resp.json()
        choice = data.get("choices", [])
        if not choice:
            print("OpenAI вернул пустой choices:", data)
            return alice_response(
                "Ответ от GPT пустой или некорректный. Попробуйте переформулировать."
            )

        reply = choice[0] \
            .get("message", {}) \
            .get("content", "") \
            .strip()

        if not reply:
            print("OpenAI вернул пустой content:", data)
            return alice_response(
                "Ответ от GPT пустой или некорректный. Попробуйте по-другому."
            )

    except httpx.RequestError as e:
        print("HTTPX RequestError:", e)
        reply = "Сетевой сбой при обращении к GPT. Попробуйте позже."
    except Exception as e:
        print("Общая ошибка:", e)
        reply = f"Произошла ошибка: {e}"

    return alice_response(reply)


def alice_response(text: str, end_session: bool = False):
    """Упаковка под формат Алисы."""
    return {
        "response": {
            "text": text,
            "end_session": end_session
        },
        "version": "1.0"
    }
