from io import BytesIO

from celery.result import AsyncResult
from fastapi import APIRouter
from pydantic import UUID4
from starlette import status
from starlette.responses import Response, StreamingResponse, JSONResponse, HTMLResponse

from cas_shared.exceptions.cas_api_error import CasError, CasErrorCode
from cas_worker.worker import cas_worker

router = APIRouter()


@router.get(
    "/",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Получить результат выполнения задачи.",
    summary="Get task result"
)
async def get_result(task_id: UUID4):
    res: AsyncResult = cas_worker.AsyncResult(str(task_id))
    if res is None:
        raise CasError(
            message="Task not found.",
            error_code=CasErrorCode.TASK_NOT_FOUND_ERROR,
            http_status_code=status.HTTP_404_NOT_FOUND
        )

    st = res.status
    match st:
        case "STARTED":
            return Response(content=None, status_code=status.HTTP_202_ACCEPTED)
        case "PENDING":
            raise CasError(
                message="Task not found.",
                error_code=CasErrorCode.TASK_NOT_FOUND_ERROR,
                http_status_code=status.HTTP_404_NOT_FOUND
            )
        case "RETRY":
            raise CasError(message="The task is to be retried, possibly because of failure.",
                           error_code=CasErrorCode.TASK_RETRY_ERROR,
                           http_status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        case "FAILURE":
            raise CasError(message="The task raised an exception, or has exceeded the retry limit.",
                           error_code=CasErrorCode.TASK_FAILURE_ERROR,
                           http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    result = res.result
    if isinstance(result, BytesIO):
        return StreamingResponse(content=result, media_type="image/png")
    elif isinstance(result, list):
        return JSONResponse(content=result)
    else:
        return HTMLResponse(content=result)
