from fastapi import FastAPI

app = FastAPI()

items = [
    {"id": 1, "name": "pen", "price": 3},
    {"id": 2, "name": "cap", "price": 5},
    {"id": 3, "name": "box", "price": 10},
]


@app.get("/")
def read_root():
    return {"service": "day004", "count": len(items)}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    for it in items:
        if it["id"] == item_id:
            return it
    return {"error": "没有这个 id", "item_id": item_id}


@app.get("/items")
def list_items(min_price: int = 0):
    found = []
    for it in items:
        if it["price"] >= min_price:
            found.append(it)
    return {"count": len(found), "items": found}


@app.post("/items")
def create_item(payload: dict):
    items.append(payload)
    return {"count": len(items)}
