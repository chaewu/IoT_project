from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv('.env')

client = OpenAI(
    api_key=os.getenv('OPEN_API_KEY')
)

model = "gpt-3.5-turbo"
query = "hi"

completion = client.chat.completions.create(
  model=model,
  messages=[
    {"role": "system", "content": "You are an AI model that answers any question in Korean."},
    {"role": "user", "content": query}
  ]
)

print(completion.choices[0].message.content)
