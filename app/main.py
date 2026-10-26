from app.routers import products
from fastapi import FastAPI

app = FastAPI(title="AgentCart")

app.include_router(products.router)

@app.get("/api/hello")
def hello() -> dict:
    return {"message": "hello from AgentCart"}

@app.get("/api/square/{n}")
def square(n: int) -> dict:
    return {"n": n, "square": n * n}