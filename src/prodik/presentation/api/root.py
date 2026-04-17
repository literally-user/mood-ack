from fastapi import APIRouter, status

router = APIRouter(tags=["root"])


@router.get("/ping")
async def ping() -> dict[str, int]:
    return {"status": status.HTTP_200_OK}
