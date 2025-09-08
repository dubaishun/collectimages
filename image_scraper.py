#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网页图片采集器
功能：从指定网址采集图片，提供GUI界面进行预览和按顺序下载
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import requests
from bs4 import BeautifulSoup
import os
import threading
from urllib.parse import urljoin, urlparse
from PIL import Image, ImageTk
import io
import time

class ImageScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("网页图片采集器")
        
        # 设置窗口大小并居中显示
        window_width = 1000
        window_height = 750  # 增加高度以适应版权信息
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算居中位置
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # 设置最小窗口大小
        self.root.minsize(800, 600)
        
        # 图片数据存储
        self.image_urls = []
        self.image_previews = []
        self.all_found_urls = []  # 存储所有找到的URL（包括被过滤的）
        self.download_folder = ""
        
        # 默认网址
        self.default_url = "https://finance.sina.cn/2024-06-23/detail-inaztrwf3233956.d.html"
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # URL输入区域
        url_frame = ttk.LabelFrame(main_frame, text="网址输入", padding="5")
        url_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="网址:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.url_entry.insert(0, self.default_url)
        
        self.fetch_btn = ttk.Button(url_frame, text="采集图片", command=self.fetch_images)
        self.fetch_btn.grid(row=0, column=2, padx=(5, 0))
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.select_folder_btn = ttk.Button(control_frame, text="选择下载文件夹", command=self.select_download_folder)
        self.select_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_btn = ttk.Button(control_frame, text="按顺序下载所有图片", command=self.download_all_images, state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 新增：显示所有找到的URL的按钮
        self.show_all_urls_btn = ttk.Button(control_frame, text="显示所有图片URL", command=self.show_all_urls, state=tk.DISABLED)
        self.show_all_urls_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.folder_label = ttk.Label(control_frame, text="未选择下载文件夹")
        self.folder_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 主内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧：图片列表
        list_frame = ttk.LabelFrame(content_frame, text="图片列表", padding="5")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview来显示图片列表
        columns = ("序号", "文件名", "URL", "状态")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.tree.heading("序号", text="序号")
        self.tree.heading("文件名", text="文件名")
        self.tree.heading("URL", text="图片URL")
        self.tree.heading("状态", text="下载状态")
        
        self.tree.column("序号", width=50, minwidth=50)
        self.tree.column("文件名", width=150, minwidth=100)
        self.tree.column("URL", width=300, minwidth=200)
        self.tree.column("状态", width=100, minwidth=80)
        
        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_image_select)
        
        # 右侧：图片预览和日志
        right_frame = ttk.Frame(content_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # 图片预览区域
        preview_frame = ttk.LabelFrame(right_frame, text="图片预览", padding="5")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_label = ttk.Label(preview_frame, text="请选择图片进行预览")
        self.preview_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志区域
        log_frame = ttk.LabelFrame(right_frame, text="操作日志", padding="5")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=50)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # 版权信息区域
        copyright_frame = ttk.Frame(main_frame)
        copyright_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))
        copyright_frame.columnconfigure(0, weight=1)
        
        # 添加上分隔线
        top_separator = ttk.Separator(copyright_frame, orient='horizontal')
        top_separator.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 创建版权内容框架
        copyright_content_frame = ttk.Frame(copyright_frame)
        copyright_content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        copyright_content_frame.columnconfigure(0, weight=1)
        
        # 主版权文本
        copyright_text = "© 2025 速光网络软件开发"
        copyright_label = ttk.Label(
            copyright_content_frame, 
            text=copyright_text,
            font=('Microsoft YaHei UI', 9, 'bold'),
            foreground='#2c3e50',
            anchor='center'
        )
        copyright_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 网站信息
        website_text = "suguang.cc"
        website_label = ttk.Label(
            copyright_content_frame, 
            text=website_text,
            font=('Arial', 8),
            foreground='#3498db',
            anchor='center'
        )
        website_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
        
        # 版本信息
        version_text = "Version 1.0 - 网页图片采集器"
        version_label = ttk.Label(
            copyright_content_frame, 
            text=version_text,
            font=('Arial', 7),
            foreground='#7f8c8d',
            anchor='center'
        )
        version_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(3, 0))
        
    def log_message(self, message):
        """添加日志消息"""
        current_time = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{current_time}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def fetch_images(self):
        """采集网页图片"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入网址")
            return
            
        # 在新线程中执行采集任务
        self.fetch_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._fetch_images_thread, args=(url,), daemon=True).start()
        
    def _fetch_images_thread(self, url):
        """在线程中采集图片"""
        try:
            self.log_message(f"开始采集网页: {url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 获取网页内容
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            self.log_message("网页获取成功，开始解析...")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有图片标签
            img_tags = soup.find_all('img')
            self.log_message(f"发现 {len(img_tags)} 个图片标签")
            
            # 清空之前的数据
            self.image_urls.clear()
            self.image_previews.clear()
            self.all_found_urls.clear()
            
            # 清空列表
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 提取图片URL
            valid_images = []
            
            for i, img in enumerate(img_tags):
                # 尝试从多个属性中获取图片URL
                possible_urls = []
                
                # 常见的图片URL属性
                src_attrs = ['src', 'data-src', 'data-original', 'data-lazy-src', 
                           'data-srcset', 'data-img-src', 'data-url', 'data-thumb']
                
                for attr in src_attrs:
                    attr_value = img.get(attr)
                    if attr_value:
                        possible_urls.append(attr_value)
                
                # 处理srcset属性（可能包含多个URL）
                srcset = img.get('srcset')
                if srcset:
                    # 解析srcset，提取URL
                    for src_desc in srcset.split(','):
                        src_url = src_desc.strip().split()[0]
                        if src_url:
                            possible_urls.append(src_url)
                
                # 处理每个可能的URL
                for src in possible_urls:
                    if src and src.strip():
                        # 转换为绝对URL
                        abs_url = urljoin(url, src.strip())
                        self.all_found_urls.append(abs_url)
                        
                        # 使用更宽松的过滤条件
                        if self._is_valid_image_url(abs_url, img):
                            # 避免重复添加同一个URL
                            if not any(existing_url == abs_url for _, existing_url in valid_images):
                                valid_images.append((len(valid_images)+1, abs_url))
            
            self.log_message(f"总共发现 {len(self.all_found_urls)} 个图片URL")
            self.log_message(f"其中前5个示例: {self.all_found_urls[:5]}")
            
            self.log_message(f"筛选出 {len(valid_images)} 个有效图片")
            
            # 更新进度条
            self.progress.config(maximum=len(valid_images))
            
            # 处理每个图片
            for i, (order, img_url) in enumerate(valid_images):
                try:
                    # 生成文件名
                    filename = self._generate_filename(img_url, order)
                    
                    # 添加到列表
                    self.image_urls.append({
                        'order': order,
                        'url': img_url,
                        'filename': filename,
                        'status': '待下载'
                    })
                    
                    # 添加到树形视图
                    self.tree.insert("", tk.END, values=(order, filename, img_url, "待下载"))
                    
                    # 更新进度
                    self.progress.config(value=i+1)
                    self.log_message(f"处理图片 {i+1}/{len(valid_images)}: {filename}")
                    
                except Exception as e:
                    self.log_message(f"处理图片时出错: {str(e)}")
                    
            self.log_message(f"图片采集完成！共找到 {len(self.image_urls)} 张图片")
            
            # 启用相关按钮
            if self.image_urls:
                self.download_btn.config(state=tk.NORMAL)
            if self.all_found_urls:
                self.show_all_urls_btn.config(state=tk.NORMAL)
                
        except Exception as e:
            self.log_message(f"采集失败: {str(e)}")
            messagebox.showerror("采集失败", f"采集图片时发生错误:\n{str(e)}")
            
        finally:
            self.fetch_btn.config(state=tk.NORMAL)
            self.progress.config(value=0)
            
    def _is_valid_image_url(self, url, img_tag=None):
        """检查是否为有效的图片URL（使用更宽松的条件）"""
        if not url or url.startswith('data:') or url.startswith('#'):
            return False
            
        parsed = urlparse(url)
        path = parsed.path.lower()
        query = parsed.query.lower()
        
        # 1. 检查明显的排除条件（更严格的过滤）
        exclude_keywords = ['logo', 'icon', 'avatar', 'ads', 'banner', 'button', 
                          'sprite', 'loading', 'placeholder', 'spacer', 'pixel',
                          'blank', 'transparent', '1x1', 'tracking']
        
        # 检查URL中是否包含排除关键词
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in exclude_keywords):
            return False
            
        # 2. 检查图片尺寸（排除过小的图片）
        if img_tag:
            width = img_tag.get('width')
            height = img_tag.get('height')
            
            # 如果指定了尺寸且太小，可能是装饰性图片
            try:
                if width and height:
                    w, h = int(width), int(height)
                    if w < 50 and h < 50:
                        return False
            except (ValueError, TypeError):
                pass
        
        # 3. 积极条件检查（满足任一即可）
        positive_indicators = [
            # 常见图片扩展名
            any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']),
            
            # 图片服务的特征
            any(indicator in url_lower for indicator in [
                'image', 'img', 'photo', 'pic', 'thumb', 'media', 'upload',
                'w=', 'width=', 'h=', 'height=', 'size=', 'resize', 'crop',
                'quality=', 'format=', 'cdn', 'amazonaws', 'cloudfront'
            ]),
            
            # 新浪等媒体网站的图片特征
            any(domain in url_lower for domain in [
                'sinaimg', 'sina.com', 'sina.cn', 'img.sina'
            ]),
            
            # 检查是否是合理的图片URL路径
            '/image' in path or '/img' in path or '/photo' in path or '/media' in path,
            
            # 包含图片相关的查询参数
            any(param in query for param in ['format=', 'size=', 'w=', 'h=', 'quality='])
        ]
        
        # 如果满足任何积极条件，则认为是有效图片
        is_valid = any(positive_indicators)
        
        return is_valid
        
    def _generate_filename(self, url, order):
        """生成文件名"""
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # 获取原始文件名
            original_name = os.path.basename(path)
            
            # 如果没有扩展名，尝试从URL参数中获取
            if not original_name or '.' not in original_name:
                # 默认使用jpg扩展名
                original_name = f"image_{order}.jpg"
            
            # 确保文件名唯一性
            name, ext = os.path.splitext(original_name)
            filename = f"{order:03d}_{name}{ext}"
            
            return filename
            
        except:
            return f"{order:03d}_image.jpg"
            
    def select_download_folder(self):
        """选择下载文件夹"""
        folder = filedialog.askdirectory(title="选择图片下载文件夹")
        if folder:
            self.download_folder = folder
            self.folder_label.config(text=f"下载到: {folder}")
            self.log_message(f"已选择下载文件夹: {folder}")
            
    def on_image_select(self, event):
        """当选择图片时显示预览"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        if len(values) >= 3:
            img_url = values[2]  # URL在第3列
            self._show_preview(img_url)
            
    def _show_preview(self, img_url):
        """显示图片预览"""
        threading.Thread(target=self._load_preview_thread, args=(img_url,), daemon=True).start()
        
    def _load_preview_thread(self, img_url):
        """在线程中加载预览图片"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(img_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 加载图片
            image = Image.open(io.BytesIO(response.content))
            
            # 调整大小以适应预览区域
            max_size = (300, 300)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self._update_preview(photo))
            
        except Exception as e:
            self.root.after(0, lambda: self.preview_label.config(text=f"预览加载失败:\n{str(e)}", image=""))
            
    def _update_preview(self, photo):
        """更新预览图片"""
        self.preview_label.config(image=photo, text="")
        # 保持引用防止图片被垃圾回收
        self.preview_label._photo_ref = photo
        
    def download_all_images(self):
        """按顺序下载所有图片"""
        if not self.download_folder:
            messagebox.showerror("错误", "请先选择下载文件夹")
            return
            
        if not self.image_urls:
            messagebox.showerror("错误", "没有可下载的图片")
            return
            
        # 在新线程中执行下载任务
        self.download_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._download_all_thread, daemon=True).start()
        
    def _download_all_thread(self):
        """在线程中下载所有图片"""
        try:
            total_images = len(self.image_urls)
            self.progress.config(maximum=total_images)
            
            success_count = 0
            failed_count = 0
            
            self.log_message(f"开始按顺序下载 {total_images} 张图片...")
            
            for i, img_info in enumerate(self.image_urls):
                try:
                    # 更新状态为"下载中"
                    self._update_tree_status(i, "下载中")
                    
                    # 下载图片
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(img_info['url'], headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    # 保存文件
                    file_path = os.path.join(self.download_folder, img_info['filename'])
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    # 更新状态为"完成"
                    self._update_tree_status(i, "完成")
                    success_count += 1
                    
                    self.log_message(f"下载完成 ({i+1}/{total_images}): {img_info['filename']}")
                    
                except Exception as e:
                    # 更新状态为"失败"
                    self._update_tree_status(i, "失败")
                    failed_count += 1
                    
                    self.log_message(f"下载失败 ({i+1}/{total_images}): {img_info['filename']} - {str(e)}")
                
                # 更新进度条
                self.progress.config(value=i+1)
                
                # 短暂延迟，避免过快请求
                time.sleep(0.5)
            
            self.log_message(f"下载完成！成功: {success_count}, 失败: {failed_count}")
            
            if success_count > 0:
                messagebox.showinfo("下载完成", f"图片下载完成！\n成功: {success_count}\n失败: {failed_count}\n保存位置: {self.download_folder}")
            
        except Exception as e:
            self.log_message(f"下载过程中发生错误: {str(e)}")
            messagebox.showerror("下载错误", f"下载过程中发生错误:\n{str(e)}")
            
        finally:
            self.download_btn.config(state=tk.NORMAL)
            self.progress.config(value=0)
            
    def _update_tree_status(self, index, status):
        """更新树形视图中的状态"""
        children = self.tree.get_children()
        if index < len(children):
            item_id = children[index]
            values = list(self.tree.item(item_id)['values'])
            values[3] = status  # 状态在第4列
            self.tree.item(item_id, values=values)
            
            # 更新数据
            self.image_urls[index]['status'] = status
            
    def show_all_urls(self):
        """显示所有找到的图片URL"""
        if not self.all_found_urls:
            messagebox.showinfo("信息", "没有找到任何图片URL")
            return
            
        # 创建新窗口显示所有URL
        urls_window = tk.Toplevel(self.root)
        urls_window.title(f"所有图片URL (共{len(self.all_found_urls)}个)")
        
        # 设置子窗口大小并居中显示
        window_width = 800
        window_height = 600
        
        # 获取屏幕尺寸
        screen_width = urls_window.winfo_screenwidth()
        screen_height = urls_window.winfo_screenheight()
        
        # 计算居中位置
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # 设置窗口大小和位置
        urls_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # 创建文本区域
        text_frame = ttk.Frame(urls_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建带滚动条的文本框
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=100, height=30)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 分类显示URL
        valid_urls = [url for _, url in [(i+1, img['url']) for i, img in enumerate(self.image_urls)]]
        filtered_urls = [url for url in self.all_found_urls if url not in valid_urls]
        
        # 显示有效图片
        text_widget.insert(tk.END, "=== 有效图片 (将被下载) ===")
        text_widget.insert(tk.END, f" 共{len(valid_urls)}个\n\n")
        for i, url in enumerate(valid_urls, 1):
            text_widget.insert(tk.END, f"{i:3d}. {url}\n")
            
        text_widget.insert(tk.END, "\n\n")
        
        # 显示被过滤的图片
        text_widget.insert(tk.END, "=== 被过滤的图片 ===")
        text_widget.insert(tk.END, f" 共{len(filtered_urls)}个\n\n")
        for i, url in enumerate(filtered_urls, 1):
            text_widget.insert(tk.END, f"{i:3d}. {url}\n")
            
        # 设置为只读
        text_widget.config(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = ttk.Frame(urls_window, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="关闭", command=urls_window.destroy).pack(side=tk.RIGHT)

def main():
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用程序
    app = ImageScraperGUI(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()