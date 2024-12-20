import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import asyncio
from PIL import Image, ImageTk
import io
import aiohttp
from urllib.parse import urlparse
import json

class XHSGui:
    def __init__(self, xhs_instance):
        self.xhs = xhs_instance
        self.root = tk.Tk()
        self.root.title("XHS-Downloader GUI")
        self.root.geometry("800x600")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL输入框
        self.url_frame = ttk.Frame(self.main_frame)
        self.url_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.url_label = ttk.Label(self.url_frame, text="小红书链接:")
        self.url_label.grid(row=0, column=0, padx=5)
        
        self.url_entry = ttk.Entry(self.url_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5)
        
        self.fetch_button = ttk.Button(self.url_frame, text="获取内容", command=self.fetch_content)
        self.fetch_button.grid(row=0, column=2, padx=5)
        
        # 内容展示区
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 作品信息展示
        self.info_text = scrolledtext.ScrolledText(self.content_frame, height=10)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 预览图片展示区域
        self.preview_frame = ttk.Frame(self.content_frame)
        self.preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.status_var.set("就绪")
        
    async def fetch_preview_image(self, url):
        """获取预览图片"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        image = Image.open(io.BytesIO(data))
                        # 调整图片大小
                        image.thumbnail((200, 200))
                        return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"获取预览图片失败: {e}")
        return None

    def show_content(self, data):
        """显示抓取的内容"""
        # 清空之前的内容
        self.info_text.delete(1.0, tk.END)
        
        # 显示基本信息
        info_text = f"""
标题: {data.get('作品标题', 'N/A')}
作者: {data.get('作者昵称', 'N/A')}
描述: {data.get('作品描述', 'N/A')}
类型: {data.get('作品类型', 'N/A')}
发布时间: {data.get('发布时间', 'N/A')}
        """
        self.info_text.insert(tk.END, info_text)

    async def _fetch_content(self):
        """异步获取内容"""
        url = self.url_entry.get().strip()
        if not url:
            self.status_var.set("请输入有效的小红书链接")
            return
            
        self.status_var.set("正在获取内容...")
        self.fetch_button.state(['disabled'])
        
        try:
            data = await self.xhs.extract(url, download=False, data=True)
            if data and isinstance(data, list):
                data = data[0]  # 获取第一个结果
                
            if data:
                self.show_content(data)
                self.status_var.set("获取内容成功")
            else:
                self.status_var.set("获取内容失败")
        except Exception as e:
            self.status_var.set(f"发生错误: {str(e)}")
        finally:
            self.fetch_button.state(['!disabled'])

    def fetch_content(self):
        """触发异步获取内容"""
        asyncio.run(self._fetch_content())

    def run(self):
        """运行GUI"""
        self.root.mainloop() 