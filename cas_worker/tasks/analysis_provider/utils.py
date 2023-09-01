from functools import wraps

from starlette import status

from cas_shared.exceptions.cas_api_error import CasError, CasErrorCode


def manage_result_size():
    def decorator(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            result = f(*args, **kwargs)

            if len(result) < 1:
                raise CasError(
                    message="The specified product is not available to receive analysis due to insufficient data or does not exist.",
                    error_code=CasErrorCode.ANALYSIS_SHAPER_ERROR,
                    http_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            return result

        return wrapped_f

    return decorator
