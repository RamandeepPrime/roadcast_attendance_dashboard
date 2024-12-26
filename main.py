import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from app.routers import router

app = FastAPI(
	default_response_class = ORJSONResponse,
	redoc_url = None,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(router, prefix = '/dashboard/api')

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8005, reload = True)
