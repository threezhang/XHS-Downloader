import uvicorn
from watchfiles import run_process
from pathlib import Path

def run_dev_server():
    """运行开发服务器（带热加载）"""
    web_dir = Path(__file__).parent
    
    uvicorn_config = {
        "app": "source.web.server:WebServer().init_app()",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "reload_dirs": [str(web_dir)],
        "reload_includes": ["*.py", "*.html", "*.css", "*.js"],
    }
    
    # 监视静态文件和模板变化
    watch_paths = [
        web_dir / "templates",
        web_dir / "static",
    ]
    
    run_process(
        target=lambda: uvicorn.run(**uvicorn_config),
        watch_paths=watch_paths,
    )

if __name__ == "__main__":
    run_dev_server() 