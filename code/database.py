#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok & Amazon 热销服装数据存储管理模块

基于SQLite数据库的数据存储解决方案，支持：
- 产品数据管理
- 热度评论跟踪
- 价格历史记录
- 爬取任务日志
- 数据备份与恢复
"""

import sqlite3
import json
import logging
import os
import shutil
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
from queue import Queue, Empty
import hashlib


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    db_path: str = "data/products.db"
    backup_dir: str = "backup"
    connection_pool_size: int = 10
    backup_retention_days: int = 7
    auto_backup: bool = True
    backup_interval_hours: int = 24


class ConnectionPool:
    """简单的SQLite连接池"""
    
    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self._connections = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        
        # 预创建连接
        for _ in range(pool_size):
            conn = self._create_connection()
            self._connections.put(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """创建新的数据库连接"""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row  # 启用字典式访问
        conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
        conn.execute("PRAGMA journal_mode = WAL")  # 启用WAL模式提高并发性
        conn.execute("PRAGMA synchronous = NORMAL")  # 平衡性能和数据安全
        return conn
    
    @contextmanager
    def get_connection(self, timeout: float = 30.0):
        """获取数据库连接"""
        conn = None
        try:
            conn = self._connections.get(timeout=timeout)
            yield conn
        except Empty:
            logger.error("连接池已满，无法获取连接")
            raise RuntimeError("数据库连接池已满")
        except Exception as e:
            logger.error(f"数据库连接错误: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                try:
                    self._connections.put_nowait(conn)
                except:
                    # 连接池满时关闭连接
                    conn.close()


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: DatabaseConfig = None):
        """
        初始化数据库管理器
        
        Args:
            config: 数据库配置
        """
        self.config = config or DatabaseConfig()
        self.db_path = Path(self.config.db_path)
        self.backup_dir = Path(self.config.backup_dir)
        
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化连接池
        self.pool = ConnectionPool(str(self.db_path), self.config.connection_pool_size)
        
        # 初始化数据库表结构
        self._init_database()
        
        # 启动自动备份任务
        if self.config.auto_backup:
            self._start_auto_backup()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建产品主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    -- 基本信息
                    product_name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    category TEXT NOT NULL,
                    
                    -- 价格信息
                    price DECIMAL(10,2),
                    original_price DECIMAL(10,2),
                    currency TEXT DEFAULT 'USD',
                    
                    -- 销售数据
                    sales_count INTEGER,
                    rating DECIMAL(3,2),
                    review_count INTEGER,
                    
                    -- 链接信息
                    product_url TEXT NOT NULL,
                    store_url TEXT,
                    store_name TEXT,
                    
                    -- 图像信息
                    main_image_url TEXT,
                    image_urls TEXT,
                    
                    -- 热度数据
                    like_count INTEGER,
                    share_count INTEGER,
                    comment_count INTEGER,
                    view_count INTEGER,
                    
                    -- 时间和状态
                    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_source TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    
                    -- 备注
                    notes TEXT,
                    keywords TEXT
                )
            """)
            
            # 创建热度评论表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hot_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    
                    -- 评论内容
                    comment_text TEXT NOT NULL,
                    comment_author TEXT,
                    author_followers INTEGER,
                    
                    -- 互动数据
                    likes_count INTEGER DEFAULT 0,
                    replies_count INTEGER DEFAULT 0,
                    
                    -- 时间信息
                    comment_date TIMESTAMP,
                    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
                )
            """)
            
            # 创建价格历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    
                    -- 价格数据
                    price DECIMAL(10,2) NOT NULL,
                    original_price DECIMAL(10,2),
                    discount_percent INTEGER,
                    
                    -- 时间信息
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
                )
            """)
            
            # 创建爬取任务日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scrape_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    -- 任务信息
                    platform TEXT NOT NULL,
                    category TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    
                    -- 执行结果
                    status TEXT NOT NULL,
                    records_found INTEGER DEFAULT 0,
                    records_saved INTEGER DEFAULT 0,
                    error_message TEXT,
                    
                    -- 时间信息
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_seconds INTEGER,
                    
                    -- 元数据
                    user_agent TEXT,
                    ip_address TEXT,
                    session_id TEXT
                )
            """)
            
            # 创建索引
            self._create_indexes(cursor)
            
            # 添加约束
            self._add_constraints(cursor)
            
            conn.commit()
            logger.info("数据库初始化完成")
    
    def _create_indexes(self, cursor: sqlite3.Cursor):
        """创建数据库索引"""
        indexes = [
            # 产品表索引
            "CREATE INDEX IF NOT EXISTS idx_products_platform_category ON products(platform, category)",
            "CREATE INDEX IF NOT EXISTS idx_products_last_updated ON products(last_updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active, platform)",
            "CREATE INDEX IF NOT EXISTS idx_products_url ON products(product_url)",
            
            # 价格历史表索引
            "CREATE INDEX IF NOT EXISTS idx_price_history_product_date ON price_history(product_id, recorded_at)",
            "CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(recorded_at)",
            
            # 热度评论表索引
            "CREATE INDEX IF NOT EXISTS idx_hot_comments_product ON hot_comments(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_hot_comments_likes ON hot_comments(likes_count DESC)",
            "CREATE INDEX IF NOT EXISTS idx_hot_comments_date ON hot_comments(captured_at)",
            
            # 爬取日志表索引
            "CREATE INDEX IF NOT EXISTS idx_scrape_logs_platform_date ON scrape_logs(platform, started_at)",
            "CREATE INDEX IF NOT EXISTS idx_scrape_logs_status ON scrape_logs(status, started_at)",
            "CREATE INDEX IF NOT EXISTS idx_scrape_logs_type ON scrape_logs(task_type)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        logger.info("数据库索引创建完成")
    
    def _add_constraints(self, cursor: sqlite3.Cursor):
        """添加数据约束"""
        constraints = [
            # 检查价格必须为正数
            "CREATE TABLE IF NOT EXISTS products_price_check AS SELECT * FROM products WHERE 1=0",
            "CREATE TRIGGER IF NOT EXISTS products_price_validation "
            "BEFORE INSERT ON products "
            "WHEN NEW.price IS NOT NULL AND NEW.price <= 0 "
            "BEGIN SELECT RAISE(ABORT, '价格必须大于0'); END;",
            
            # 检查评分范围
            "CREATE TRIGGER IF NOT EXISTS products_rating_validation "
            "BEFORE INSERT ON products "
            "WHEN NEW.rating IS NOT NULL AND (NEW.rating < 0 OR NEW.rating > 5) "
            "BEGIN SELECT RAISE(ABORT, '评分必须在0-5之间'); END;",
            
            # 检查平台枚举值
            "CREATE TRIGGER IF NOT EXISTS products_platform_validation "
            "BEFORE INSERT ON products "
            "WHEN NEW.platform NOT IN ('tiktok', 'amazon') "
            "BEGIN SELECT RAISE(ABORT, '平台必须是tiktok或amazon'); END;",
            
            # 检查分类枚举值
            "CREATE TRIGGER IF NOT EXISTS products_category_validation "
            "BEFORE INSERT ON products "
            "WHEN NEW.category NOT IN ('tshirt', 'hoodie', 'sweatshirt') "
            "BEGIN SELECT RAISE(ABORT, '分类必须是tshirt、hoodie或sweatshirt'); END;"
        ]
        
        for constraint_sql in constraints:
            try:
                cursor.execute(constraint_sql)
            except sqlite3.Error as e:
                logger.warning(f"约束创建失败: {e}")
    
    def _start_auto_backup(self):
        """启动自动备份任务"""
        def backup_task():
            while True:
                try:
                    time.sleep(self.config.backup_interval_hours * 3600)
                    self.create_backup()
                    self.cleanup_old_backups()
                except Exception as e:
                    logger.error(f"自动备份任务错误: {e}")
        
        backup_thread = threading.Thread(target=backup_task, daemon=True)
        backup_thread.start()
        logger.info("自动备份任务已启动")
    
    # ==================== 产品管理方法 ====================
    
    def insert_product(self, product_data: Dict[str, Any]) -> int:
        """
        插入新产品记录
        
        Args:
            product_data: 产品数据
            
        Returns:
            新产品ID
        """
        try:
            # 处理JSON字段
            if 'image_urls' in product_data and isinstance(product_data['image_urls'], list):
                product_data['image_urls'] = json.dumps(product_data['image_urls'])
            if 'keywords' in product_data and isinstance(product_data['keywords'], list):
                product_data['keywords'] = json.dumps(product_data['keywords'])
            
            # 检查产品URL是否已存在
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM products WHERE product_url = ?", 
                             (product_data['product_url'],))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有产品
                    product_data['last_updated_at'] = datetime.now().isoformat()
                    update_fields = [f"{k} = ?" for k in product_data.keys() if k != 'product_url']
                    update_values = [product_data[k] for k in product_data.keys() if k != 'product_url']
                    update_values.append(product_data['product_url'])
                    
                    cursor.execute(f"""
                        UPDATE products SET {', '.join(update_fields)}
                        WHERE product_url = ?
                    """, update_values)
                    conn.commit()
                    logger.info(f"产品已更新: {product_data['product_url']}")
                    return existing[0]
                else:
                    # 插入新产品
                    placeholders = ', '.join(['?' for _ in product_data])
                    columns = ', '.join(product_data.keys())
                    values = list(product_data.values())
                    
                    cursor.execute(f"""
                        INSERT INTO products ({columns}) VALUES ({placeholders})
                    """, values)
                    product_id = cursor.lastrowid
                    conn.commit()
                    logger.info(f"新产品已插入: ID {product_id}")
                    return product_id
                    
        except Exception as e:
            logger.error(f"插入产品失败: {e}")
            raise
    
    def get_products(self, 
                    platform: str = None, 
                    category: str = None,
                    limit: int = 100,
                    offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取产品列表
        
        Args:
            platform: 平台过滤
            category: 分类过滤
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            产品列表
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                where_clauses = ["is_active = 1"]
                params = []
                
                if platform:
                    where_clauses.append("platform = ?")
                    params.append(platform)
                
                if category:
                    where_clauses.append("category = ?")
                    params.append(category)
                
                where_sql = " AND ".join(where_clauses)
                
                cursor.execute(f"""
                    SELECT * FROM products 
                    WHERE {where_sql}
                    ORDER BY last_updated_at DESC
                    LIMIT ? OFFSET ?
                """, params + [limit, offset])
                
                products = []
                for row in cursor.fetchall():
                    product = dict(row)
                    # 解析JSON字段
                    if product['image_urls']:
                        try:
                            product['image_urls'] = json.loads(product['image_urls'])
                        except:
                            pass
                    if product['keywords']:
                        try:
                            product['keywords'] = json.loads(product['keywords'])
                        except:
                            pass
                    products.append(product)
                
                return products
                
        except Exception as e:
            logger.error(f"获取产品列表失败: {e}")
            return []
    
    def update_product_price(self, product_id: int, price: float, original_price: float = None):
        """
        更新产品价格并记录到历史表
        
        Args:
            product_id: 产品ID
            price: 新价格
            original_price: 原价
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                # 更新产品价格
                update_data = {
                    'price': price,
                    'last_updated_at': datetime.now().isoformat()
                }
                if original_price:
                    update_data['original_price'] = original_price
                
                placeholders = ', '.join([f"{k} = ?" for k in update_data.keys()])
                values = list(update_data.values()) + [product_id]
                
                cursor.execute(f"UPDATE products SET {placeholders} WHERE id = ?", values)
                
                # 记录到价格历史表
                discount_percent = None
                if original_price and original_price > 0:
                    discount_percent = int((original_price - price) / original_price * 100)
                
                cursor.execute("""
                    INSERT INTO price_history (product_id, price, original_price, discount_percent)
                    VALUES (?, ?, ?, ?)
                """, (product_id, price, original_price, discount_percent))
                
                conn.commit()
                logger.info(f"产品价格已更新: 产品ID {product_id}, 价格 {price}")
                
        except Exception as e:
            logger.error(f"更新产品价格失败: {e}")
            raise
    
    def delete_product(self, product_id: int, soft_delete: bool = True):
        """
        删除产品
        
        Args:
            product_id: 产品ID
            soft_delete: 是否软删除
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                if soft_delete:
                    cursor.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
                else:
                    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                
                conn.commit()
                logger.info(f"产品已删除: ID {product_id}")
                
        except Exception as e:
            logger.error(f"删除产品失败: {e}")
            raise
    
    # ==================== 评论管理方法 ====================
    
    def insert_hot_comment(self, product_id: int, comment_data: Dict[str, Any]):
        """
        插入热度评论
        
        Args:
            product_id: 产品ID
            comment_data: 评论数据
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO hot_comments (
                        product_id, comment_text, comment_author, author_followers,
                        likes_count, replies_count, comment_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id,
                    comment_data.get('comment_text'),
                    comment_data.get('comment_author'),
                    comment_data.get('author_followers'),
                    comment_data.get('likes_count', 0),
                    comment_data.get('replies_count', 0),
                    comment_data.get('comment_date')
                ))
                
                conn.commit()
                logger.info(f"热度评论已插入: 产品ID {product_id}")
                
        except Exception as e:
            logger.error(f"插入热度评论失败: {e}")
            raise
    
    def get_hot_comments(self, product_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取产品热度评论
        
        Args:
            product_id: 产品ID
            limit: 限制数量
            
        Returns:
            评论列表
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM hot_comments 
                    WHERE product_id = ?
                    ORDER BY likes_count DESC, captured_at DESC
                    LIMIT ?
                """, (product_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"获取热度评论失败: {e}")
            return []
    
    # ==================== 价格历史方法 ====================
    
    def get_price_history(self, product_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取产品价格历史
        
        Args:
            product_id: 产品ID
            days: 查询天数
            
        Returns:
            价格历史记录
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM price_history 
                    WHERE product_id = ? AND recorded_at >= datetime('now', '-{} days')
                    ORDER BY recorded_at ASC
                """.format(days), (product_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"获取价格历史失败: {e}")
            return []
    
    # ==================== 爬取日志方法 ====================
    
    def insert_scrape_log(self, log_data: Dict[str, Any]) -> int:
        """
        插入爬取日志
        
        Args:
            log_data: 日志数据
            
        Returns:
            日志ID
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO scrape_logs (
                        platform, category, task_type, status, records_found,
                        records_saved, error_message, user_agent, ip_address, session_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_data['platform'],
                    log_data['category'],
                    log_data['task_type'],
                    log_data['status'],
                    log_data.get('records_found', 0),
                    log_data.get('records_saved', 0),
                    log_data.get('error_message'),
                    log_data.get('user_agent'),
                    log_data.get('ip_address'),
                    log_data.get('session_id')
                ))
                
                log_id = cursor.lastrowid
                conn.commit()
                return log_id
                
        except Exception as e:
            logger.error(f"插入爬取日志失败: {e}")
            raise
    
    def update_scrape_log(self, log_id: int, **kwargs):
        """
        更新爬取日志
        
        Args:
            log_id: 日志ID
            **kwargs: 更新字段
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                if 'completed_at' not in kwargs:
                    kwargs['completed_at'] = datetime.now().isoformat()
                
                # 计算执行时长
                if 'started_at' in kwargs and 'completed_at' in kwargs:
                    start_time = datetime.fromisoformat(kwargs['started_at'])
                    end_time = datetime.fromisoformat(kwargs['completed_at'])
                    kwargs['duration_seconds'] = int((end_time - start_time).total_seconds())
                
                set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
                values = list(kwargs.values()) + [log_id]
                
                cursor.execute(f"UPDATE scrape_logs SET {set_clause} WHERE id = ?", values)
                conn.commit()
                
        except Exception as e:
            logger.error(f"更新爬取日志失败: {e}")
            raise
    
    def get_scrape_logs(self, 
                       platform: str = None,
                       status: str = None,
                       days: int = 7,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取爬取日志
        
        Args:
            platform: 平台过滤
            status: 状态过滤
            days: 查询天数
            limit: 限制数量
            
        Returns:
            日志列表
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                where_clauses = ["started_at >= datetime('now', '-{} days')".format(days)]
                params = []
                
                if platform:
                    where_clauses.append("platform = ?")
                    params.append(platform)
                
                if status:
                    where_clauses.append("status = ?")
                    params.append(status)
                
                where_sql = " AND ".join(where_clauses)
                
                cursor.execute(f"""
                    SELECT * FROM scrape_logs 
                    WHERE {where_sql}
                    ORDER BY started_at DESC
                    LIMIT ?
                """, params + [limit])
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"获取爬取日志失败: {e}")
            return []
    
    # ==================== 备份与恢复方法 ====================
    
    def create_backup(self, backup_name: str = None) -> str:
        """
        创建数据库备份
        
        Args:
            backup_name: 备份文件名（可选）
            
        Returns:
            备份文件路径
        """
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"products_backup_{timestamp}.db"
            
            backup_path = self.backup_dir / backup_name
            
            with self.pool.get_connection() as conn:
                backup_conn = sqlite3.connect(str(backup_path))
                conn.backup(backup_conn)
                backup_conn.close()
            
            logger.info(f"数据库备份已创建: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            raise
    
    def restore_backup(self, backup_path: str):
        """
        从备份恢复数据库
        
        Args:
            backup_path: 备份文件路径
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            # 关闭所有连接
            while not self.pool._connections.empty():
                try:
                    conn = self.pool._connections.get_nowait()
                    conn.close()
                except:
                    break
            
            # 复制备份文件
            shutil.copy2(backup_path, self.db_path)
            
            # 重新初始化连接池
            self.pool = ConnectionPool(str(self.db_path), self.config.connection_pool_size)
            
            logger.info(f"数据库已从备份恢复: {backup_path}")
            
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            raise
    
    def cleanup_old_backups(self):
        """清理过期的备份文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.backup_retention_days)
            
            for backup_file in self.backup_dir.glob("products_backup_*.db"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.info(f"删除过期备份: {backup_file}")
            
        except Exception as e:
            logger.error(f"清理过期备份失败: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                # 数据库大小
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                db_size_mb = (page_size * page_count) / 1024 / 1024
                
                # 各类记录数量
                stats = {}
                for table in ['products', 'hot_comments', 'price_history', 'scrape_logs']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # 今日新增记录
                cursor.execute("SELECT COUNT(*) FROM products WHERE DATE(first_seen_at) = DATE('now')")
                stats['today_new_products'] = cursor.fetchone()[0]
                
                # 活跃产品数量
                cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
                stats['active_products'] = cursor.fetchone()[0]
                
                # 最近失败任务数
                cursor.execute("SELECT COUNT(*) FROM scrape_logs WHERE status = 'failed' AND DATE(started_at) = DATE('now')")
                stats['today_failed_tasks'] = cursor.fetchone()[0]
                
                stats['database_size_mb'] = round(db_size_mb, 2)
                
                return stats
                
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        try:
            # 关闭连接池中的所有连接
            while not self.pool._connections.empty():
                try:
                    conn = self.pool._connections.get_nowait()
                    conn.close()
                except:
                    break
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")


# ==================== 便利函数 ====================

def get_database_manager(config: DatabaseConfig = None) -> DatabaseManager:
    """
    获取数据库管理器实例
    
    Args:
        config: 数据库配置
        
    Returns:
        数据库管理器实例
    """
    return DatabaseManager(config)


def create_sample_data(db_manager: DatabaseManager, count: int = 10):
    """
    创建示例数据用于测试
    
    Args:
        db_manager: 数据库管理器
        count: 创建记录数量
    """
    import random
    
    platforms = ['tiktok', 'amazon']
    categories = ['tshirt', 'hoodie', 'sweatshirt']
    sample_products = []
    
    for i in range(count):
        platform = random.choice(platforms)
        category = random.choice(categories)
        
        product = {
            'product_name': f"{category.title()} {i+1} - 热门款式",
            'platform': platform,
            'category': category,
            'price': round(random.uniform(15.99, 89.99), 2),
            'original_price': round(random.uniform(20.99, 99.99), 2),
            'currency': 'USD',
            'sales_count': random.randint(100, 10000),
            'rating': round(random.uniform(3.0, 5.0), 1),
            'review_count': random.randint(10, 500),
            'product_url': f"https://{platform}.com/product/{i+1}",
            'store_url': f"https://{platform}.com/store/merchant_{i%5}",
            'store_name': f"Store {i%5}",
            'main_image_url': f"https://cdn.example.com/product_{i+1}.jpg",
            'image_urls': [f"https://cdn.example.com/product_{i+1}_{j}.jpg" for j in range(3)],
            'like_count': random.randint(50, 1000),
            'share_count': random.randint(10, 200),
            'comment_count': random.randint(5, 100),
            'view_count': random.randint(500, 5000),
            'data_source': 'web_scraper',
            'keywords': ['hot', 'trending', 'fashion'],
            'notes': f'示例产品数据 #{i+1}'
        }
        
        product_id = db_manager.insert_product(product)
        sample_products.append(product_id)
        
        # 为每个产品添加一些评论
        for j in range(random.randint(2, 5)):
            comment = {
                'comment_text': f'这真是{j+1}个很棒的产品！',
                'comment_author': f'用户{i}_{j}',
                'author_followers': random.randint(100, 10000),
                'likes_count': random.randint(5, 100),
                'replies_count': random.randint(0, 10),
                'comment_date': datetime.now().isoformat()
            }
            db_manager.insert_hot_comment(product_id, comment)
        
        # 添加价格历史
        for k in range(random.randint(1, 3)):
            price = round(product['price'] * (0.9 ** k), 2)
            original_price = product['original_price']
            db_manager.update_product_price(product_id, price, original_price)
    
    logger.info(f"示例数据创建完成，共 {len(sample_products)} 个产品")


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 配置数据库
    config = DatabaseConfig(
        db_path="test_data/products.db",
        backup_dir="test_data/backup",
        auto_backup=True
    )
    
    # 初始化数据库管理器
    db = get_database_manager(config)
    
    try:
        # 创建示例数据
        print("创建示例数据...")
        create_sample_data(db, count=20)
        
        # 测试查询
        print("\n获取产品列表:")
        products = db.get_products(limit=5)
        for product in products:
            print(f"- {product['product_name']} ({product['platform']}) - ${product['price']}")
        
        # 测试统计信息
        print("\n数据库统计:")
        stats = db.get_database_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 测试备份
        print("\n创建备份...")
        backup_path = db.create_backup()
        print(f"备份已创建: {backup_path}")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
    
    finally:
        # 关闭数据库连接
        db.close()
        print("\n数据库连接已关闭")