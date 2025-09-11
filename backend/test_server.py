from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "test successful"}

@app.get("/health")
async def health():
    return {"status": "ok"}