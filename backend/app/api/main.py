from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import user_routes

app = FastAPI()

class LifespanManager:
    async def __aenter__(self):
        init_db()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    lifespan_manager = LifespanManager()
    await lifespan_manager.__aenter__()
    try:
        yield
    finally:
        await lifespan_manager.__aexit__(None, None, None)

app.router.lifespan_context = app_lifespan

app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {"Jeeeeee": "Parrrrrrk"}
