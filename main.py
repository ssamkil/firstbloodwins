from fastapi import FastAPI
from routes import router

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})

app.include_router(router)

@app.get('/')
async def index():
    return {'MESSAGE': 'Welcome to First Blood Kills Official'}