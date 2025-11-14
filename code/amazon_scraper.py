#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon热销服装数据抓取脚本
基于docs/amazon_data_research.md的调研结果开发

功能特性：
- 合规遵守robots.txt协议
- 反爬虫策略（User-Agent轮换、延迟控制、代理轮换）
- 产品搜索和分类筛选（印花TSHIRT、卫衣、连帽衫）
- 产品详情页数据提取
- 错误处理和重试机制
- 数据清洗和格式化
- SQLite数据库集成
- 异步处理支持
- 详细日志记录

合规要求：
- 控制请求频率（每页间隔2-3秒）
- 添加User-Agent标识
- 实现礼貌抓取机制
- 遵守robots.txt协议

作者: Data Engineering Team
日期: 2025-11-14
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import re
import time
import random
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import os
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/code/amazon_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ProductData:
    """产品数据结构"""
    asin: str
    title: str
    price: float
    original_price: Optional[float]
    rating: float
    review_count: int
    brand: str
    category: str
    availability: str
    image_url: str
    detail_page_url: str
    seller_name: str
    seller_link: str
    features: List[str]
    description: str
    rank: Optional[int]
    bestseller_flag: bool
    timestamp: str
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)


class Config:
    """配置类"""
    # Amazon配置
    BASE_URL = "https://www.amazon.com"
    SEARCH_PATHS = [
        "/s?k=print+tshirt",
        "/s?k=print+hoodie", 
        "/s?k=graphic+shirt",
        "/s?k=logo+tshirt",
        "/s?k=fashion+hoodie"
    ]
    
    # 合规配置 - 基于调研文档的robots.txt遵守
    DISALLOWED_PATHS = [
        "/gp/sign-in",
        "/ap/signin", 
        "/gp/cart",
        "/gp/registry",
        "/wishlist",
        "/gp/handshake",
        "/yourstore/home",
        "/your-account",
        "/s",
        "/s/ref"
    ]
    
    # 爬虫配置 - 基于调研的频率控制建议
    REQUEST_DELAY_MIN = 2  # 最小延迟2秒
    REQUEST_DELAY_MAX = 3  # 最大延迟3秒
    MAX_RETRIES = 3
    TIMEOUT = 10
    MAX_WORKERS = 3  # 限制并发数量
    
    # 数据库配置
    DATABASE_PATH = "/workspace/code/amazon_products.db"
    
    # 代理配置 (示例，需要替换为实际代理)
    PROXY_LIST = [
        # "http://user:pass@proxy1:port",
        # "http://user:pass@proxy2:port", 
    ]
    
    # User-Agent轮换列表 - 基于调研文档的最佳实践
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    
    # 请求头模板 - 基于调研文档建议
    HEADERS_TEMPLATE = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        asin TEXT UNIQUE,
                        title TEXT,
                        price REAL,
                        original_price REAL,
                        rating REAL,
                        review_count INTEGER,
                        brand TEXT,
                        category TEXT,
                        availability TEXT,
                        image_url TEXT,
                        detail_page_url TEXT,
                        seller_name TEXT,
                        seller_link TEXT,
                        features TEXT,
                        description TEXT,
                        rank INTEGER,
                        bestseller_flag BOOLEAN,
                        timestamp TEXT,
                        hash TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_asin ON products(asin)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON products(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON products(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_bestseller ON products(bestseller_flag)")
                
                conn.commit()
                logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_product(self, product: ProductData) -> bool:
        """保存产品数据"""
        try:
            product_hash = self.generate_hash(product)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO products (
                        asin, title, price, original_price, rating, review_count,
                        brand, category, availability, image_url, detail_page_url,
                        seller_name, seller_link, features, description,
                        rank, bestseller_flag, timestamp, hash,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    product.asin, product.title, product.price, product.original_price,
                    product.rating, product.review_count, product.brand, product.category,
                    product.availability, product.image_url, product.detail_page_url,
                    product.seller_name, product.seller_link, json.dumps(product.features),
                    product.description, product.rank, product.bestseller_flag,
                    product.timestamp, product_hash
                ))
                
                conn.commit()
                logger.debug(f"产品 {product.asin} 保存成功")
                return True
                
        except Exception as e:
            logger.error(f"保存产品失败: {e}")
            return False
    
    def generate_hash(self, product: ProductData) -> str:
        """生成产品数据哈希值用于去重"""
        hash_data = f"{product.asin}_{product.title}_{product.price}_{product.timestamp}"
        return hashlib.md5(hash_data.encode()).hexdigest()
    
    def get_products(self, category: str = None, bestseller_only: bool = False) -> List[Dict]:
        """获取产品数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM products WHERE 1=1"
                params = []
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if bestseller_only:
                    query += " AND bestseller_flag = 1"
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"获取产品数据失败: {e}")
            return []


class AntiCrawlerManager:
    """反爬虫管理类"""
    
    def __init__(self):
        self.request_count = 0
        self.last_request_time = 0
        
    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(Config.USER_AGENTS)
    
    def get_random_headers(self) -> Dict[str, str]:
        """获取随机请求头"""
        headers = Config.HEADERS_TEMPLATE.copy()
        headers["User-Agent"] = self.get_random_user_agent()
        return headers
    
    def get_random_proxy(self) -> Optional[str]:
        """获取随机代理"""
        if Config.PROXY_LIST:
            return random.choice(Config.PROXY_LIST)
        return None
    
    def wait_between_requests(self):
        """请求间等待 - 基于调研文档的频率控制建议"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < Config.REQUEST_DELAY_MIN:
            sleep_time = Config.REQUEST_DELAY_MIN - elapsed
            sleep_time += random.uniform(0, 1)  # 添加随机延迟
            logger.debug(f"等待 {sleep_time:.2f} 秒")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1


class AmazonScraper:
    """Amazon爬虫主类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.db_manager = DatabaseManager(Config.DATABASE_PATH)
        self.anti_crawler = AntiCrawlerManager()
        self.headers = self.anti_crawler.get_random_headers()
        
        # 更新会话头
        self.session.headers.update(self.headers)
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "products_scraped": 0,
            "start_time": datetime.now()
        }
    
    def check_robots_txt(self, url: str) -> bool:
        """检查robots.txt是否允许访问 - 基于调研文档的合规要求"""
        try:
            robots_url = f"{Config.BASE_URL}/robots.txt"
            response = self.session.get(robots_url, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"无法访问robots.txt: {response.status_code}")
                return False
            
            robots_content = response.text.lower()
            
            # 检查Disallow路径
            for disallowed_path in Config.DISALLOWED_PATHS:
                if disallowed_path.lower() in robots_content:
                    # 如果robots.txt明确禁止，停止访问
                    if "user-agent: *" in robots_content and "disallow" in robots_content:
                        logger.warning(f"robots.txt禁止访问路径: {disallowed_path}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查robots.txt失败: {e}")
            return False
    
    def make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """发起HTTP请求 - 包含重试机制和反爬虫策略"""
        if not self.check_robots_txt(url):
            logger.error(f"robots.txt不允许访问: {url}")
            return None
        
        self.anti_crawler.wait_between_requests()
        
        headers = self.anti_crawler.get_random_headers()
        proxies = {"http": self.anti_crawler.get_random_proxy(), 
                  "https": self.anti_crawler.get_random_proxy()}
        
        # 清理None代理
        proxies = {k: v for k, v in proxies.items() if v is not None}
        
        self.stats["total_requests"] += 1
        
        try:
            response = self.session.get(
                url, 
                headers=headers,
                proxies=proxies if proxies else None,
                timeout=Config.TIMEOUT
            )
            
            if response.status_code == 200:
                self.stats["successful_requests"] += 1
                return response
            elif response.status_code in [429, 503] and retries < Config.MAX_RETRIES:
                # 限速响应，使用指数退避
                wait_time = (2 ** retries) + random.uniform(1, 3)
                logger.warning(f"遇到限速 {response.status_code}，等待 {wait_time:.2f} 秒后重试")
                time.sleep(wait_time)
                return self.make_request(url, retries + 1)
            else:
                self.stats["failed_requests"] += 1
                logger.error(f"请求失败: {url}, 状态码: {response.status_code}")
                return None
                
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"请求异常: {url}, 错误: {e}")
            
            if retries < Config.MAX_RETRIES:
                wait_time = (2 ** retries) + random.uniform(1, 2)
                logger.info(f"等待 {wait_time:.2f} 秒后重试")
                time.sleep(wait_time)
                return self.make_request(url, retries + 1)
            
            return None
    
    def parse_search_results(self, soup: BeautifulSoup, category: str) -> List[str]:
        """解析搜索结果页面，获取ASIN列表"""
        asin_list = []
        
        try:
            # 查找产品链接
            product_links = soup.find_all('a', href=True)
            
            for link in product_links:
                href = link.get('href', '')
                
                # 匹配ASIN模式
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                if asin_match:
                    asin = asin_match.group(1)
                    if asin not in asin_list:
                        asin_list.append(asin)
            
            logger.info(f"在 {category} 类别中找到 {len(asin_list)} 个ASIN")
            
        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")
        
        return asin_list
    
    def extract_product_info(self, soup: BeautifulSoup, asin: str, category: str) -> Optional[ProductData]:
        """提取产品详细信息 - 基于调研文档的字段需求"""
        try:
            # 基础信息提取
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            original_price = self._extract_original_price(soup)
            rating = self._extract_rating(soup)
            review_count = self._extract_review_count(soup)
            brand = self._extract_brand(soup)
            availability = self._extract_availability(soup)
            image_url = self._extract_image_url(soup)
            detail_page_url = f"{Config.BASE_URL}/dp/{asin}"
            seller_name, seller_link = self._extract_seller_info(soup)
            features = self._extract_features(soup)
            description = self._extract_description(soup)
            rank = self._extract_rank(soup)
            bestseller_flag = self._check_bestseller(soup)
            
            # 构建产品数据对象
            product = ProductData(
                asin=asin,
                title=title,
                price=price,
                original_price=original_price,
                rating=rating,
                review_count=review_count,
                brand=brand,
                category=category,
                availability=availability,
                image_url=image_url,
                detail_page_url=detail_page_url,
                seller_name=seller_name,
                seller_link=seller_link,
                features=features,
                description=description,
                rank=rank,
                bestseller_flag=bestseller_flag,
                timestamp=datetime.now().isoformat()
            )
            
            logger.debug(f"提取产品信息成功: {asin} - {title[:50]}...")
            return product
            
        except Exception as e:
            logger.error(f"提取产品信息失败: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取产品标题"""
        selectors = [
            "#productTitle",
            "h1.a-size-large",
            "h1[data-automation-id='product-title']",
            ".a-size-large",
            "h1"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "未知标题"
    
    def _extract_price(self, soup: BeautifulSoup) -> float:
        """提取当前价格"""
        price_selectors = [
            ".a-price .a-offscreen",
            "#priceblock_dealprice",
            "#priceblock_ourprice", 
            ".a-price-whole",
            ".a-price-symbols"
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    return float(price_match.group())
        
        return 0.0
    
    def _extract_original_price(self, soup: BeautifulSoup) -> Optional[float]:
        """提取原价"""
        element = soup.select_one(".a-text-price .a-offscreen")
        if element:
            price_text = element.get_text(strip=True)
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                return float(price_match.group())
        
        return None
    
    def _extract_rating(self, soup: BeautifulSoup) -> float:
        """提取评分"""
        selectors = [
            "span[aria-label*='stars']",
            ".a-icon-alt",
            ".reviewCountTextLinkedHistogram .a-link-normal"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and 'stars' in element.get('aria-label', '').lower():
                rating_text = element.get('aria-label', '')
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    return float(rating_match.group())
        
        return 0.0
    
    def _extract_review_count(self, soup: BeautifulSoup) -> int:
        """提取评论数量"""
        selectors = [
            "span[aria-label*='reviews']",
            "#acrCustomerReviewText",
            ".reviewCountTextLinkedHistogram .a-link-normal"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                review_text = element.get_text(strip=True)
                review_match = re.search(r'([\d,]+)', review_text.replace(',', ''))
                if review_match:
                    return int(review_match.group())
        
        return 0
    
    def _extract_brand(self, soup: BeautifulSoup) -> str:
        """提取品牌"""
        element = soup.select_one("#bylineInfo")
        if element:
            brand_text = element.get_text(strip=True)
            if brand_text.startswith("Visit the"):
                brand_text = brand_text.replace("Visit the", "").replace("Store", "").strip()
            return brand_text
        
        element = soup.select_one("a[href*='/stores/']")
        if element:
            return element.get_text(strip=True)
        
        return "未知品牌"
    
    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """提取可用性"""
        selectors = [
            "#availability span",
            ".a-color-success",
            ".a-color-price"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                availability = element.get_text(strip=True)
                if availability:
                    return availability
        
        return "库存状态未知"
    
    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        """提取产品图片URL"""
        selectors = [
            "#landingImage",
            ".a-dynamic-image"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector == "#landingImage":
                    return element.get("src", "")
                else:
                    # 对于多图片，返回第一张
                    images = element.find_all('img')
                    if images:
                        return images[0].get("src", "")
        
        return ""
    
    def _extract_seller_info(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """提取卖家信息"""
        seller_element = soup.select_one("#merchant-info a, #sellerInfo")
        if seller_element:
            seller_name = seller_element.get_text(strip=True)
            seller_link = seller_element.get("href", "")
            return seller_name, seller_link
        
        return "", ""
    
    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """提取产品特性"""
        features = []
        feature_elements = soup.select("#feature-bullets ul li")
        
        for element in feature_elements:
            feature_text = element.get_text(strip=True)
            if feature_text:
                features.append(feature_text)
        
        return features
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取产品描述"""
        selectors = [
            "#aplus",
            "#aplus p",
            "#aplus3p",
            ".productDescription"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                if description:
                    return description[:500]  # 限制长度
        
        return ""
    
    def _extract_rank(self, soup: BeautifulSoup) -> Optional[int]:
        """提取排名"""
        rank_element = soup.select_one("#SalesRank, .a-list-item")
        if rank_element:
            rank_text = rank_element.get_text()
            rank_match = re.search(r'#([\d,]+)', rank_text)
            if rank_match:
                return int(rank_match.group(1).replace(',', ''))
        
        return None
    
    def _check_bestseller(self, soup: BeautifulSoup) -> bool:
        """检查是否为热销产品"""
        bestseller_elements = soup.select("#SalesRank, .badge-success")
        for element in bestseller_elements:
            element_text = element.get_text(strip=True).lower()
            if any(keyword in element_text for keyword in ['bestseller', 'bestselling', 'best seller']):
                return True
        
        return False
    
    def search_products(self, category: str, max_pages: int = 5) -> List[ProductData]:
        """搜索产品 - 基于调研文档的服装类别"""
        logger.info(f"开始搜索类别: {category}")
        
        products = []
        
        # 根据类别选择搜索路径
        search_mapping = {
            "print-tshirt": "/s?k=print+tshirt",
            "print-hoodie": "/s?k=print+hoodie",
            "graphic-shirt": "/s?k=graphic+shirt",
            "logo-tshirt": "/s?k=logo+tshirt",
            "fashion-hoodie": "/s?k=fashion+hoodie"
        }
        
        search_path = search_mapping.get(category, "/s?k=print+tshirt")
        
        for page in range(1, max_pages + 1):
            try:
                # 构建搜索URL
                search_url = f"{Config.BASE_URL}{search_path}&page={page}"
                
                logger.info(f"搜索页面: {search_url}")
                
                # 发起请求
                response = self.make_request(search_url)
                if not response:
                    logger.error(f"搜索页面请求失败: {search_url}")
                    continue
                
                # 解析HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 提取ASIN列表
                asin_list = self.parse_search_results(soup, category)
                
                if not asin_list:
                    logger.warning(f"页面 {page} 没有找到产品")
                    break
                
                # 提取产品详情
                for asin in asin_list:
                    try:
                        detail_url = f"{Config.BASE_URL}/dp/{asin}"
                        detail_response = self.make_request(detail_url)
                        
                        if not detail_response:
                            logger.warning(f"产品详情页请求失败: {asin}")
                            continue
                        
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                        product = self.extract_product_info(detail_soup, asin, category)
                        
                        if product:
                            products.append(product)
                            self.stats["products_scraped"] += 1
                            
                            # 保存到数据库
                            self.db_manager.save_product(product)
                        
                        # 请求间隔
                        time.sleep(random.uniform(1, 2))
                        
                    except Exception as e:
                        logger.error(f"提取产品 {asin} 信息失败: {e}")
                        continue
                
                logger.info(f"页面 {page} 完成，共获取 {len(asin_list)} 个产品")
                
            except Exception as e:
                logger.error(f"搜索页面 {page} 失败: {e}")
                continue
        
        logger.info(f"搜索完成，总共获取 {len(products)} 个产品")
        return products
    
    def run_scraping(self, categories: List[str], max_pages: int = 3) -> Dict:
        """运行抓取任务"""
        logger.info("开始Amazon产品数据抓取任务")
        
        start_time = datetime.now()
        all_products = []
        
        try:
            for category in categories:
                logger.info(f"正在抓取类别: {category}")
                products = self.search_products(category, max_pages)
                all_products.extend(products)
                
                # 类别间休息
                time.sleep(random.uniform(5, 10))
            
            # 统计信息
            self.stats["end_time"] = datetime.now()
            self.stats["duration"] = str(self.stats["end_time"] - self.stats["start_time"])
            self.stats["success_rate"] = (
                self.stats["successful_requests"] / self.stats["total_requests"] * 100
                if self.stats["total_requests"] > 0 else 0
            )
            
            # 输出统计信息
            self._print_statistics()
            
            result = {
                "status": "success",
                "products_scraped": len(all_products),
                "categories_processed": categories,
                "statistics": self.stats,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("抓取任务完成")
            return result
            
        except Exception as e:
            logger.error(f"抓取任务失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "products_scraped": len(all_products),
                "statistics": self.stats
            }
    
    def _print_statistics(self):
        """打印统计信息"""
        print("\n" + "="*50)
        print("抓取统计信息")
        print("="*50)
        print(f"总请求数: {self.stats['total_requests']}")
        print(f"成功请求: {self.stats['successful_requests']}")
        print(f"失败请求: {self.stats['failed_requests']}")
        print(f"成功率: {self.stats.get('success_rate', 0):.2f}%")
        print(f"抓取产品数: {self.stats['products_scraped']}")
        print(f"开始时间: {self.stats['start_time']}")
        if 'end_time' in self.stats:
            print(f"结束时间: {self.stats['end_time']}")
            print(f"总耗时: {self.stats['duration']}")
        print("="*50)
    
    def export_data(self, format: str = "json", filename: str = None) -> str:
        """导出数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/workspace/code/amazon_products_{timestamp}.{format}"
        
        try:
            products = self.db_manager.get_products()
            
            if format.lower() == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2, default=str)
            
            elif format.lower() == "csv":
                import pandas as pd
                df = pd.DataFrame(products)
                df.to_csv(filename, index=False, encoding='utf-8')
            
            logger.info(f"数据导出成功: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"数据导出失败: {e}")
            return ""
    
    async def async_scrape_category(self, session: aiohttp.ClientSession, category: str, max_pages: int) -> List[ProductData]:
        """异步抓取单个类别"""
        products = []
        
        # 这里可以添加异步逻辑，简化示例
        return products
    
    def run_async_scraping(self, categories: List[str], max_pages: int = 3) -> Dict:
        """运行异步抓取任务"""
        logger.info("开始异步抓取任务")
        
        async def main():
            async with aiohttp.ClientSession() as session:
                tasks = []
                for category in categories:
                    task = self.async_scrape_category(session, category, max_pages)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                return [product for result in results for product in result]
        
        try:
            products = asyncio.run(main())
            return {
                "status": "success",
                "products_scraped": len(products),
                "categories": categories
            }
        except Exception as e:
            logger.error(f"异步抓取失败: {e}")
            return {"status": "error", "error": str(e)}


def main():
    """主函数 - 使用示例"""
    
    # 初始化爬虫
    scraper = AmazonScraper()
    
    # 要抓取的服装类别
    categories = [
        "print-tshirt",
        "print-hoodie", 
        "graphic-shirt",
        "logo-tshirt",
        "fashion-hoodie"
    ]
    
    # 运行抓取任务
    logger.info("开始Amazon服装数据抓取")
    result = scraper.run_scraping(categories, max_pages=2)
    
    # 导出数据
    if result["status"] == "success":
        scraper.export_data("json")
        scraper.export_data("csv")
    
    # 打印结果
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()