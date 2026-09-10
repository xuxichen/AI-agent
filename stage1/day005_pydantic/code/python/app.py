from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class ItemIn(BaseModel):
    name: str = Field(min_length=2)
    price: int = Field(ge=0)


class ItemOut(BaseModel):
    id: int
    name: str
    price: int


items = [
    {"id": 1, "name": "pen", "price": 3},
    {"id": 2, "name": "cap", "price": 5},
    {"id": 3, "name": "box", "price": 10},
]


@app.get("/")
def read_root():
    return {"service": "day005", "count": len(items)}


@app.get("/items/{item_id}", response_model=ItemOut)
def read_item(item_id: int):
    for it in items:
        if it["id"] == item_id:
            return it
    return {"error": "没有这个 id", "item_id": item_id}


@app.get("/items", response_model=list[ItemOut])
def list_items(min_price: int = 0):
    found = []
    for it in items:
        if it["price"] >= min_price:
            found.append(it)
    return found


@app.post("/items", response_model=ItemOut)
def create_item(payload: ItemIn):
    data = payload.model_dump()
    data["id"] = len(items) + 1
    items.append(data)
    return data
