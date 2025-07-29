import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

async def generate_text(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Ошибка при генерации текста: {e}"
