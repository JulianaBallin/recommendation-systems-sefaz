from fastapi import FastAPI
from backend.api.rotas_usuarios import router as usuarios_router
from backend.api.rotas_nfs import router as nfs_router

app = FastAPI()

app.include_router(usuarios_router)
app.include_router(nfs_router)
