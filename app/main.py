from fastapi import FastAPI

app = FastAPI(title="AgentCart")

@app.get("/api/hello")
def hello() -> dict:
    return {"message": "hello from AgentCart"}