from fastapi import APIRouter
from fastapi.responses import JSONResponse


hello_router = APIRouter()


@hello_router.get("/hello/", name="hello:greet")
async def new():
    return JSONResponse(content={"message": "Hello World"})
