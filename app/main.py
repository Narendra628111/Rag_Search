from fastapi import FastAPI
from app.api import routes_rag, routes_ingest

app = FastAPI()

app.include_router(routes_ingest.router, prefix="/api")
app.include_router(routes_rag.router, prefix="/api")