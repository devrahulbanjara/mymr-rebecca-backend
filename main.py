from fastapi import FastAPI

from app.routes import api_router

app = FastAPI(
    title="MyMR-AI API",
    description="API for MyMR-AI which lets patients and providers chat with medical records",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the API of MyMR-AI"}


@app.get("/health")
async def health():
    return {"message": "Healthy...."}
