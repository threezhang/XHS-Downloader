from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional
from source import XHS, Settings
from source.module import REPOSITORY, VERSION_MAJOR, VERSION_MINOR, VERSION_BETA

class WebServer:
    def __init__(self):
        self.xhs: Optional[XHS] = None
        self.app: Optional[FastAPI] = None
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """FastAPI 生命周期管理"""
        self.xhs = XHS(**Settings().run())
        await self.xhs.__aenter__()
        yield
        await self.xhs.__aexit__(None, None, None)
    
    def init_app(self):
        """初始化FastAPI应用"""
        self.app = FastAPI(
            title="XHS-Downloader",
            description="小红书下载器Web界面",
            version=f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BETA}",
            lifespan=self.lifespan
        )
        
        # 添加CORS支持
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        templates = Jinja2Templates(directory="source/web/templates")
        
        @self.app.get("/")
        async def index(request: Request):
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "version": f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BETA}",
                    "repository": REPOSITORY
                }
            )
            
        @self.app.post("/api/extract")
        async def extract(url: str = Form(...)):
            try:
                data = await self.xhs.extract(url, download=False)
                if isinstance(data, list):
                    data = data[0]
                if not data:
                    return {"success": False, "error": "无法获取数据"}
                    
                print("Debug - Extracted data:", data)
                
                # 构造返回数据
                result = {
                    "作品标题": data.get("作品标题", ""),
                    "作者昵称": data.get("作者昵称", ""),
                    "作品描述": data.get("作品描述", ""),
                    "作品类型": data.get("作品类型", ""),
                    "发布时间": data.get("发布时间", ""),
                    "图片列表": [],
                    "动图列表": [],
                    "视频地址": ""
                }

                # 处理媒体内容
                if data.get("作品类型") == "图文":
                    # 处理静态图片
                    result["图片列表"] = [url for url in data.get("下载地址", []) if url]
                    # 处理动图
                    result["动图列表"] = [url for url in data.get("动图地址", []) if url and url != 'NaN']
                elif data.get("作品类型") == "视频":
                    # 对于视频类型，使用第一个下载地址作为视频地址
                    video_urls = data.get("下载地址", [])
                    if video_urls and isinstance(video_urls, list) and len(video_urls) > 0:
                        result["视频地址"] = video_urls[0]
                
                print("Debug - Formatted result:", result)
                return {"success": True, "data": result}
            except Exception as e:
                print(f"Error extracting data: {str(e)}")
                import traceback
                traceback.print_exc()
                return {"success": False, "error": str(e)}
        
        # 挂载静态文件
        self.app.mount("/static", StaticFiles(directory="source/web/static"), name="static")
        
        return self.app
    
    async def start(self, host: str = "0.0.0.0", port: int = 8000, log_level: str = "info"):
        """启动Web服务器"""
        app = self.init_app()
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level=log_level
        )
        server = uvicorn.Server(config)
        await server.serve()

    @classmethod
    async def run(cls, host: str = "0.0.0.0", port: int = 8000, log_level: str = "info"):
        """快速启动方法"""
        server = cls()
        await server.start(host, port, log_level)

# 创建一个应用实例供 uvicorn 使用
app = WebServer().init_app() 