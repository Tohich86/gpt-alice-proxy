from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

@app.post("/gpt")
async def gpt_proxy(req: Request):
    try:
        data = await req.json()
        prompt = data.get("request", {}).get("original_utterance", "").strip()

        if not prompt:
            return {
                "response": {
                    "text": "Запрос не распознан. Пожалуйста, повторите.",
                    "end_session": False
                },
                "version": "1.0"
            }

        if not OPENAI_API_KEY:
            return {
                "response": {
                    "text": "Ошибка: API-ключ не задан. Проверь Render → Environment.",
                    "end_session": False
                },
                "version": "1.0"
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            api_response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
            )

        result = api_response.json()

        reply = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not reply:
            reply = "Ответ от GPT пустой или некорректный. Проверь prompt."

    except Exception as e:
        reply = f"Ошибка обработки запроса: {str(e)}"

    return {
        "response": {
            "text": reply,
            "end_session": False
        },
        "version": "1.0"
    }
