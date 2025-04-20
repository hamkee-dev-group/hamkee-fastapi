from api.routes.hello import hello_router
from fastapi import APIRouter


_PREFIX_V1 = "/v1"


router = APIRouter()
router.include_router(hello_router, tags=["hello"], prefix=_PREFIX_V1)
