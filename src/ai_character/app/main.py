from fastapi import FastAPI
from app.api import router as characters_router
from contextlib import asynccontextmanager
from app.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    yield


app = FastAPI(title="Chat WebSocket Service", version="1.0.0", lifespan=lifespan)

app.include_router(characters_router, prefix="/api", tags=["AI Characters"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
