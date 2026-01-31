from pydantic import BaseModel, Field
import random
from typing import List, Optional
import httpx
import asyncio

# Вхідні дані
COMMENTS = [
    "Python is the best language!",
    "I hate errors, they are stupid.",
    "Asyncio makes me happy.",
    "This code is garbage.",
    "Have a nice day!",
    "You are a bad coder."
]

class ModerationResult(BaseModel):
  text : str
  is_toxic: bool
  score: float = Field(ge = 0.0, le =1.0)
  """
  pydantic Field - це спосіб додати додаткові обмеження або метадані до полів моделі.
                   У цьому випадку ми використовуємо його, щоб вказати, що score має бути в діапазоні від 0.0 до 1.0 включно.
  
  """

async def check_text(client: httpx.AsyncClient, text: str, index: int)-> ModerationResult:
  toxic_scale: float = scale_toxic()
  is_toxic:bool = check_is_toxic()
  try:
    print(f"Message {index} sended\n")
    response = await client.post(url= "https://httpbin.org/post", json ={"content": text}, timeout = 30.0)
    print(f"Message {index} recieved\n")

    response.raise_for_status()
    data = response.json()

    return ModerationResult(text = data["json"]["content"],  is_toxic=is_toxic, score=toxic_scale)


  except httpx.HTTPStatusError as e:
    print(f"\nError : {e.response.status_code}\n{e.response.text}")
    

def scale_toxic():
  return round(random.uniform(0,1), 1)
  """
  random.uniform(a, b) --> це функція з модуля random, яка повертає випадкове число з плаваючою комою в діапазоні від a до b.
  """

def check_is_toxic():
  result= random.choice([0,1])
  """
  random.choice(sequence) --> це функція з модуля random, яка вибирає випадковий елемент із непорожньої послідовності (наприклад, список або кортеж).
  """
  if result == 1:
    return True
  else:
   return False 
  

async def main():
  async with httpx.AsyncClient() as client: 
    tasks =[]
    for comment in COMMENTS:
      task = check_text(client=client, text=comment, index = COMMENTS.index(comment)+1)
      tasks.append(task)

    results: List[Optional[ModerationResult]] =  await asyncio.gather(*tasks)

    for res in results:
      print(f"Message: {res.text} \t| Toxic: {res.is_toxic}\t| Score: {res.score}\n")



if __name__ == "__main__":
  asyncio.run(main())