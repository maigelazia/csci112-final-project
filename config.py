import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/test")
DB_NAME = os.getenv("DB_NAME", "clinic")

# APP
SECRET_KEY = os.getenv("SECRET_KEY", "dev123")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345")

# EMAIL (MAILTRAP)
MAIL_SERVER = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
MAIL_PORT = int(os.getenv("MAIL_PORT", 2525))
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@clinic.com")

# URLs
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
