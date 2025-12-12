import uvicorn
from fastapi import FastAPI
from app.routers import org_router, auth_router
from app.db import ensure_master_indexes

app = FastAPI(title='Organization Management Service')

app.include_router(org_router.router)
app.include_router(auth_router.router)

@app.on_event('startup')
async def startup_event():
    await ensure_master_indexes()

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)