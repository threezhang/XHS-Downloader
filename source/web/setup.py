from pathlib import Path
import shutil

def setup_web_directories():
    """设置Web服务所需的目录结构"""
    # 获取当前文件所在目录
    current_dir = Path(__file__).parent
    
    # 创建必要的目录
    directories = {
        'static': current_dir / 'static',
        'static/css': current_dir / 'static' / 'css',
        'static/js': current_dir / 'static' / 'js',
        'static/img': current_dir / 'static' / 'img',
        'templates': current_dir / 'templates',
    }
    
    # 创建目录
    for path in directories.values():
        path.mkdir(parents=True, exist_ok=True)
    
    return directories

if __name__ == '__main__':
    setup_web_directories() 