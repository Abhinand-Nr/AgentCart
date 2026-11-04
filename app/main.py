from app.handlers import register_handlers
from app.routers import auth, cart, orders, products
from fastapi import FastAPI

app = FastAPI(title="AgentCart")
register_handlers(app)

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(auth.router)
app.include_router(orders.router)

@app.get("/api/hello")
def hello() -> dict:
    return {"message": "hello from AgentCart"}

@app.get("/api/square/{n}")
def square(n: int) -> dict:
    return {"n": n, "square": n * n}