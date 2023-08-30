from io import BytesIO

from celery.result import AsyncResult
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from starlette import status
from starlette.responses import Response, StreamingResponse, JSONResponse, HTMLResponse

from cas_api.worker import cas_api_worker
from cas_shared.exceptions.cas_api_error import CasError, CasErrorCode
from cas_shared.schemas.analysis import (
    CustomersForAllCategoriesBaseAnalysis,
    CustomersForAllCategoriesAnalysis,
    GroupRegionallyAllCustomerAnalysis,
    CustomerReputationAnalysisValue
)
from cas_shared.schemas.product import FoundProduct
from cas_shared.schemas.task import CasPipelineComponent

router = APIRouter()


@router.get(
    "",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    description="Получить результат выполнения задачи.",
    summary="Get task result",
    responses={
        200: {
            "description": "Result of the assignment(s)",
            "content": {
                "application/json": {
                    "example": [
                        [CustomersForAllCategoriesBaseAnalysis.example()],
                        [CustomersForAllCategoriesAnalysis.example()],
                        [GroupRegionallyAllCustomerAnalysis.example()],
                        [CustomerReputationAnalysisValue.example()],
                        [CasPipelineComponent.example()],
                        [FoundProduct.example()]
                    ]
                },
                "text/html": {
                    "example": [
                        "html"
                    ]
                },
                "image/png": {
                    "example": [
                        "BytesIO"
                    ]
                }
            }
        }
    }
)
async def get_result(task_id: UUID4):
    res: AsyncResult = cas_api_worker.AsyncResult(str(task_id))
    if res is None:
        raise CasError(
            message="Task not found.",
            error_code=CasErrorCode.TASK_NOT_FOUND_ERROR,
            http_status_code=status.HTTP_404_NOT_FOUND
        )

    st = res.status
    match st:
        case "STARTED" | "PENDING":
            return Response(content=None, status_code=status.HTTP_202_ACCEPTED)
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
        return JSONResponse(content=jsonable_encoder(result))
    else:
        return HTMLResponse(content=result)
