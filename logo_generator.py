import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

async def generate_logo(prompt: str) -> str:
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return response['data'][0]['url']
    except Exception as e:
        return f"Ошибка при генерации логотипа: {e}"
