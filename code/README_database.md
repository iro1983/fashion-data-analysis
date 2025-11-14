# 数据库管理系统使用说明

## 概述

这是一个基于SQLite的完整数据库管理系统，专门为TikTok & Amazon热销服装数据存储而设计。

## 主要功能

### 1. 数据库表结构
- **products**: 产品主表，存储产品基本信息、价格、销量等
- **hot_comments**: 热度评论表，存储产品相关评论数据
- **price_history**: 价格历史表，记录产品价格变化
- **scrape_logs**: 爬取任务日志表，记录数据抓取过程

### 2. 核心特性
- ✅ 完整的CRUD操作
- ✅ 连接池管理
- ✅ 数据验证约束
- ✅ 自动备份功能
- ✅ 索引优化
- ✅ 错误处理和日志记录
- ✅ 并发访问支持

## 快速开始

### 1. 基本使用

```python
from database import DatabaseManager, DatabaseConfig

# 配置数据库
config = DatabaseConfig(
    db_path="data/products.db",
    backup_dir="data/backup",
    auto_backup=True
)

# 初始化数据库管理器
db = DatabaseManager(config)

# 插入产品数据
product = {
    'product_name': '热门T恤',
    'platform': 'tiktok',
    'category': 'tshirt',
    'price': 29.99,
    'original_price': 39.99,
    'product_url': 'https://tiktok.com/product/123',
    'store_name': 'Fashion Store',
    'rating': 4.5,
    'review_count': 150,
    'sales_count': 1000,
    'keywords': ['hot', 'trending']
}

product_id = db.insert_product(product)
print(f"产品已插入，ID: {product_id}")

# 查询产品
products = db.get_products(platform='tiktok', category='tshirt', limit=10)
for product in products:
    print(f"- {product['product_name']}: ${product['price']}")

# 关闭数据库
db.close()
```

### 2. 价格管理

```python
# 更新产品价格并记录历史
db.update_product_price(product_id=1, price=25.99, original_price=39.99)

# 获取价格历史
price_history = db.get_price_history(product_id=1, days=30)
for record in price_history:
    print(f"{record['recorded_at']}: ${record['price']}")
```

### 3. 评论管理

```python
# 添加评论
comment = {
    'comment_text': '这个产品真的很棒！',
    'comment_author': '用户123',
    'author_followers': 5000,
    'likes_count': 100,
    'replies_count': 5,
    'comment_date': '2025-11-14'
}

db.insert_hot_comment(product_id=1, comment_data=comment)

# 获取热门评论
comments = db.get_hot_comments(product_id=1, limit=10)
for comment in comments:
    print(f"评论: {comment['comment_text']} (点赞: {comment['likes_count']})")
```

### 4. 日志管理

```python
# 记录爬取任务日志
log_data = {
    'platform': 'tiktok',
    'category': 'tshirt',
    'task_type': 'full_scrape',
    'status': 'success',
    'records_found': 100,
    'records_saved': 95,
    'user_agent': 'Mozilla/5.0',
    'session_id': 'scrape_session_001'
}

log_id = db.insert_scrape_log(log_data)

# 更新日志完成状态
db.update_scrape_log(log_id, records_saved=98, status='success')

# 查询最近的日志
recent_logs = db.get_scrape_logs(platform='tiktok', days=7, limit=20)
```

### 5. 备份和恢复

```python
# 创建备份
backup_path = db.create_backup("backup_20251114.db")
print(f"备份已创建: {backup_path}")

# 从备份恢复
db.restore_backup(backup_path)

# 清理过期备份
db.cleanup_old_backups()
```

### 6. 统计信息

```python
# 获取数据库统计信息
stats = db.get_database_stats()
print("数据库统计:")
for key, value in stats.items():
    print(f"  {key}: {value}")
```

## 配置选项

```python
config = DatabaseConfig(
    db_path="data/products.db",           # 数据库文件路径
    backup_dir="data/backup",             # 备份目录
    connection_pool_size=10,              # 连接池大小
    backup_retention_days=7,              # 备份保留天数
    auto_backup=True,                     # 是否启用自动备份
    backup_interval_hours=24              # 备份间隔（小时）
)
```

## 数据库约束

### 数据验证
- 价格必须大于0
- 评分必须在0-5之间
- 平台必须是 'tiktok' 或 'amazon'
- 分类必须是 'tshirt', 'hoodie' 或 'sweatshirt'

### 自动索引
系统自动创建以下索引以提高查询性能：
- 平台和分类组合索引
- 最后更新时间索引
- 价格历史时间索引
- 评论点赞数索引

## 性能特性

### 连接池
- 默认连接池大小：10
- 支持并发访问
- 自动连接回收

### 查询优化
- 预编译语句
- 索引优化
- 分页查询支持

### 性能数据（基于测试）
- 批量插入100个产品：~46ms/个
- 查询操作：~9.5ms/次

## 错误处理

系统包含完整的错误处理机制：
- 数据库连接错误
- 数据验证错误
- 备份/恢复错误
- 并发访问错误

所有错误都会被记录到日志文件中，便于调试和监控。

## 日志记录

系统会自动记录以下信息：
- 数据库操作日志
- 错误和异常信息
- 性能统计
- 备份操作记录

日志文件：`database.log`

## 迁移到云端

该数据库设计支持渐进式升级：
1. **阶段一**: SQLite本地数据库（当前阶段）
2. **阶段二**: Supabase云数据库
3. **阶段三**: 企业级云数据库

在数据量超过10万条记录或需要多用户访问时，可以考虑迁移到Supabase。

## 注意事项

1. **文件路径**: 确保数据库目录有写入权限
2. **并发访问**: 大量并发访问时注意连接池配置
3. **备份策略**: 建议定期备份并测试恢复功能
4. **数据清理**: 定期清理过期数据保持性能
5. **监控**: 定期检查数据库大小和性能指标

## 故障排除

### 常见问题

**Q: 数据库文件锁定错误**
A: 检查是否有其他进程占用数据库文件，Windows系统可能需要重启。

**Q: 备份恢复失败**
A: 确认备份文件完整性，检查磁盘空间是否足够。

**Q: 性能下降**
A: 检查索引使用情况，必要时执行数据库优化，定期清理历史数据。

**Q: 并发访问错误**
A: 调整连接池大小，检查是否有长事务阻塞。

## 示例项目

查看 `test_database.py` 文件了解更多使用示例和测试用例。

## 许可证

本项目仅供学习和研究使用。