import os

MODEL_ID = os.getenv("MODEL_ID", "aegisscan/hazard-vision-v0.1")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0-demo")
MAX_INCIDENTS = int(os.getenv("MAX_INCIDENTS", "100"))
