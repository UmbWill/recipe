import os
import math
from dotenv import load_dotenv
load_dotenv()

class BaseConfig(object):
    CACHE_TYPE = os.getenv("CACHE_TYPE") 
    CACHE_REDIS_HOST = os.getenv("CACHE_REDIS_HOST") 
    CACHE_REDIS_PORT = os.getenv("CACHE_REDIS_PORT") 
    CACHE_REDIS_DB = os.getenv("CACHE_REDIS_DB") 
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL") 
    CACHE_DEFAULT_TIMEOUT = os.getenv("CACHE_DEFAULT_TIMEOUT") if str(os.getenv("CACHE_DEFAULT_TIMEOUT")) != "0" else int(math.pow(2,31)-1)
