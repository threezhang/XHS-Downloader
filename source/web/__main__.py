from asyncio import run
from asyncio.exceptions import CancelledError
from contextlib import suppress
import click
import uvicorn
from .server import WebServer
from .setup import setup_web_directories

@click.command()
@click.option('--host', default="0.0.0.0", help='服务器主机地址')
@click.option('--port', default=8000, help='服务器端口')
@click.option('--log-level', default="info", help='日志级别')
@click.option('--dev', is_flag=True, help='开发模式（启用热加载）')
def main(host: str, port: int, log_level: str, dev: bool):
    """启动小红书下载器Web服务"""
    # 确保目录结构存在
    setup_web_directories()
    
    if dev:
        # 开发模式 - 使用 uvicorn 的热重载功能
        uvicorn.run(
            "source.web.server:app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=["source/web"],
            log_level=log_level
        )
    else:
        # 生产模式
        with suppress(KeyboardInterrupt, CancelledError):
            run(WebServer.run(host, port, log_level))

if __name__ == '__main__':
    main() 