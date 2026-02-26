from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# import logfire
from app.routes import api_router

app = FastAPI(
    title="Rebecca API",
    description="API for Rebecca which lets patients and providers chat with medical records",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite local development
        "http://localhost:5174",  # Alternative Vite port
        "https://mymr-rebecca-frontend.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logfire.configure()
# logfire.instrument_fastapi(app)
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to the API of Rebecca"}


@app.get("/health")
async def health():
    return {"message": "Healthy...."}
