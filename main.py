from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"  # или gpt-3.5-turbo, если хочешь быстрее и дешевле

@app.post("/gpt")
async def gpt_proxy(req: Request):
    data = await req.json()
    prompt = data.get("request", {}).get("original_utterance", "")

    if not prompt:
        return {
            "response": {
                "text": "Запрос не распознан. Пожалуйста, повторите.",
                "end_session": False
            },
            "version": "1.0"
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
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
            result = response.json()
            reply = result["choices"][0]["message"]["content"]

    except Exception as e:
        reply = f"Ошибка получения ответа от GPT: {str(e)}"

    return {
        "response": {
            "text": reply.strip(),
            "end_session": False
        },
        "version": "1.0"
    }
