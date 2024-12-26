import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

# from src.common.utils.constants import EZ_FILE_IDS
# from src.common.utils.cloudwatch import CloudwatchInstance
# from src.common.utils.s3_helper import S3Instance
# from src.db.functions.tm_files import get_ez_tm_file_ids
# from src.db.utils import SessionFactory
# from src.resources import router
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
