import uvicorn
from fastapi import FastAPI

from features.brak.router import router as brak_router
from features.tree.router import router as tree_router

print("initial program...")
app = FastAPI(
    title="FamilyTree API",
    summary="API for build nodes from user_id and send image with family tree",
)
app.include_router(brak_router)
app.include_router(tree_router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


uvicorn.run(app, host="localhost", port=8001)
