from typing import Annotated

from fastapi import APIRouter, Query

from cas_api.worker import cas_api_worker
from cas_shared.schemas.task import CasTask
from config import WorkerTasks

router = APIRouter()


@router.get(
    "/search",
    response_model=CasTask,
    description="Выполнить поиск продукта для анализа.",
    summary="Search products"
)
async def products_search(
        search_input: Annotated[str, Query(
            description="Поисковый ввод",
            min_length=1,
            max_length=100)] = "ЧелГу",
        max_count_items: Annotated[int, Query(
            description="Максимальное количество получаемых совпадений",
            ge=3,
            le=100)] = 5):
    task = cas_api_worker.send_task(WorkerTasks.products_search, args=[search_input, max_count_items])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/products_data",
    response_model=CasTask,
    description="Выполнение скрапинга всех данных необходимых для анализа по продукту."
                "(данные продукта, данные всех ревьеров и комментаторов, ревью, комментарии)",
    summary="Product data collection"
)
async def products_data(
        product_name_id: Annotated[str, Query(
            description="Идентифицирующее имя продукта",
            min_length=1,
            max_length=100)] = "chelyabinskiy_gosudarstvenniy_universitet_russia_chelyabinsk"):
    task = cas_api_worker.send_task(WorkerTasks.products_data, args=[product_name_id])
    return CasTask(task_id=task.id, task_status=task.status)


@router.get(
    "/category_data",
    response_model=CasTask,
    description="Выполнение скрапинга всех данных необходимых для анализа всех продуктов в категории."
                "(данные продуктов, данные всех ревьеров и комментаторов, ревью, комментарии)",
    summary="Category data collection"
)
async def category_data(
        href_product_path: Annotated[str, Query(
            description="Идентифицирующий путь категории",
            min_length=1,
            max_length=200)] = "/in_town/education_companies/"):
    task = cas_api_worker.send_task(WorkerTasks.category_data, args=[href_product_path])
    return CasTask(task_id=task.id, task_status=task.status)
