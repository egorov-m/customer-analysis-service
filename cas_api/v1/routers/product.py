from http import HTTPStatus

from fastapi import APIRouter, Depends

from cas_api.deps import get_db
from cas_shared.db.models import Product
from cas_shared.db.repository import ProductRepository
from cas_shared.exceptions.cas_api_error import CasError, CasErrorCode
from cas_shared.schemas.product import FoundProduct

router = APIRouter()


@router.get(
    "/info",
    response_model=FoundProduct
)
def get_product_info(product_name_id: str, session=Depends(get_db)):
    repo: ProductRepository = ProductRepository(session)
    db_product: Product = repo.get_product(product_name_id)
    if db_product is not None:
        return FoundProduct(name_id=db_product.name_id, fullname=db_product.fullname, image_url=db_product.image_url)
    else:
        raise CasError(message=f"Product {product_name_id} is not found.",
                       error_code=CasErrorCode.PRODUCT_NOT_FOUND,
                       http_status_code=HTTPStatus.NOT_FOUND)
