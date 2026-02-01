"""
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH/QkWNMqBAXAVbjPNhoiXjjgV9gm+eublzZ0BKmKKln tvoya_poshta@gmail.com 


"""


from pydantic import BaseModel, Field
import random
from typing import List, Optional
import httpx
import asyncio

TOXIC_THRESHOLD = 0.9
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
  

def check_is_toxic():
  result= random.choice([0,1])
  
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

# Changed logic to categorize based on TOXIC_THRESHOLD constant
    for res in results:
      if res.is_toxic and res.score >= TOXIC_THRESHOLD:
        print(f"😡 CRITICAL TOXIC [{res.score}]:\t {res.text}")
      elif res.is_toxic:
        print(f"⚠️ SUSPICIOUS [{res.score}]:\t {res.text}")
      else:
        print(f"✅ CLEAN [{res.score}]:\t {res.text}")



if __name__ == "__main__":
  asyncio.run(main())