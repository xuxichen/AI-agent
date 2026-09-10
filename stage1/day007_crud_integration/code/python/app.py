import json
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()


class ItemIn(BaseModel):
    name: str = Field(min_length=2)
    price: int = Field(ge=0)


class ItemOut(BaseModel):
    id: int
    name: str
    price: int


DB_FILE = "items.json"


def save():
    with open(DB_FILE, "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


try:
    with open(DB_FILE) as f:
        items = json.load(f)
except FileNotFoundError:
    items = [
        {"id": 1, "name": "pen", "price": 3},
        {"id": 2, "name": "cap", "price": 5},
        {"id": 3, "name": "box", "price": 10},
    ]
    save()


def find_biggest():
    biggest = 0
    for it in items:
        if it["id"] > biggest:
            biggest = it["id"]
    return biggest


def pagination(page: int = 1, size: int = 2):
    if size > 10:
        raise HTTPException(status_code=400, detail="size 最大 10")
    return {"page": page, "size": size, "skip": (page - 1) * size}


@app.middleware("http")
async def log_it(request: Request, call_next):
    start = time.perf_counter()
    print("[请求]", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception as err:
        print("[崩了]", type(err).__name__, "用了", round(time.perf_counter() - start, 4))
        raise
    cost = time.perf_counter() - start
    print("[响应] 状态", response.status_code, "用了", round(cost, 4))
    response.headers["X-Process-Time"] = str(round(cost, 4))
    return response


@app.exception_handler(HTTPException)
def on_http(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail},
    )


@app.exception_handler(Exception)
def on_other(request: Request, exc: Exception):
    print("[兜底]", type(exc).__name__)
    return JSONResponse(status_code=500, content={"code": 500, "msg": "服务器内部错误"})


@app.get("/")
def read_root():
    return {"service": "day007", "count": len(items)}


@app.get("/items/{item_id}", response_model=ItemOut)
def read_item(item_id: int):
    for it in items:
        if it["id"] == item_id:
            return it
    raise HTTPException(status_code=404, detail="没有这个 id")


@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemIn):
    for it in items:
        if it["id"] == item_id:
            it["name"] = payload.name
            it["price"] = payload.price
            save()
            return it
    raise HTTPException(status_code=404, detail="没有这个 id")


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    n = 0
    for it in items:
        if it["id"] == item_id:
            items.pop(n)
            save()
            return None
        n = n + 1
    raise HTTPException(status_code=404, detail="没有这个 id")


@app.get("/items", response_model=list[ItemOut])
def list_items(min_price: int = 0, pg=Depends(pagination)):
    found = []
    n = 0
    for it in items:
        if it["price"] >= min_price:
            if n >= pg["skip"]:
                if len(found) < pg["size"]:
                    found.append(it)
            n = n + 1
    return found


@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn):
    data = payload.model_dump()
    data["id"] = find_biggest() + 1
    items.append(data)
    save()
    return data
