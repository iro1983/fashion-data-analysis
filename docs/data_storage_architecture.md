# TikTok & Amazon 热销服装数据存储架构设计

## 1. 架构概述

基于前期调研结果，设计一个**低成本、易扩展**的数据存储架构，满足每日自动抓取印花TSHIRT/卫衣/连帽衫数据的需求。

### 核心设计原则
- **低成本优先**：MVP阶段使用免费工具
- **渐进式升级**：SQLite → Supabase → 云原生
- **易维护**：适合无编程基础用户
- **数据完整**：确保价格、销量、评论、店铺链接完整存储

## 2. 数据库选择策略

### 阶段一：SQLite本地数据库（推荐起始方案）

**选择理由**：
- ✅ 完全免费，无需配置
- ✅ 轻量级，适合小数据量
- ✅ 数据持久化，本地备份
- ✅ 标准SQL语法，学习成本低
- ✅ 跨平台兼容（Windows/Mac/Linux）

**存储容量**：
- 每日新增：~500条记录
- 月存储需求：~15MB
- 年存储需求：~180MB

### 阶段二：Supabase云数据库（后续升级）

**升级时机**：
- 数据量超过10万条记录
- 需要多用户访问
- 自动化程度提升

**优势**：
- 云端存储，访问便利
- 内置API，自动生成接口
- 用户认证支持
- 定时函数支持

## 3. 数据库表结构设计

### 3.1 产品主表（products）

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本信息
    product_name TEXT NOT NULL,           -- 产品名称
    platform TEXT NOT NULL,               -- 平台 (tiktok/amazon)
    category TEXT NOT NULL,               -- 分类 (tshirt/hoodie/sweatshirt)
    
    -- 价格信息
    price DECIMAL(10,2),                  -- 当前价格
    original_price DECIMAL(10,2),         -- 原价
    currency TEXT DEFAULT 'USD',          -- 货币
    
    -- 销售数据
    sales_count INTEGER,                  -- 销量（估算）
    rating DECIMAL(3,2),                  -- 评分
    review_count INTEGER,                 -- 评价数量
    
    -- 链接信息
    product_url TEXT NOT NULL,            -- 产品链接
    store_url TEXT,                       -- 店铺链接
    store_name TEXT,                      -- 店铺名称
    
    -- 图像信息
    main_image_url TEXT,                  -- 主图链接
    image_urls TEXT,                      -- 图片URLs (JSON格式)
    
    -- 热度数据
    like_count INTEGER,                   -- 点赞数
    share_count INTEGER,                  -- 分享数
    comment_count INTEGER,                -- 评论数
    view_count INTEGER,                   -- 浏览量
    
    -- 时间和状态
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 首次发现时间
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 最后更新时间
    data_source TEXT,                     -- 数据来源
    is_active BOOLEAN DEFAULT 1,          -- 是否活跃
    
    -- 备注
    notes TEXT,                           -- 备注信息
    keywords TEXT                         -- 关键词 (JSON格式)
);
```

### 3.2 热度评论表（hot_comments）

```sql
CREATE TABLE hot_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,                   -- 产品ID (外键)
    
    -- 评论内容
    comment_text TEXT NOT NULL,           -- 评论内容
    comment_author TEXT,                  -- 评论者
    author_followers INTEGER,             -- 博主粉丝数
    
    -- 互动数据
    likes_count INTEGER DEFAULT 0,        -- 点赞数
    replies_count INTEGER DEFAULT 0,      -- 回复数
    
    -- 时间信息
    comment_date TIMESTAMP,               -- 评论时间
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 抓取时间
    
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

### 3.3 价格历史表（price_history）

```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,                   -- 产品ID (外键)
    
    -- 价格数据
    price DECIMAL(10,2) NOT NULL,         -- 价格
    original_price DECIMAL(10,2),         -- 原价
    discount_percent INTEGER,             -- 折扣百分比
    
    -- 时间信息
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 记录时间
    
    FOREIGN KEY (product_id) REFERENCES products (id)
);
```

### 3.4 爬取任务日志表（scrape_logs）

```sql
CREATE TABLE scrape_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 任务信息
    platform TEXT NOT NULL,               -- 平台
    category TEXT NOT NULL,               -- 分类
    task_type TEXT NOT NULL,              -- 任务类型 (full_scrape/price_update/comment_update)
    
    -- 执行结果
    status TEXT NOT NULL,                 -- 状态 (success/failed/partial)
    records_found INTEGER DEFAULT 0,      -- 发现记录数
    records_saved INTEGER DEFAULT 0,      -- 保存记录数
    error_message TEXT,                   -- 错误信息
    
    -- 时间信息
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,             -- 执行时长(秒)
    
    -- 元数据
    user_agent TEXT,                      -- 用户代理
    ip_address TEXT,                      -- IP地址
    session_id TEXT                       -- 会话ID
);
```

## 4. 索引优化设计

### 4.1 主要索引
```sql
-- 平台和分类查询优化
CREATE INDEX idx_products_platform_category ON products(platform, category);
CREATE INDEX idx_products_last_updated ON products(last_updated_at);
CREATE INDEX idx_products_active ON products(is_active, platform);

-- 价格历史查询优化
CREATE INDEX idx_price_history_product_date ON price_history(product_id, recorded_at);
CREATE INDEX idx_price_history_date ON price_history(recorded_at);

-- 热度评论查询优化
CREATE INDEX idx_hot_comments_product ON hot_comments(product_id);
CREATE INDEX idx_hot_comments_likes ON hot_comments(likes_count DESC);

-- 爬取日志查询优化
CREATE INDEX idx_scrape_logs_platform_date ON scrape_logs(platform, started_at);
CREATE INDEX idx_scrape_logs_status ON scrape_logs(status, started_at);
```

