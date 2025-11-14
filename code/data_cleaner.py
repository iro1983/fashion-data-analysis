#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗和处理模块
处理从TikTok和Amazon抓取的产品数据，确保符合数据库结构要求
"""

import re
import json
import logging
import unicodedata
from typing import Dict, List, Tuple, Optional, Union, Any
from urllib.parse import urlparse, urljoin
from difflib import SequenceMatcher
from datetime import datetime


class DataCleaner:
    """数据清洗和处理类"""
    
    def __init__(self):
        """初始化数据清洗器"""
        self.logger = self._setup_logger()
        
        # 产品分类映射
        self.category_mapping = {
            'tshirt': ['t-shirt', 't shirt', 'tee', 'T恤', 't恤', '短袖', '短袖衫'],
            'hoodie': ['hoodie', 'hooded', '卫衣', '连帽衫', '帽衫', '拉链衫'],
            'sweatshirt': ['sweatshirt', 'sweater', '毛衣', '针织衫', '长袖衫', '套头衫']
        }
        
        # 价格验证范围
        self.price_range = (0, 1000)
        
        # 评分验证范围
        self.rating_range = (0, 5)
        
        # 质量报告统计
        self.quality_stats = {
            'total_processed': 0,
            'valid_products': 0,
            'invalid_products': 0,
            'duplicates_removed': 0,
            'errors': []
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('DataCleaner')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def clean_product_data(self, raw_data: Union[Dict, List[Dict]]) -> Dict:
        """
        清洗单条产品数据
        
        Args:
            raw_data: 原始产品数据
            
        Returns:
            清洗后的产品数据字典
        """
        if isinstance(raw_data, list):
            return self.clean_batch(raw_data)
        
        self.quality_stats['total_processed'] += 1
        
        cleaned_data = {
            'title': self._clean_title(raw_data.get('title', '')),
            'price': self._format_price(raw_data.get('price', 0)),
            'original_price': self._format_price(raw_data.get('original_price', 0)),
            'category': self._map_category(raw_data.get('category', '')),
            'rating': self._format_rating(raw_data.get('rating', 0)),
            'review_count': self._format_number(raw_data.get('review_count', 0)),
            'image_url': self._validate_url(raw_data.get('image_url', '')),
            'product_url': self._validate_url(raw_data.get('product_url', '')),
            'brand': self._clean_text(raw_data.get('brand', '')),
            'description': self._clean_description(raw_data.get('description', '')),
            'colors': self._extract_colors(raw_data.get('colors', '')),
            'sizes': self._extract_sizes(raw_data.get('sizes', '')),
            'source': raw_data.get('source', 'unknown'),
            'source_id': raw_data.get('source_id', ''),
            'scraped_at': datetime.now().isoformat(),
            'keywords': self._extract_keywords(raw_data.get('title', '')),
            'slug': self._generate_slug(raw_data.get('title', '')),
            'popularity_score': self._calculate_popularity_score(raw_data),
            'data_quality_score': 0,
            'validation_errors': []
        }
        
        # 验证数据
        validation_result = self._validate_product_data(cleaned_data)
        cleaned_data['data_quality_score'] = validation_result['quality_score']
        cleaned_data['validation_errors'] = validation_result['errors']
        
        if validation_result['is_valid']:
            self.quality_stats['valid_products'] += 1
        else:
            self.quality_stats['invalid_products'] += 1
            self.quality_stats['errors'].extend(validation_result['errors'])
        
        return cleaned_data
    
    def clean_batch(self, batch_data: List[Dict]) -> Dict:
        """
        批量清洗产品数据
        
        Args:
            batch_data: 原始产品数据列表
            
        Returns:
            批量处理结果
        """
        cleaned_products = []
        valid_products = []
        invalid_products = []
        
        for product_data in batch_data:
            try:
                cleaned = self.clean_product_data(product_data)
                cleaned_products.append(cleaned)
                
                if cleaned['validation_errors']:
                    invalid_products.append(cleaned)
                else:
                    valid_products.append(cleaned)
            except Exception as e:
                self.logger.error(f"清洗数据时出错: {e}")
                self.quality_stats['errors'].append(f"批量处理错误: {str(e)}")
        
        # 去重处理
        deduplicated_products = self._remove_duplicates(cleaned_products)
        self.quality_stats['duplicates_removed'] = len(cleaned_products) - len(deduplicated_products)
        
        return {
            'products': deduplicated_products,
            'valid_products': [p for p in deduplicated_products if not p['validation_errors']],
            'invalid_products': [p for p in deduplicated_products if p['validation_errors']],
            'quality_report': self.generate_quality_report(),
            'processed_at': datetime.now().isoformat()
        }
    
    def _clean_title(self, title: str) -> str:
        """清理产品标题"""
        if not isinstance(title, str):
            return ""
        
        # 移除HTML标签
        title = re.sub(r'<[^>]+>', '', title)
        
        # 移除多余的空白字符
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 移除特殊字符，但保留中文、英文、数字、常用符号
        title = re.sub(r'[^\w\s\-_\.\,\!\?\(\)\[\]\{\}\"\'\&\%\$#@\*\+\=\|\:;/\\]', '', title)
        
        # 标准化Unicode字符
        title = unicodedata.normalize('NFKD', title)
        
        # 限制长度
        if len(title) > 200:
            title = title[:200] + "..."
        
        return title
    
    def _format_price(self, price: Union[str, int, float]) -> float:
        """格式化价格"""
        if price is None or price == "":
            return 0.0
        
        if isinstance(price, str):
            # 移除货币符号和非数字字符
            price_str = re.sub(r'[^\d\.]', '', price)
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                return 0.0
        
        try:
            price = float(price)
            # 限制价格范围
            if price < self.price_range[0]:
                return 0.0
            if price > self.price_range[1]:
                return self.price_range[1]
            return round(price, 2)
        except (ValueError, TypeError):
            return 0.0
    
    def _map_category(self, category: str) -> str:
        """映射产品分类"""
        if not isinstance(category, str):
            return "other"
        
        category_lower = category.lower().strip()
        
        for standard_cat, keywords in self.category_mapping.items():
            for keyword in keywords:
                if keyword.lower() in category_lower:
                    return standard_cat
        
        return "other"
    
    def _format_rating(self, rating: Union[str, int, float]) -> float:
        """格式化评分"""
        if rating is None or rating == "":
            return 0.0
        
        if isinstance(rating, str):
            # 提取数字
            rating_match = re.search(r'(\d+\.?\d*)', rating)
            if rating_match:
                rating = float(rating_match.group(1))
            else:
                return 0.0
        
        try:
            rating = float(rating)
            if rating < self.rating_range[0]:
                return self.rating_range[0]
            if rating > self.rating_range[1]:
                return self.rating_range[1]
            return round(rating, 1)
        except (ValueError, TypeError):
            return 0.0
    
    def _format_number(self, num: Union[str, int, float]) -> int:
        """格式化数字"""
        if num is None or num == "":
            return 0
        
        if isinstance(num, str):
            # 提取数字
            num_str = re.sub(r'[^\d]', '', num)
            try:
                num = int(num_str)
            except (ValueError, TypeError):
                return 0
        
        try:
            num = int(num)
            return max(0, num)
        except (ValueError, TypeError):
            return 0
    
    def _validate_url(self, url: str) -> str:
        """验证和规范化URL"""
        if not isinstance(url, str) or not url.strip():
            return ""
        
        try:
            parsed = urlparse(url)
            
            # 确保URL有协议
            if not parsed.scheme:
                url = urljoin('https://', url)
                parsed = urlparse(url)
            
            # 验证URL格式
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                # 标准化域名大小写
                normalized_url = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"
                if parsed.query:
                    normalized_url += f"?{parsed.query}"
                return normalized_url
            
            return ""
        except Exception:
            return ""
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not isinstance(text, str):
            return ""
        
        # 移除HTML标签和多余空白
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _clean_description(self, description: str) -> str:
        """清理产品描述"""
        if not isinstance(description, str):
            return ""
        
        # 移除HTML标签
        description = re.sub(r'<[^>]+>', '', description)
        
        # 移除多余的空白字符
        description = re.sub(r'\s+', ' ', description).strip()
        
        # 限制长度
        if len(description) > 1000:
            description = description[:1000] + "..."
        
        return description
    
    def _extract_colors(self, colors_input: Union[str, List[str]]) -> List[str]:
        """提取颜色信息"""
        if isinstance(colors_input, list):
            return [self._clean_text(color) for color in colors_input if color]
        
        if not isinstance(colors_input, str):
            return []
        
        # 常见颜色关键词
        color_keywords = [
            'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink',
            'brown', 'gray', 'grey', 'navy', 'beige', 'cream', 'khaki', 'olive', 'maroon',
            '黑色', '白色', '红色', '蓝色', '绿色', '黄色', '橙色', '紫色', '粉色',
            '棕色', '灰色', '米色', '卡其', '橄榄', '栗色'
        ]
        
        found_colors = []
        colors_lower = colors_input.lower()
        
        for color in color_keywords:
            if color in colors_lower:
                found_colors.append(color)
        
        return list(set(found_colors))
    
    def _extract_sizes(self, sizes_input: Union[str, List[str]]) -> List[str]:
        """提取尺寸信息"""
        if isinstance(sizes_input, list):
            return [self._clean_text(size) for size in sizes_input if size]
        
        if not isinstance(sizes_input, str):
            return []
        
        # 常见尺寸格式
        size_patterns = [
            r'\b(xx?s|xs|s|m|l|xl|xxl|xxxl)\b',
            r'\b(\d{1,2}\s*(inch|in)?)\b',
            r'\b(\d{2,3}\s*(cm|centimeter)?)\b',
            r'\b(小号|s|中号|m|大号|l|特大号|xl)\b'
        ]
        
        found_sizes = []
        for pattern in size_patterns:
            matches = re.findall(pattern, sizes_input, re.IGNORECASE)
            for match in matches:
                size = match if isinstance(match, str) else match[0]
                found_sizes.append(size.strip())
        
        return list(set(found_sizes))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        if not isinstance(text, str):
            return []
        
        # 转换为小写并分词
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词和短词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', '我', '你', '他', '她', '它', '我们', '你们', '他们', '的', '了', '在', '是', '有', '和', '与', '或', '但', '与', '到', '为', '对', '从', '被', '让', '把', '被'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # 去重并限制数量
        unique_keywords = list(set(keywords))[:10]
        
        return unique_keywords
    
    def _generate_slug(self, title: str) -> str:
        """生成产品slug"""
        if not isinstance(title, str):
            return ""
        
        # 转换为小写
        slug = title.lower()
        
        # 替换特殊字符为连字符
        slug = re.sub(r'[^\w\s\-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        
        # 移除首尾连字符
        slug = slug.strip('-')
        
        # 限制长度
        if len(slug) > 50:
            slug = slug[:50]
        
        return slug
    
    def _calculate_popularity_score(self, raw_data: Dict) -> float:
        """计算热度分数"""
        score = 0.0
        
        # 基于评分的分数
        rating = self._format_rating(raw_data.get('rating', 0))
        score += rating * 20  # 最高100分
        
        # 基于评论数量的分数
        review_count = self._format_number(raw_data.get('review_count', 0))
        if review_count > 0:
            # 使用对数函数计算评论数量分数
            import math
            review_score = min(100, math.log10(review_count + 1) * 25)
            score += review_score
        
        # 基于价格的分数（中等价格得分较高）
        price = self._format_price(raw_data.get('price', 0))
        if 10 <= price <= 100:
            score += 20
        elif price > 0:
            score += 10
        
        # 基于数据来源的分数
        source = raw_data.get('source', '').lower()
        if 'tiktok' in source:
            score += 15
        elif 'amazon' in source:
            score += 10
        
        return min(100.0, max(0.0, score))
    
    def _validate_product_data(self, product: Dict) -> Dict:
        """验证产品数据"""
        errors = []
        quality_score = 100
        
        # 验证必填字段
        required_fields = ['title', 'price', 'category', 'product_url']
        for field in required_fields:
            if not product.get(field):
                errors.append(f"缺少必填字段: {field}")
                quality_score -= 20
        
        # 验证价格
        if product.get('price', 0) <= 0:
            errors.append("价格必须大于0")
            quality_score -= 15
        
        # 验证URL
        for url_field in ['product_url', 'image_url']:
            url = product.get(url_field)
            if url and not self._validate_url(url):
                errors.append(f"URL格式无效: {url_field}")
                quality_score -= 10
        
        # 验证评分
        rating = product.get('rating', 0)
        if rating < 0 or rating > 5:
            errors.append("评分必须在0-5之间")
            quality_score -= 10
        
        # 验证产品标题长度
        title = product.get('title', '')
        if len(title) < 5:
            errors.append("产品标题过短")
            quality_score -= 10
        elif len(title) > 200:
            errors.append("产品标题过长")
            quality_score -= 5
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'quality_score': max(0, quality_score)
        }
    
    def _remove_duplicates(self, products: List[Dict]) -> List[Dict]:
        """去除重复产品"""
        if not products:
            return []
        
        unique_products = []
        seen_urls = set()
        seen_titles = set()
        
        for product in products:
            # 基于URL去重
            product_url = product.get('product_url', '')
            title = product.get('title', '')
            
            is_duplicate = False
            
            # 检查URL重复
            if product_url and product_url in seen_urls:
                is_duplicate = True
            
            # 检查标题相似度
            elif title:
                title_lower = title.lower().strip()
                for seen_title in seen_titles:
                    similarity = self._calculate_similarity(title_lower, seen_title)
                    if similarity > 0.85:  # 85%相似度阈值
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_products.append(product)
                if product_url:
                    seen_urls.add(product_url)
                if title:
                    seen_titles.add(title.lower().strip())
        
        return unique_products
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算两个字符串的相似度"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def generate_quality_report(self) -> Dict:
        """生成数据质量报告"""
        total = self.quality_stats['total_processed']
        
        if total == 0:
            return {
                'message': '没有处理任何数据',
                'stats': self.quality_stats.copy()
            }
        
        valid_rate = (self.quality_stats['valid_products'] / total) * 100
        error_rate = (self.quality_stats['invalid_products'] / total) * 100
        
        # 统计错误类型
        error_types = {}
        for error in self.quality_stats['errors']:
            error_type = error.split(':')[0] if ':' in error else '未知错误'
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'summary': {
                'total_processed': total,
                'valid_products': self.quality_stats['valid_products'],
                'invalid_products': self.quality_stats['invalid_products'],
                'duplicates_removed': self.quality_stats['duplicates_removed'],
                'valid_rate': round(valid_rate, 2),
                'error_rate': round(error_rate, 2),
                'data_quality_score': round((valid_rate / 100) * 100, 2)
            },
            'error_analysis': {
                'total_errors': len(self.quality_stats['errors']),
                'error_types': error_types,
                'top_errors': list(error_types.keys())[:5]
            },
            'recommendations': self._generate_recommendations(),
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成数据质量改进建议"""
        recommendations = []
        
        total = self.quality_stats['total_processed']
        if total == 0:
            return ['请先处理数据']
        
        valid_rate = (self.quality_stats['valid_products'] / total) * 100
        
        if valid_rate < 50:
            recommendations.append("数据质量较低，建议检查数据源和数据提取逻辑")
        elif valid_rate < 80:
            recommendations.append("数据质量中等，建议优化数据验证规则")
        else:
            recommendations.append("数据质量良好")
        
        if self.quality_stats['duplicates_removed'] > 0:
            recommendations.append(f"去除了{self.quality_stats['duplicates_removed']}个重复产品，建议改进去重算法")
        
        error_types = {}
        for error in self.quality_stats['errors']:
            error_type = error.split(':')[0] if ':' in error else '未知错误'
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if error_types:
            top_error = max(error_types.items(), key=lambda x: x[1])
            recommendations.append(f"最常见的错误是: {top_error[0]}，建议重点改进")
        
        return recommendations
    
    def export_cleaned_data(self, cleaned_data: Dict, format: str = 'json') -> str:
        """
        导出清洗后的数据
        
        Args:
            cleaned_data: 清洗后的数据
            format: 导出格式 ('json' 或 'csv')
            
        Returns:
            导出的数据字符串
        """
        if format.lower() == 'json':
            return json.dumps(cleaned_data, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def reset_stats(self):
        """重置质量统计"""
        self.quality_stats = {
            'total_processed': 0,
            'valid_products': 0,
            'invalid_products': 0,
            'duplicates_removed': 0,
            'errors': []
        }


# 使用示例
if __name__ == "__main__":
    # 创建数据清洗器实例
    cleaner = DataCleaner()
    
    # 示例数据
    sample_data = [
        {
            'title': 'Classic Cotton T-Shirt - Black <b>Sale!</b>',
            'price': '$29.99',
            'original_price': '$39.99',
            'category': 'T-Shirts & Tanks',
            'rating': 4.5,
            'review_count': '1,234 reviews',
            'image_url': 'https://example.com/image1.jpg',
            'product_url': 'https://amazon.com/product/123',
            'brand': 'Nike',
            'description': 'Comfortable cotton t-shirt perfect for everyday wear',
            'colors': 'Black, White, Blue',
            'sizes': 'S, M, L, XL',
            'source': 'amazon',
            'source_id': 'B08N5WRWNW'
        },
        {
            'title': 'Hoodie - 卫衣 - 灰色',
            'price': '59.99美元',
            'category': '服装 - 卫衣',
            'rating': '4.2/5',
            'review_count': 856,
            'product_url': 'tiktok.com/product/456',
            'source': 'tiktok',
            'source_id': 'tt456'
        }
    ]
    
    # 清洗数据
    print("开始数据清洗...")
    result = cleaner.clean_product_data(sample_data[0])
    
    print("\n清洗结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 批量清洗
    print("\n开始批量清洗...")
    batch_result = cleaner.clean_batch(sample_data)
    
    print(f"\n批量处理结果:")
    print(f"处理产品数: {len(batch_result['products'])}")
    print(f"有效产品数: {len(batch_result['valid_products'])}")
    print(f"无效产品数: {len(batch_result['invalid_products'])}")
    print(f"去重移除: {batch_result['quality_report']['summary']['duplicates_removed']}")
    
    # 质量报告
    print(f"\n质量报告:")
    quality_report = batch_result['quality_report']
    print(json.dumps(quality_report, ensure_ascii=False, indent=2))