# uvicorn main:app --reload
from fastapi import FastAPI
from pydantic import BaseModel

from redactor import Redactor

import sys
sys.path.append('../')

class Item(BaseModel):
    payload: str

app = FastAPI()

redactor = Redactor('../data/yo.dat')

@app.post("/app")
async def predict(item: Item):
    item.payload = redactor.run(item.payload)
    return item
