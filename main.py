from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"  # конкретно запрошенная модель

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

            # Проверка на ошибки от OpenAI
            if "choices" in result:
                reply = result["choices"][0]["message"]["content"]
            elif "error" in result:
                reply = f"OpenAI error: {result['error'].get('message', 'Неизвестная ошибка')}"
            else:
                reply = f"Непредвиденный ответ: {result}"

    except Exception as e:
        reply = f"Ошибка обращения к GPT: {str(e)}"

    return {
        "response": {
            "text": reply.strip(),
            "end_session": False
        },
        "version": "1.0"
    }
