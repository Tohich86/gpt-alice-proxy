from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.post("/gpt")
async def gpt_proxy(req: Request):
    data = await req.json()
    prompt = data.get("request", {}).get("original_utterance", "")
    response_text = f"Вы сказали: {prompt}. Это ответ от GPT-заглушки."
    return {
        "response": {
            "text": response_text,
            "end_session": False
        },
        "version": "1.0"
    }