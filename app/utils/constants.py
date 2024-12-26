import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
DATABASE_URL = "postgresql+asyncpg://{}:{}@{}/{}".format(
	urllib.parse.quote_plus(os.getenv("DATABASE_USER")),
	urllib.parse.quote_plus(os.getenv("DATABASE_PASS")),
	os.getenv("DATABASE_URL"),
	os.getenv("DATABASE_DB"),
)

JWT_SUBJECT = "access"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRATION'))
JWT_SECRET_KEY = os.getenv('SECRET_KEY')

IS_LOCAL = os.getenv('IS_LOCAL') == 'TRUE'