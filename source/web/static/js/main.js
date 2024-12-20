let currentIndex = 0;
let currentMediaList = [];

document.addEventListener('DOMContentLoaded', function() {
    const fetchForm = document.getElementById('fetchForm');
    let currentImages = [];
    let currentGifs = [];
    
    // 键盘快捷键支持
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + V 自动粘贴并提交
        if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
            const urlInput = document.getElementById('url');
            if (document.activeElement !== urlInput) {
                e.preventDefault();
                navigator.clipboard.readText().then(text => {
                    urlInput.value = text;
                    fetchForm.dispatchEvent(new Event('submit'));
                });
            }
        }
    });

    // 输入框自动聚焦
    const urlInput = document.getElementById('url');
    urlInput.focus();

    // 输入框粘贴优化
    urlInput.addEventListener('paste', (e) => {
        e.preventDefault();
        const text = e.clipboardData.getData('text');
        // 自动提取链接
        const urlMatch = text.match(/https?:\/\/[^\s]+/);
        if (urlMatch) {
            urlInput.value = urlMatch[0];
            // 自动提交
            fetchForm.dispatchEvent(new Event('submit'));
        } else {
            urlInput.value = text;
        }
    });

    // 创建媒体预览模态框
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/90 hidden items-center justify-center z-50';
    modal.innerHTML = `
        <div class="relative w-full h-full flex items-center justify-center p-4">
            <button class="absolute top-4 right-4 text-white/80 hover:text-white">
                <i class="bi bi-x-lg text-2xl"></i>
            </button>
            <div class="max-w-full max-h-full" id="modalContent"></div>
        </div>
    `;
    document.body.appendChild(modal);

    // 关闭模态框
    modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target.closest('button')) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            const video = modal.querySelector('video');
            if (video) video.pause();
        }
    });

    // 创建图片查看器
    const viewer = document.createElement('div');
    viewer.className = 'viewer-overlay';
    viewer.innerHTML = `
        <div class="viewer-toolbar">
            <button class="zoom-in" title="放大">
                <i class="bi bi-zoom-in"></i>
            </button>
            <button class="zoom-out" title="缩小">
                <i class="bi bi-zoom-out"></i>
            </button>
            <button class="zoom-reset" title="重置">
                <i class="bi bi-arrows-angle-contract"></i>
            </button>
            <button class="close" title="关闭">
                <i class="bi bi-x-lg"></i>
            </button>
        </div>
        <div class="nav-arrow prev">
            <i class="bi bi-chevron-left text-2xl"></i>
        </div>
        <div class="nav-arrow next">
            <i class="bi bi-chevron-right text-2xl"></i>
        </div>
        <div class="viewer-content"></div>
        <div class="zoom-indicator">100%</div>
    `;
    document.body.appendChild(viewer);

    // 添加键盘导航
    document.addEventListener('keydown', (e) => {
        if (viewer.style.display === 'flex') {
            if (e.key === 'ArrowLeft') {
                showPrevious();
            } else if (e.key === 'ArrowRight') {
                showNext();
            } else if (e.key === 'Escape') {
                closeViewer();
            }
        }
    });

    // 关闭查看器
    function closeViewer() {
        viewer.style.display = 'none';
        const video = viewer.querySelector('video');
        if (video) video.pause();
    }

    // 显示上一个
    function showPrevious() {
        if (currentIndex > 0) {
            currentIndex--;
            updateViewer();
        }
    }

    // 显示下一个
    function showNext() {
        if (currentIndex < currentMediaList.length - 1) {
            currentIndex++;
            updateViewer();
        }
    }

    // 更新查看器内容
    function updateViewer() {
        const url = currentMediaList[currentIndex];
        const content = viewer.querySelector('.viewer-content');
        const isVideo = url.endsWith('.mp4');
        
        if (isVideo) {
            content.innerHTML = `<video src="${url}" controls autoplay class="max-w-[90vw] max-h-[90vh] object-contain"></video>`;
            viewer.querySelector('.zoom-in').style.display = 'none';
            viewer.querySelector('.zoom-out').style.display = 'none';
            viewer.querySelector('.zoom-reset').style.display = 'none';
        } else {
            content.innerHTML = `<img src="${url}" class="max-w-[90vw] max-h-[90vh] object-contain" alt="预览图">`;
            viewer.querySelector('.zoom-in').style.display = 'flex';
            viewer.querySelector('.zoom-out').style.display = 'flex';
            viewer.querySelector('.zoom-reset').style.display = 'flex';
        }
        
        // 重置缩放状态
        currentScale = 1;
        translateX = 0;
        translateY = 0;
        updateImageTransform();
    }

    // 更新图片变换
    function updateImageTransform() {
        const img = viewer.querySelector('img');
        if (img) {
            img.style.transform = `translate(${translateX}px, ${translateY}px) scale(${currentScale})`;
            viewer.querySelector('.zoom-indicator').textContent = `${Math.round(currentScale * 100)}%`;
            viewer.querySelector('.zoom-indicator').classList.toggle('active', currentScale !== 1);
            img.classList.toggle('zoomed', currentScale > 1);
        }
    }

    // 添加缩放事件处理
    viewer.querySelector('.zoom-in').onclick = () => {
        currentScale = Math.min(currentScale * 1.5, 5);
        updateImageTransform();
    };

    viewer.querySelector('.zoom-out').onclick = () => {
        currentScale = Math.max(currentScale / 1.5, 1);
        translateX = 0;
        translateY = 0;
        updateImageTransform();
    };

    viewer.querySelector('.zoom-reset').onclick = () => {
        currentScale = 1;
        translateX = 0;
        translateY = 0;
        updateImageTransform();
    };

    // 添加拖动支持
    viewer.querySelector('.viewer-content').addEventListener('mousedown', (e) => {
        const img = viewer.querySelector('img');
        if (img && currentScale > 1) {
            isDragging = true;
            startX = e.clientX - translateX;
            startY = e.clientY - translateY;
            img.style.transition = 'none';
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            updateImageTransform();
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        const img = viewer.querySelector('img');
        if (img) {
            img.style.transition = 'transform 0.3s ease';
        }
    });

    // 添加滚轮缩放支持
    viewer.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        currentScale = Math.max(1, Math.min(currentScale * delta, 5));
        updateImageTransform();
    });

    // 修改 createMediaElement 函数中的点击事件
    function createMediaElement(url, index, isVideo = false) {
        const mediaItem = document.createElement('div');
        mediaItem.className = 'media-item group cursor-pointer';
        
        if (isVideo) {
            // 对于动图，直接使用自动播放的video标签
            const video = document.createElement('video');
            video.src = url;
            video.className = 'w-full h-full object-cover';
            video.autoplay = true;
            video.loop = true;
            video.muted = true;
            video.playsInline = true;
            video.controls = false; // 移除控制条
            video.loading = 'lazy';
            
            // 添加预览功能
            mediaItem.onclick = (e) => {
                e.preventDefault();
                currentMediaList = currentGifs;
                currentIndex = index;
                updateViewer();
                viewer.style.display = 'flex';
            };
            mediaItem.appendChild(video);
        } else {
            const img = document.createElement('img');
            img.src = url;
            img.className = 'w-full h-full object-cover';
            img.alt = `预览图 ${index + 1}`;
            img.loading = 'lazy';
            
            // 添加预览功能
            mediaItem.onclick = (e) => {
                e.preventDefault();
                currentMediaList = isVideo ? currentGifs : currentImages;
                currentIndex = index;
                updateViewer();
                viewer.style.display = 'flex';
            };
            mediaItem.appendChild(img);
        }

        // 添加下载按钮
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'absolute bottom-2 right-2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity z-10';
        downloadBtn.innerHTML = '<i class="bi bi-download"></i>';
        downloadBtn.onclick = (e) => {
            e.stopPropagation();
            const a = document.createElement('a');
            a.href = url;
            a.download = '';
            a.target = '_blank';
            a.click();
        };
        mediaItem.appendChild(downloadBtn);
        
        return mediaItem;
    }

    // 显示媒体内容
    function displayMedia(urls, containerId, isVideo = false) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        if (!urls || urls.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'col-span-full text-center text-gray-500 py-8';
            emptyMessage.textContent = '暂无内容';
            container.appendChild(emptyMessage);
            return;
        }
        
        urls.forEach((url, index) => {
            if (url && url !== 'NaN') {
                const element = createMediaElement(url, index, isVideo);
                container.appendChild(element);
            }
        });
    }

    // 复制功能
    function setupCopyButton(buttonId, urls) {
        const button = document.getElementById(buttonId);
        if (!button) return;
        
        button.onclick = async () => {
            if (urls.length > 0) {
                try {
                    await navigator.clipboard.writeText(urls.join('\n'));
                    showToast('复制成功');
                } catch (err) {
                    console.error('Failed to copy:', err);
                    showToast('复制失败', 'error');
                }
            }
        };
    }

    // Toast 提示
    function showToast(message, type = 'success') {
        const toast = document.getElementById('copyToast');
        toast.className = type === 'success' 
            ? 'flex items-center gap-2 px-4 py-3 rounded-lg bg-green-500/20 text-green-400 border border-green-500/20 shadow-lg toast-enter'
            : 'flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/20 text-red-400 border border-red-500/20 shadow-lg toast-enter';
        toast.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'x-circle'}"></i>
            <span>${message}</span>
        `;
        
        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => {
                toast.className = 'hidden';
            }, 300);
        }, 2000);
    }

    // 表单提交处理
    fetchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = document.getElementById('url').value;
        const loading = document.getElementById('loading');
        const content = document.getElementById('content');
        const error = document.getElementById('error');
        
        loading.classList.remove('hidden');
        content.classList.add('hidden');
        error.classList.add('hidden');
        
        try {
            const formData = new FormData();
            formData.append('url', url);
            
            const response = await fetch('/api/extract', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success && result.data) {
                const data = result.data;
                console.log('Received data:', data);
                
                // 更新基本信息
                document.getElementById('title').textContent = data['作品标题'] || 'N/A';
                document.getElementById('author').textContent = data['作者昵称'] || 'N/A';
                document.getElementById('description').textContent = data['作品描述'] || 'N/A';
                document.getElementById('type').textContent = data['作品类型'] || 'N/A';
                document.getElementById('time').textContent = data['发布时间'] || 'N/A';
                
                // 根据类型显示内容
                const imageSection = document.getElementById('imageSection');
                const gifSection = document.getElementById('gifSection');
                const videoSection = document.getElementById('videoSection');
                
                if (data['作品类型'] === '图文') {
                    // 处理图片
                    imageSection.classList.remove('hidden');
                    currentImages = data['图片列表'];
                    displayMedia(currentImages, 'imageGallery');
                    setupCopyButton('copyImagesBtn', currentImages);
                    
                    // 处理动图
                    currentGifs = data['动图列表'];
                    if (currentGifs.length > 0) {
                        gifSection.classList.remove('hidden');
                        displayMedia(currentGifs, 'gifGallery', true);
                        setupCopyButton('copyGifsBtn', currentGifs);
                    } else {
                        gifSection.classList.add('hidden');
                    }
                    
                    videoSection.classList.add('hidden');
                } else if (data['作品类型'] === '视频') {
                    imageSection.classList.add('hidden');
                    gifSection.classList.add('hidden');
                    videoSection.classList.remove('hidden');
                    
                    const videoPlayer = document.getElementById('videoPlayer');
                    if (data['视频地址']) {
                        videoPlayer.innerHTML = `
                            <video src="${data['视频地址']}" 
                                   class="w-full h-full" 
                                   controls 
                                   playsinline>
                            </video>`;
                    } else {
                        videoPlayer.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500">无法加载视频</div>';
                    }
                }
                
                content.classList.remove('hidden');
            } else {
                error.textContent = result.error || '获取数据失败';
                error.classList.remove('hidden');
            }
        } catch (err) {
            console.error('Error:', err);
            error.textContent = '获取数据失败：' + (err.message || '未知错误');
            error.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    });

    // 添加导航箭头事件
    viewer.querySelector('.prev').onclick = showPrevious;
    viewer.querySelector('.next').onclick = showNext;
    viewer.onclick = (e) => {
        if (e.target === viewer) {
            closeViewer();
        }
    };
}); 