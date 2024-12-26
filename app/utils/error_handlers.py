import time

from typing import Callable, Coroutine, Any
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.routing import APIRoute

from app.database.custom_errors import DatabaseErrors
from app.utils.custom_errors import UserErrors
from app.utils.logging_config import logger


class ErrorHandlingLoggingRoute(APIRoute):
	def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
		original_route_handler = super().get_route_handler()

		async def custom_route_handler(request: Request) -> Response:
			start_time = time.perf_counter()
			try:
				response = await original_route_handler(request)

			# Happens when No auth is given and Oauth Handler raises HTTP Exception
			except HTTPException:
				raise

			except UserErrors as exc:
				return JSONResponse(
					content = {
						'details': {
							'type': exc.type,
							'message' : exc.message,
							'error_details' : exc.error_details
						},
						'message' : exc.message,
						'success' : False
					},
					status_code = exc.response_code
				)
			
			except RequestValidationError:
				raise

			except Exception as e:
				logger.error("Some unknown error occurred", exc_info=True)
				return JSONResponse(
					content = {
						'details' : {
							'type': 'Internal Server Error',
							'message' : 'Internal Server Error',
							'error_details': None
						},
						'message' : 'Internal Server Error', 'success' : False
					},
					status_code = 500
				)
			
			response.headers["X-Process-Time"] = (
				f"{round((time.perf_counter() - start_time) * 1000, 3)} ms"
			)
			return response

		return custom_route_handler
