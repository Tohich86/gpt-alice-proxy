from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

TRIGGER_PHRASES = {
    "спроси gpt", "спроси гпт", "запусти чат", "запусти gpt",
    "командный центр", "алиса, gpt", "алиса, командный центр"
}
EXIT_PHRASES = {"пока", "до свидания", "выход", "завершить"}

SYSTEM_PROMPT = (
    "Вы — полезный ассистент Алисы. Отвечайте на вопросы по-русски "
    "коротко и понятно, без лишних слов."
)

def alice_response(text: str, end_session: bool = False):
    return {
        "response": {
            "text": text,
            "end_session": end_session
        },
        "version": "1.0"
    }

@app.post("/gpt")
async def gpt_proxy(req: Request):
    try:
        data = await req.json()
        print("Входящие данные:", data)

        prompt = data.get("request", {}).get("original_utterance", "").strip()
        lower = prompt.lower()

        if not prompt or lower in TRIGGER_PHRASES:
            return alice_response("Скажите, что вы хотите узнать у GPT.")

        if lower in EXIT_PHRASES:
            return alice_response("До новых встреч!", end_session=True)

        if not OPENAI_API_KEY:
            print("Ошибка: Нет ключа API")
            return alice_response("Ошибка: API-ключ не задан. Проверьте Render Environment.")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            )

        print("OpenAI ответ статус:", resp.status_code)
        print("OpenAI ответ тело:", resp.text)

        if resp.status_code != 200:
            return alice_response(
                f"Ошибка OpenAI {resp.status_code}: {resp.text[:100]}"
            )

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            return alice_response("Ответ от GPT пустой или некорректный. Проверь prompt.")

        reply = choices[0].get("message", {}).get("content", "").strip()
        if not reply:
            return alice_response("Ответ от GPT пустой или некорректный. Проверь prompt.")

        return alice_response(reply)

    except Exception as e:
        print("Ошибка сервера:", e)
        return alice_response(f"Серверная ошибка: {e}")
