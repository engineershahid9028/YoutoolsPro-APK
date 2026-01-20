from fastapi import FastAPI
from app.database import Base,engine
from app.auth import router as auth_router
Base.metadata.create_all(bind=engine)
app=FastAPI(title='YouToolsPro Backend API')
app.include_router(auth_router)
@app.get('/')
def root(): return {'status':'running'}