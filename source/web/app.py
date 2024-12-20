from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from pathlib import Path
import os
from source.module.tools import extract_note_id
from source.module.static import API_ENDPOINTS

app = FastAPI(title="XHS Downloader")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前文件所在目录
current_dir = Path(__file__).parent

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")

# 设置模板目录
templates = Jinja2Templates(directory=str(current_dir / "templates"))

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "version": "2.4"})

@app.post("/api/extract")
async def extract(url: str = Form(...)):
    try:
        # 提取笔记ID
        note_id = extract_note_id(url)
        if not note_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "无效的小红书链接"}
            )

        # 构建API请求
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": os.getenv("XHS_COOKIE", "")  # 从环境变量获取Cookie
        }

        # 获取笔记信息
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                API_ENDPOINTS["note_info"].format(note_id=note_id),
                headers=headers
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"success": False, "error": "获取数据失败"}
                )

            data = response.json()
            if not data.get("success"):
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": data.get("msg", "获取数据失败")}
                )

            # 处理数据
            note_data = data["data"]
            processed_data = {
                "作品标题": note_data.get("title", ""),
                "作者昵称": note_data.get("user", {}).get("nickname", ""),
                "作品描述": note_data.get("desc", ""),
                "作品类型": "视频" if note_data.get("type") == "video" else "图文",
                "发布时间": note_data.get("time", ""),
                "图片列表": [img.get("url") for img in note_data.get("images", [])],
                "动图列表": [img.get("url") for img in note_data.get("video_thumbnails", [])],
                "视频地址": note_data.get("video", {}).get("url", "") if note_data.get("type") == "video" else None
            }

            return {"success": True, "data": processed_data}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"服务器错误: {str(e)}"}
        )

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "healthy"}