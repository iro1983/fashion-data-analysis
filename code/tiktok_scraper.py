#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok热销服装数据抓取脚本
基于docs/tiktok_data_research.md调研结果开发

主要功能：
1. 多渠道数据获取（TikHub API + 网页爬虫）
2. 热门服装标签搜索与视频分析
3. 商品链接提取与验证
4. 数据去重和分类
5. 合规性检查与错误处理

作者：数据抓取系统
版本：1.0
日期：2025-11-14
"""

import json
import logging
import os
import time
import re
import hashlib
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, parse_qs
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import cv2
import numpy as np
from PIL import Image
import pytesseract

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TikTokVideo:
    """TikTok视频数据结构"""
    video_id: str
    title: str
    description: str
    author: str
    author_id: str
    author_followers: int
    author_following: int
    likes: int
    comments: int
    shares: int
    views: int
    hashtags: List[str]
    music_info: str
    product_links: List[str]
    product_images: List[str]
    upload_time: str
    region: str
    language: str
    scraped_at: str
    source: str  # 'tikhub_api', 'web_scraper', 'manual'
    data_hash: str  # 用于去重
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.data_hash:
            # 生成数据哈希用于去重
            content = f"{self.video_id}{self.title}{self.description}"
            self.data_hash = hashlib.md5(content.encode()).hexdigest()

@dataclass
class ScrapingConfig:
    """抓取配置"""
    # TikHub API配置
    tiktok_api_key: str = ""
    tiktok_api_url: str = "https://api.tikhub.io"
    
    # 爬虫配置
    use_proxy: bool = False
    proxy_list: List[str] = None
    request_delay: float = 2.0  # 请求间隔(秒)
    max_retries: int = 3
    timeout: int = 30
    
    # 目标数据配置
    target_hashtags: List[str] = None
    target_languages: List[str] = None
    target_regions: List[str] = None
    
    # 数据库配置
    database_path: str = "tiktok_clothing_data.db"
    
    # OCR配置
    enable_ocr: bool = False
    ocr_languages: str = "eng+chi_sim"
    
    def __post_init__(self):
        if self.target_hashtags is None:
            self.target_hashtags = [
                "#tshirt", "#hoodie", "#sweatshirt", "#pullover", 
                "#dress", "#top", "#blouse", "#shirt",
                "#pants", "#jeans", "#shorts", "#skirt",
                "#jacket", "#coat", "#sweater", "#cardigan",
                "#clothing", "#fashion", "#ootd", "#style"
            ]
        
        if self.target_languages is None:
            self.target_languages = ["en", "zh", "es", "fr", "de", "ja", "ko"]
            
        if self.target_regions is None:
            self.target_regions = ["US", "UK", "CA", "AU", "DE", "FR", "JP", "KR"]

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_id TEXT UNIQUE,
                        title TEXT,
                        description TEXT,
                        author TEXT,
                        author_id TEXT,
                        author_followers INTEGER,
                        author_following INTEGER,
                        likes INTEGER,
                        comments INTEGER,
                        shares INTEGER,
                        views INTEGER,
                        hashtags TEXT, -- JSON
                        music_info TEXT,
                        product_links TEXT, -- JSON
                        product_images TEXT, -- JSON
                        upload_time TEXT,
                        region TEXT,
                        language TEXT,
                        scraped_at TEXT,
                        source TEXT,
                        data_hash TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scraping_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        source TEXT,
                        operation TEXT,
                        status TEXT,
                        details TEXT,
                        items_processed INTEGER,
                        errors_count INTEGER,
                        duration_seconds REAL
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS product_extractions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_id TEXT,
                        extracted_url TEXT,
                        url_type TEXT,  -- 'shop_link', 'product_link', 'affiliate_link'
                        is_valid BOOLEAN,
                        platform TEXT,
                        confidence_score REAL,
                        extracted_at TEXT,
                        FOREIGN KEY (video_id) REFERENCES videos (video_id)
                    )
                """)
                
                conn.commit()
                logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_video(self, video: TikTokVideo) -> bool:
        """保存视频数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO videos 
                    (video_id, title, description, author, author_id, author_followers, 
                     author_following, likes, comments, shares, views, hashtags, 
                     music_info, product_links, product_images, upload_time, region, 
                     language, scraped_at, source, data_hash, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    video.video_id, video.title, video.description, video.author,
                    video.author_id, video.author_followers, video.author_following,
                    video.likes, video.comments, video.shares, video.views,
                    json.dumps(video.hashtags), video.music_info,
                    json.dumps(video.product_links), json.dumps(video.product_images),
                    video.upload_time, video.region, video.language, video.scraped_at,
                    video.source, video.data_hash
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"保存视频数据失败: {e}")
            return False
    
    def check_duplicate(self, data_hash: str) -> bool:
        """检查数据是否重复"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM videos WHERE data_hash = ?", (data_hash,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"检查重复数据失败: {e}")
            return False
    
    def log_operation(self, source: str, operation: str, status: str, 
                     details: str = "", items_processed: int = 0, 
                     errors_count: int = 0, duration_seconds: float = 0):
        """记录操作日志"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO scraping_logs 
                    (timestamp, source, operation, status, details, items_processed, 
                     errors_count, duration_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(), source, operation, status,
                    details, items_processed, errors_count, duration_seconds
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")

class TikHubAPIClient:
    """TikHub API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.tikhub.io"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'TikTok-Scraper/1.0'
        })
    
    def search_videos_by_hashtag(self, hashtag: str, max_results: int = 100) -> List[Dict]:
        """根据标签搜索视频"""
        videos = []
        try:
            params = {
                'platform': 'tiktok',
                'type': 'search',
                'keyword': hashtag,
                'content_type': 'video',
                'limit': min(max_results, 50),
                'sort_by': 'popularity'
            }
            
            response = self.session.get(f"{self.base_url}/search", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                videos_data = data['data'].get('videos', [])
                for video_data in videos_data:
                    videos.append(self._parse_video_data(video_data))
                    
            logger.info(f"TikHub API: 成功获取 {len(videos)} 个视频 (标签: {hashtag})")
            
        except Exception as e:
            logger.error(f"TikHub API 搜索失败: {e}")
            
        return videos
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """获取视频详情"""
        try:
            params = {
                'platform': 'tiktok',
                'type': 'video_detail',
                'video_id': video_id
            }
            
            response = self.session.get(f"{self.base_url}/video", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                return self._parse_video_data(data['data'])
                
        except Exception as e:
            logger.error(f"获取视频详情失败 (ID: {video_id}): {e}")
            
        return None
    
    def get_trending_hashtags(self, region: str = "US") -> List[str]:
        """获取热门标签"""
        hashtags = []
        try:
            params = {
                'platform': 'tiktok',
                'type': 'trending_hashtags',
                'region': region,
                'limit': 50
            }
            
            response = self.session.get(f"{self.base_url}/trending", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                hashtags = [item['hashtag'] for item in data['data'].get('hashtags', [])]
                
        except Exception as e:
            logger.error(f"获取热门标签失败: {e}")
            
        return hashtags
    
    def _parse_video_data(self, raw_data: Dict) -> Dict:
        """解析视频数据"""
        try:
            # 提取产品链接
            product_links = self._extract_product_links(raw_data.get('description', '') + ' ' + raw_data.get('title', ''))
            
            return {
                'video_id': raw_data.get('id', ''),
                'title': raw_data.get('desc', ''),
                'description': raw_data.get('desc', ''),
                'author': raw_data.get('author', {}).get('nickname', ''),
                'author_id': raw_data.get('author', {}).get('unique_id', ''),
                'author_followers': raw_data.get('author', {}).get('follower_count', 0),
                'author_following': raw_data.get('author', {}).get('following_count', 0),
                'likes': raw_data.get('stats', {}).get('digg_count', 0),
                'comments': raw_data.get('stats', {}).get('comment_count', 0),
                'shares': raw_data.get('stats', {}).get('share_count', 0),
                'views': raw_data.get('stats', {}).get('play_count', 0),
                'hashtags': self._extract_hashtags(raw_data.get('desc', '')),
                'music_info': raw_data.get('music', {}).get('title', ''),
                'product_links': product_links,
                'upload_time': raw_data.get('create_time', ''),
                'region': raw_data.get('region', 'US'),
                'language': raw_data.get('language', 'en'),
                'source': 'tikhub_api'
            }
        except Exception as e:
            logger.error(f"解析视频数据失败: {e}")
            return {}
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """从文本中提取标签"""
        hashtags = re.findall(r'#\w+', text)
        return list(set(hashtags))
    
    def _extract_product_links(self, text: str) -> List[str]:
        """从文本中提取产品链接"""
        # 常见电商平台链接模式
        patterns = [
            r'https?://(?:www\.)?amazon\.com/[^\s]+',
            r'https?://(?:www\.)?ebay\.com/[^\s]+',
            r'https?://(?:www\.)?shopify\.com/[^\s]+',
            r'https?://(?:www\.)?etsy\.com/[^\s]+',
            r'https?://(?:www\.)?aliexpress\.com/[^\s]+',
            r'https?://(?:www\.)?temu\.com/[^\s]+',
            r'https?://(?:www\.)?shein\.com/[^\s]+',
            r'bit\.ly/[^\s]+',  # 短链接
            r'tinyurl\.com/[^\s]+',
            r'cutt\.ly/[^\s]+'
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            links.extend(matches)
            
        return list(set(links))

class WebScraper:
    """网页爬虫"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.driver = None
        self.init_browser()
    
    def init_browser(self):
        """初始化浏览器"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            if self.config.use_proxy and self.config.proxy_list:
                proxy = random.choice(self.config.proxy_list)
                chrome_options.add_argument(f'--proxy-server={proxy}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.config.timeout)
            logger.info("浏览器初始化成功")
            
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise
    
    def search_tiktok_hashtag(self, hashtag: str, max_results: int = 50) -> List[Dict]:
        """在TikTok网页版搜索标签"""
        videos = []
        try:
            # 访问TikTok搜索页面
            search_url = f"https://www.tiktok.com/search?q={hashtag.replace('#', '')}"
            self.driver.get(search_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='search-video-container']"))
            )
            
            # 滚动加载更多视频
            self._load_more_videos(max_results)
            
            # 提取视频信息
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-e2e='search-video-item']")
            
            for element in video_elements[:max_results]:
                try:
                    video_data = self._extract_video_data_from_element(element)
                    if video_data and video_data.get('video_id'):
                        videos.append(video_data)
                except Exception as e:
                    logger.warning(f"提取视频数据失败: {e}")
                    continue
            
            logger.info(f"网页爬虫: 成功获取 {len(videos)} 个视频 (标签: {hashtag})")
            
        except Exception as e:
            logger.error(f"网页爬虫搜索失败: {e}")
            
        return videos
    
    def _load_more_videos(self, target_count: int):
        """加载更多视频"""
        current_count = 0
        max_scrolls = 20
        
        for _ in range(max_scrolls):
            if current_count >= target_count:
                break
                
            # 滚动页面
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 3))  # 随机等待
            
            # 检查是否有新内容加载
            new_videos = self.driver.find_elements(By.CSS_SELECTOR, "[data-e2e='search-video-item']")
            current_count = len(new_videos)
    
    def _extract_video_data_from_element(self, element) -> Dict:
        """从页面元素提取视频数据"""
        try:
            # 基本信息
            title = element.find_element(By.CSS_SELECTOR, "[data-e2e='search-video-desc']").text
            author = element.find_element(By.CSS_SELECTOR, "[data-e2e='search-video-author']").text
            
            # 统计数据
            stats_text = element.find_element(By.CSS_SELECTOR, "[data-e2e='search-video-stats']").text
            
            # 解析统计数据
            likes = self._parse_count(stats_text, 'like')
            comments = self._parse_count(stats_text, 'comment')
            shares = self._parse_count(stats_text, 'share')
            
            # 生成唯一ID（基于URL和标题）
            video_id = hashlib.md5(f"{title}{author}".encode()).hexdigest()[:16]
            
            # 提取产品链接
            product_links = self._extract_product_links(title)
            
            return {
                'video_id': video_id,
                'title': title,
                'description': title,  # 网页版描述和标题通常相同
                'author': author,
                'author_id': '',
                'author_followers': 0,
                'author_following': 0,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'views': 0,
                'hashtags': self._extract_hashtags(title),
                'music_info': '',
                'product_links': product_links,
                'upload_time': datetime.now().isoformat(),
                'region': 'US',
                'language': 'en',
                'source': 'web_scraper'
            }
            
        except Exception as e:
            logger.warning(f"提取视频元素数据失败: {e}")
            return {}
    
    def _parse_count(self, stats_text: str, metric_type: str) -> int:
        """解析数量统计"""
        patterns = {
            'like': r'(\d+(?:\.\d+)?[KMB]?)(\s*)like',
            'comment': r'(\d+(?:\.\d+)?[KMB]?)(\s*)comment',
            'share': r'(\d+(?:\.\d+)?[KMB]?)(\s*)share'
        }
        
        pattern = patterns.get(metric_type, '')
        match = re.search(pattern, stats_text.lower())
        
        if match:
            count_str = match.group(1)
            return self._convert_count_string(count_str)
        
        return 0
    
    def _convert_count_string(self, count_str: str) -> int:
        """转换数量字符串为整数"""
        count_str = count_str.upper()
        if count_str.endswith('K'):
            return int(float(count_str[:-1]) * 1000)
        elif count_str.endswith('M'):
            return int(float(count_str[:-1]) * 1000000)
        elif count_str.endswith('B'):
            return int(float(count_str[:-1]) * 1000000000)
        else:
            return int(float(count_str))
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """提取标签"""
        hashtags = re.findall(r'#\w+', text)
        return list(set(hashtags))
    
    def _extract_product_links(self, text: str) -> List[str]:
        """提取产品链接"""
        # 复用TikHub客户端的链接提取逻辑
        patterns = [
            r'https?://(?:www\.)?amazon\.com/[^\s]+',
            r'https?://(?:www\.)?ebay\.com/[^\s]+',
            r'https?://(?:www\.)?shopify\.com/[^\s]+',
            r'https?://(?:www\.)?etsy\.com/[^\s]+',
            r'https?://(?:www\.)?aliexpress\.com/[^\s]+',
            r'https?://(?:www\.)?temu\.com/[^\s]+',
            r'https?://(?:www\.)?shein\.com/[^\s]+',
            r'bit\.ly/[^\s]+',
            r'tinyurl\.com/[^\s]+',
            r'cutt\.ly/[^\s]+'
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            links.extend(matches)
            
        return list(set(links))
    
    def extract_product_images(self, video_url: str) -> List[str]:
        """从视频中提取商品图片（OCR）"""
        if not self.config.enable_ocr:
            return []
            
        try:
            self.driver.get(video_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # 截图并使用OCR识别产品图片
            image_urls = []
            
            # 滚动页面寻找产品图片
            for i in range(5):
                self.driver.execute_script("window.scrollTo(0, window.scrollY + 500);")
                time.sleep(1)
                
                # 查找图片元素
                images = self.driver.find_elements(By.TAG_NAME, "img")
                for img in images:
                    src = img.get_attribute("src")
                    if src and any(platform in src.lower() for platform in 
                                 ['amazon', 'shopify', 'etsy', 'ebay']):
                        image_urls.append(src)
            
            return list(set(image_urls))
            
        except Exception as e:
            logger.error(f"提取商品图片失败: {e}")
            return []
    
    def __del__(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

class ProductLinkValidator:
    """产品链接验证器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def validate_link(self, url: str) -> Dict:
        """验证链接有效性"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            return {
                'url': url,
                'is_valid': response.status_code < 400,
                'status_code': response.status_code,
                'final_url': response.url,
                'content_type': response.headers.get('content-type', ''),
                'platform': self._detect_platform(url),
                'confidence_score': self._calculate_confidence(response)
            }
        except Exception as e:
            return {
                'url': url,
                'is_valid': False,
                'status_code': 0,
                'final_url': url,
                'content_type': '',
                'platform': 'unknown',
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def _detect_platform(self, url: str) -> str:
        """检测电商平台"""
        url_lower = url.lower()
        if 'amazon.' in url_lower:
            return 'amazon'
        elif 'ebay.' in url_lower:
            return 'ebay'
        elif 'shopify.' in url_lower:
            return 'shopify'
        elif 'etsy.' in url_lower:
            return 'etsy'
        elif 'aliexpress.' in url_lower:
            return 'aliexpress'
        elif 'temu.' in url_lower:
            return 'temu'
        elif 'shein.' in url_lower:
            return 'shein'
        else:
            return 'other'
    
    def _calculate_confidence(self, response) -> float:
        """计算置信度分数"""
        score = 0.0
        
        # 状态码评分
        if response.status_code == 200:
            score += 0.3
        elif 200 <= response.status_code < 400:
            score += 0.2
        
        # 内容类型评分
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            score += 0.2
        elif 'image' in content_type:
            score += 0.15
        
        # 平台评分
        url_lower = response.url.lower()
        if any(platform in url_lower for platform in ['amazon', 'ebay', 'shopify']):
            score += 0.3
        
        return min(score, 1.0)
    
    def batch_validate(self, urls: List[str], max_workers: int = 10) -> List[Dict]:
        """批量验证链接"""
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.validate_link, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                try:
                    result = future.result(timeout=15)
                    results.append(result)
                except Exception as e:
                    url = future_to_url[future]
                    results.append({
                        'url': url,
                        'is_valid': False,
                        'status_code': 0,
                        'platform': 'unknown',
                        'confidence_score': 0.0,
                        'error': str(e)
                    })
        
        return results

class TikTokClothingScraper:
    """TikTok服装数据抓取器主类"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.db_manager = DatabaseManager(config.database_path)
        
        # 初始化组件
        self.tikhub_client = None
        self.web_scraper = None
        self.link_validator = ProductLinkValidator()
        
        if config.tiktok_api_key:
            self.tikhub_client = TikHubAPIClient(config.tiktok_api_key)
        
        self.web_scraper = WebScraper(config)
    
    def scrape_clothing_videos(self, target_sources: List[str] = None, 
                             max_videos_per_tag: int = 100) -> Dict:
        """抓取服装相关视频数据"""
        if target_sources is None:
            target_sources = ['tikhub_api', 'web_scraper']
        
        start_time = time.time()
        total_processed = 0
        total_errors = 0
        all_videos = []
        
        logger.info(f"开始抓取TikTok服装视频数据，源: {target_sources}")
        
        for hashtag in self.config.target_hashtags:
            logger.info(f"处理标签: {hashtag}")
            tag_videos = []
            tag_errors = 0
            
            # TikHub API抓取
            if 'tikhub_api' in target_sources and self.tikhub_client:
                try:
                    api_videos = self.tikhub_client.search_videos_by_hashtag(
                        hashtag, max_videos_per_tag // 2
                    )
                    tag_videos.extend(api_videos)
                    logger.info(f"API获取 {len(api_videos)} 个视频")
                except Exception as e:
                    logger.error(f"TikHub API抓取失败: {e}")
                    tag_errors += 1
            
            # 网页爬虫抓取
            if 'web_scraper' in target_sources:
                try:
                    web_videos = self.web_scraper.search_tiktok_hashtag(
                        hashtag, max_videos_per_tag // 2
                    )
                    tag_videos.extend(web_videos)
                    logger.info(f"网页爬虫获取 {len(web_videos)} 个视频")
                except Exception as e:
                    logger.error(f"网页爬虫抓取失败: {e}")
                    tag_errors += 1
            
            # 数据处理和存储
            for video_data in tag_videos:
                try:
                    if video_data:
                        video = TikTokVideo(
                            scraped_at=datetime.now().isoformat(),
                            **video_data
                        )
                        
                        # 检查重复
                        if not self.db_manager.check_duplicate(video.data_hash):
                            if self.db_manager.save_video(video):
                                all_videos.append(video)
                                total_processed += 1
                            
                            # 延迟请求
                            time.sleep(self.config.request_delay)
                        else:
                            logger.debug(f"跳过重复视频: {video.video_id}")
                            
                except Exception as e:
                    logger.error(f"处理视频数据失败: {e}")
                    total_errors += 1
                    tag_errors += 1
            
            # 记录该标签的处理日志
            self.db_manager.log_operation(
                source="combined",
                operation=f"scrape_hashtag_{hashtag}",
                status="completed" if tag_errors == 0 else "completed_with_errors",
                details=f"Processed hashtag: {hashtag}",
                items_processed=len(tag_videos),
                errors_count=tag_errors
            )
        
        # 记录总体操作日志
        duration = time.time() - start_time
        self.db_manager.log_operation(
            source="combined",
            operation="scrape_clothing_videos",
            status="completed" if total_errors == 0 else "completed_with_errors",
            details=f"Scraped clothing videos across {len(self.config.target_hashtags)} hashtags",
            items_processed=total_processed,
            errors_count=total_errors,
            duration_seconds=duration
        )
        
        return {
            'total_videos': total_processed,
            'total_errors': total_errors,
            'duration_seconds': duration,
            'videos': [asdict(video) for video in all_videos]
        }
    
    def validate_product_links(self, videos: List[TikTokVideo] = None) -> Dict:
        """验证产品链接"""
        if videos is None:
            # 从数据库获取最新的视频数据
            videos = self._get_recent_videos()
        
        all_links = []
        for video in videos:
            all_links.extend(video.product_links)
        
        # 去重
        unique_links = list(set(all_links))
        logger.info(f"开始验证 {len(unique_links)} 个产品链接")
        
        validation_results = self.link_validator.batch_validate(unique_links)
        
        # 统计结果
        valid_count = sum(1 for r in validation_results if r['is_valid'])
        invalid_count = len(validation_results) - valid_count
        
        platform_stats = {}
        for result in validation_results:
            platform = result['platform']
            if platform not in platform_stats:
                platform_stats[platform] = {'total': 0, 'valid': 0}
            platform_stats[platform]['total'] += 1
            if result['is_valid']:
                platform_stats[platform]['valid'] += 1
        
        logger.info(f"链接验证完成: 有效 {valid_count}, 无效 {invalid_count}")
        
        return {
            'total_links': len(unique_links),
            'valid_links': valid_count,
            'invalid_links': invalid_count,
            'validation_rate': valid_count / len(unique_links) if unique_links else 0,
            'platform_stats': platform_stats,
            'detailed_results': validation_results
        }
    
    def extract_trending_fashion(self, region: str = "US") -> Dict:
        """提取时尚趋势数据"""
        if not self.tikhub_client:
            return {'error': 'TikHub API未配置'}
        
        try:
            # 获取热门标签
            trending_hashtags = self.tikhub_client.get_trending_hashtags(region)
            
            # 筛选时尚相关标签
            fashion_hashtags = []
            fashion_keywords = ['fashion', 'style', 'ootd', 'cloth', 'wear', 'outfit', 'trend']
            
            for tag in trending_hashtags:
                if any(keyword in tag.lower() for keyword in fashion_keywords):
                    fashion_hashtags.append(tag)
            
            logger.info(f"获取到 {len(fashion_hashtags)} 个时尚趋势标签")
            
            return {
                'region': region,
                'trending_fashion_hashtags': fashion_hashtags,
                'total_trending': len(trending_hashtags),
                'fashion_count': len(fashion_hashtags),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"提取时尚趋势失败: {e}")
            return {'error': str(e)}
    
    def _get_recent_videos(self, hours: int = 24) -> List[TikTokVideo]:
        """获取最近的视频数据"""
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM videos 
                    WHERE scraped_at > datetime('now', '-{} hours')
                    ORDER BY scraped_at DESC
                """.format(hours))
                
                rows = cursor.fetchall()
                videos = []
                
                for row in rows:
                    # 转换数据库行为TikTokVideo对象
                    # 这里需要根据实际的列顺序来映射
                    video_dict = {
                        'video_id': row[1],
                        'title': row[2],
                        'description': row[3],
                        'author': row[4],
                        'author_id': row[5],
                        'author_followers': row[6],
                        'author_following': row[7],
                        'likes': row[8],
                        'comments': row[9],
                        'shares': row[10],
                        'views': row[11],
                        'hashtags': json.loads(row[12]) if row[12] else [],
                        'music_info': row[13],
                        'product_links': json.loads(row[14]) if row[14] else [],
                        'product_images': json.loads(row[15]) if row[15] else [],
                        'upload_time': row[16],
                        'region': row[17],
                        'language': row[18],
                        'scraped_at': row[19],
                        'source': row[20],
                        'data_hash': row[21]
                    }
                    videos.append(TikTokVideo(**video_dict))
                
                return videos
                
        except Exception as e:
            logger.error(f"获取最近视频数据失败: {e}")
            return []
    
    def get_scraping_statistics(self) -> Dict:
        """获取抓取统计信息"""
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                
                # 基本统计
                cursor.execute("SELECT COUNT(*) FROM videos")
                total_videos = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM videos WHERE date(scraped_at) = date('now')")
                today_videos = cursor.fetchone()[0]
                
                # 来源统计
                cursor.execute("""
                    SELECT source, COUNT(*) as count 
                    FROM videos 
                    GROUP BY source 
                    ORDER BY count DESC
                """)
                source_stats = dict(cursor.fetchall())
                
                # 标签统计
                cursor.execute("""
                    SELECT hashtags, COUNT(*) as count 
                    FROM videos 
                    GROUP BY hashtags 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                hashtag_rows = cursor.fetchall()
                hashtag_stats = {}
                for row in hashtag_rows:
                    try:
                        hashtags = json.loads(row[0]) if row[0] else []
                        for tag in hashtags:
                            hashtag_stats[tag] = hashtag_stats.get(tag, 0) + row[1]
                    except:
                        continue
                
                # 产品链接统计
                cursor.execute("SELECT COUNT(*) FROM product_extractions WHERE is_valid = 1")
                valid_product_links = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM product_extractions")
                total_product_links = cursor.fetchone()[0]
                
                # 最近操作日志
                cursor.execute("""
                    SELECT * FROM scraping_logs 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """)
                recent_logs = cursor.fetchall()
                
                return {
                    'total_videos': total_videos,
                    'today_videos': today_videos,
                    'source_distribution': source_stats,
                    'top_hashtags': dict(sorted(hashtag_stats.items(), 
                                              key=lambda x: x[1], reverse=True)[:10]),
                    'product_links': {
                        'total': total_product_links,
                        'valid': valid_product_links,
                        'validation_rate': valid_product_links / total_product_links if total_product_links > 0 else 0
                    },
                    'recent_operations': recent_logs
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {'error': str(e)}

def main():
    """主函数"""
    # 示例配置
    config = ScrapingConfig(
        tiktok_api_key="your_tikhub_api_key_here",
        use_proxy=False,
        request_delay=2.0,
        max_retries=3,
        enable_ocr=False
    )
    
    # 创建抓取器实例
    scraper = TikTokClothingScraper(config)
    
    # 示例用法
    try:
        # 1. 抓取服装视频数据
        logger.info("开始抓取服装视频数据...")
        results = scraper.scrape_clothing_videos(
            target_sources=['tikhub_api', 'web_scraper'],
            max_videos_per_tag=50
        )
        print(f"抓取完成: 处理了 {results['total_videos']} 个视频")
        
        # 2. 验证产品链接
        logger.info("验证产品链接...")
        validation_results = scraper.validate_product_links()
        print(f"链接验证: {validation_results['valid_links']}/{validation_results['total_links']} 有效")
        
        # 3. 提取时尚趋势
        logger.info("提取时尚趋势...")
        trending = scraper.extract_trending_fashion("US")
        if 'error' not in trending:
            print(f"时尚趋势标签: {len(trending['trending_fashion_hashtags'])} 个")
        
        # 4. 获取统计信息
        stats = scraper.get_scraping_statistics()
        print(f"数据统计: 总共 {stats.get('total_videos', 0)} 个视频")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
    finally:
        # 清理资源
        if hasattr(scraper, 'web_scraper'):
            del scraper.web_scraper

if __name__ == "__main__":
    main()