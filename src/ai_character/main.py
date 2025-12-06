from fastapi import FastAPI
from routers import router as characters_router
from db import Base, engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    yield


app = FastAPI(title="Chat WebSocket Service", version="1.0.0", lifespan=lifespan)

# Routers
app.include_router(characters_router, prefix="/api", tags=["AI Characters"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