## 5. 数据更新策略

### 5.1 自动更新频率

| 数据类型 | 更新频率 | 更新策略 |
|---------|---------|---------|
| 产品基本信息 | 每日 | 检查新产品+更新现有产品 |
| 价格数据 | 每日 | 定时更新+价格变化提醒 |
| 销量数据 | 每日 | 估算更新+趋势分析 |
| 热度评论 | 每2-3日 | 抓取热门评论+情感分析 |
| 店铺信息 | 每周 | 检查店铺变化+新增店铺 |

### 5.2 数据去重策略

```python
# Python数据去重逻辑示例
def deduplicate_products(new_products):
    """
    基于product_url去重，保留最新数据
    """
    existing_urls = get_existing_urls()
    unique_products = []
    
    for product in new_products:
        if product['product_url'] not in existing_urls:
            unique_products.append(product)
            existing_urls.add(product['product_url'])
    
    return unique_products
```

### 5.3 数据验证规则

```sql
-- 价格验证
ALTER TABLE products ADD CONSTRAINT chk_price_positive CHECK (price > 0);

-- 评分范围验证
ALTER TABLE products ADD CONSTRAINT chk_rating_range CHECK (rating >= 0 AND rating <= 5);

-- 平台枚举验证
ALTER TABLE products ADD CONSTRAINT chk_platform_enum CHECK (platform IN ('tiktok', 'amazon'));

-- 分类枚举验证
ALTER TABLE products ADD CONSTRAINT chk_category_enum CHECK (category IN ('tshirt', 'hoodie', 'sweatshirt'));
```

## 6. 备份与恢复策略

### 6.1 本地备份（SQLite阶段）
```bash
# 每日自动备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp data/products.db "backup/products_backup_$DATE.db"

# 保留最近7天的备份
find backup/ -name "products_backup_*.db" -mtime +7 -delete
```

### 6.2 云端同步（Supabase阶段）
- 实时数据同步
- 自动备份到云存储
- 跨设备数据访问

## 7. 性能优化建议

### 7.1 查询优化
```sql
-- 常用查询模式
-- 1. 获取最新产品（最近24小时）
SELECT * FROM products 
WHERE last_updated_at >= datetime('now', '-1 day')
ORDER BY last_updated_at DESC;

-- 2. 价格趋势分析
SELECT p.product_name, ph.price, ph.recorded_at
FROM products p
JOIN price_history ph ON p.id = ph.product_id
WHERE p.category = 'tshirt'
ORDER BY ph.recorded_at;

-- 3. 热门产品排行
SELECT product_name, rating, review_count, sales_count
FROM products
WHERE platform = 'amazon' AND is_active = 1
ORDER BY (rating * 0.3 + sales_count * 0.7) DESC
LIMIT 50;
```

### 7.2 数据分区策略
```sql
-- 按月份分区（当数据量大时）
CREATE TABLE products_2025_01 PARTITION OF products
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

## 8. 实施计划

### 8.1 第一周：基础架构
- [ ] 创建SQLite数据库和表结构
- [ ] 建立数据模型和验证规则
- [ ] 实现基本的增删改查功能

### 8.2 第二周：数据处理
- [ ] 开发数据清洗和去重逻辑
- [ ] 实现自动备份机制
- [ ] 创建数据验证脚本

### 8.3 第三周：性能优化
- [ ] 建立索引优化策略
- [ ] 实现缓存机制
- [ ] 创建性能监控仪表板

### 8.4 第四周：云端迁移
- [ ] Supabase数据迁移
- [ ] API接口开发
- [ ] 自动化部署测试

## 9. 成本估算

### 9.1 本地阶段成本（SQLite）
| 项目 | 成本 | 说明 |
|------|------|------|
| 数据库 | $0 | SQLite免费 |
| 存储 | $0 | 本地存储 |
| 备份 | $0 | 本地+云盘备份 |
| **总计** | **$0** | **完全免费** |

### 9.2 云端阶段成本（Supabase）
| 项目 | 免费额度 | 付费成本 |
|------|----------|----------|
| 数据库存储 | 500MB | $25/GB/月 |
| API请求 | 500K/月 | $0.0001/请求 |
| 实时连接 | 2个 | $5/连接/月 |
| **总计** | **免费** | **$30-50/月** |

## 10. 风险控制

### 10.1 数据丢失风险
- **预防**：每日自动备份 + 云端同步
- **恢复**：备份恢复脚本 + 数据验证

### 10.2 数据库损坏风险
- **预防**：事务处理 + 写入验证
- **恢复**：SQLite修复工具 + 备份恢复

### 10.3 性能下降风险
- **预防**：定期索引重建 + 数据归档
- **优化**：查询优化 + 分区策略

## 11. 扩展性设计

### 11.1 水平扩展
- 读写分离
- 分库分表
- 分布式缓存

### 11.2 功能扩展
- 用户权限管理
- 数据导出功能
- 报告生成
- API开放

## 12. 监控与告警

### 12.1 关键指标
```sql
-- 数据库大小监控
SELECT 
    'database_size' as metric,
    page_count * page_size / 1024 / 1024 as size_mb
FROM pragma_page_count(), pragma_page_size();

-- 最新记录统计
SELECT 
    DATE(last_updated_at) as date,
    COUNT(*) as count
FROM products 
GROUP BY DATE(last_updated_at)
ORDER BY date DESC;
```

### 12.2 自动告警
- 数据库大小超阈值
- 爬取任务失败率过高
- 数据质量异常
- 备份失败

---

**总结**：该架构设计既满足了MVP阶段的低成本需求，又为未来的扩展升级预留了空间。通过渐进式的发展路径，可以确保项目在有限预算下快速上线，同时具备良好的扩展性。