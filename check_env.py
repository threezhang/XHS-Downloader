import sys
import platform
from pathlib import Path

def check_environment():
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    
    try:
        import fastapi
        print(f"FastAPI 版本: {fastapi.__version__}")
    except ImportError:
        print("FastAPI 未安装")
    
    try:
        import uvicorn
        print(f"Uvicorn 版本: {uvicorn.__version__}")
    except ImportError:
        print("Uvicorn 未安装")
    
    try:
        import gunicorn
        print(f"Gunicorn 版本: {gunicorn.__version__}")
    except ImportError:
        print("Gunicorn 未安装")

if __name__ == "__main__":
    check_environment() 