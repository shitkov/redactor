from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    payload: str

from redactor import Redactor

redactor = Redactor(
    yo_dict_path = 'yo.dat',
    abb_dict_path = 'abbreviation.json',
    all_abb_list_path = 'all_abb_list.txt',
    bad_abb_list_path = 'bad_abb_list.txt',
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"response": "ok"}

@app.post("/app")
async def predict(item: Item):
    item.payload = redactor.run(item.payload)
    return item