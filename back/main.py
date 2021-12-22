from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    payload: str

from redactor import Redactor

redactor = Redactor('yo.dat')

app = FastAPI()

@app.get("/")
def read_root():
    return {"response": "ok"}

@app.post("/app")
async def predict(item: Item):
    item.payload = redactor.run(item.payload)
    return item
