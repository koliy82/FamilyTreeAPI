import uvicorn
from fastapi import FastAPI

from app.config import SERVER_PORT, SERVER_HOST
from app.features.brak.router import router as brak_router
from app.features.tree.router import router as tree_router
from app.features.user.router import router as user_router

app = FastAPI(
    title="FamilyTree API",
    summary="API for build nodes from user_id and send image with family tree",
)


@app.get("/status")
def get_status():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "routes": [
            {"method": "GET", "path": "/openapi.json", "summary": "Openapi"},
            {"method": "GET", "path": "/status", "summary": "App status"},
            {"method": "GET", "path": "/docs", "summary": "Swagger"},
        ]
    }


app.include_router(user_router)
app.include_router(brak_router)
app.include_router(tree_router)

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
