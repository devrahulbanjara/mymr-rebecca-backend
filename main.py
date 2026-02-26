from fastapi import FastAPI
# import logfire
from app.routes import api_router

app = FastAPI(
    title="Rebecca API",
    description="API for Rebecca which lets patients and providers chat with medical records",
    version="1.0.0",
)

# logfire.configure()
# logfire.instrument_fastapi(app)
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the API of Rebecca"}


@app.get("/health")
async def health():
    return {"message": "Healthy...."}
