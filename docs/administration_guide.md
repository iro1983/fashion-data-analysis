# 管理维护指南

本文档详细介绍系统的安装、配置、监控和维护操作，适用于系统管理员和运维人员。

## 📋 目录

- [系统安装与部署](#系统安装与部署)
- [配置管理](#配置管理)
- [数据库管理](#数据库管理)
- [监控与告警](#监控与告警)
- [数据抓取管理](#数据抓取管理)
- [系统优化](#系统优化)
- [备份与恢复](#备份与恢复)
- [安全设置](#安全设置)

## 系统安装与部署

### 环境准备

#### 系统要求
- **操作系统**：Ubuntu 18.04+ / CentOS 7+ / Windows 10+ / macOS 10.15+
- **CPU**：至少2核，推荐4核+
- **内存**：最少4GB，推荐8GB+
- **存储**：最少10GB可用空间，推荐50GB+
- **网络**：稳定的互联网连接，建议带宽10Mbps+

#### 依赖软件安装

**Ubuntu/Debian系统**：
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装Node.js (前端仪表板需要)
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs -y

# 安装SQLite
sudo apt install sqlite3 -y

# 安装其他必要工具
sudo apt install git curl wget unzip -y
```

**CentOS/RHEL系统**：
```bash
# 安装EPEL仓库
sudo yum install epel-release -y

# 安装Python和pip
sudo yum install python3 python3-pip -y

# 安装Node.js
curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install nodejs -y

# 安装SQLite
sudo yum install sqlite -y
```

**macOS系统**：
```bash
# 安装Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python3 node sqlite
```

### 部署步骤

#### 1. 项目文件部署

```bash
# 创建项目目录
sudo mkdir -p /opt/tiktok-amazon-system
cd /opt/tiktok-amazon-system

# 复制项目文件（假设从源码仓库获取）
git clone <repository-url> .
# 或者
# wget <download-url> && unzip <archive-file>

# 设置目录权限
sudo chown -R $USER:$USER /opt/tiktok-amazon-system
chmod +x run.sh
```

#### 2. Python环境配置

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 验证安装
python main.py --help
```

#### 3. 前端仪表板部署

```bash
# 进入前端目录
cd fashion-dashboard

# 安装依赖
npm install

# 构建生产版本
npm run build

# 使用静态文件服务器部署
npm install -g serve
serve -s dist -l 3000
```

### 生产环境部署

#### 使用systemd服务（Linux）

创建服务文件 `/etc/systemd/system/tiktok-amazon-scraper.service`：

```ini
[Unit]
Description=TikTok Amazon Scraper Service
After=network.target

[Service]
Type=simple
User=scraper
Group=scraper
WorkingDirectory=/opt/tiktok-amazon-system
Environment=PATH=/opt/tiktok-amazon-system/venv/bin
ExecStart=/opt/tiktok-amazon-system/venv/bin/python main.py daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable tiktok-amazon-scraper
sudo systemctl start tiktok-amazon-scraper
sudo systemctl status tiktok-amazon-scraper
```

#### 使用Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py", "daemon"]
```

构建和运行：
```bash
# 构建镜像
docker build -t tiktok-amazon-scraper .

# 运行容器
docker run -d \
  --name scraper-service \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  tiktok-amazon-scraper
```

## 配置管理

### 配置文件结构

系统使用YAML格式的配置文件，主要配置文件为 `config/config.yaml`：

```yaml
# 完整配置示例
database:
  type: sqlite
  path: data/scraping.db
  backup_enabled: true
  backup_interval: "24h"
  connection_pool_size: 10

scraping:
  amazon:
    enabled: true
    max_concurrent: 3
    request_delay: 1.0
    timeout: 30
    user_agent: "Mozilla/5.0..."
    categories:
      - "T-Shirt"
      - "Hoodie"
      - "Sweatshirt"
    keywords:
      - "print"
      - "graphic"
      - "design"
    proxy:
      enabled: false
      url: ""
      username: ""
      password: ""
  
  tiktok:
    enabled: true
    max_concurrent: 2
    request_delay: 2.0
    timeout: 30
    categories:
      - "服装"
      - "时尚"
      - "潮流"
    keywords:
      - "印花"
      - "T恤"
      - "卫衣"

retry:
  max_retries: 3
  backoff_factor: 2
  retry_delay: 5
  max_retry_delay: 300

monitoring:
  log_level: INFO
  performance_tracking: true
  alert_thresholds:
    failure_rate: 0.3
    avg_response_time: 30
    memory_usage: 80
    disk_usage: 90
  notification:
    email:
      enabled: false
      smtp_server: ""
      smtp_port: 587
      username: ""
      password: ""
      recipients: []

advanced:
  deduplication:
    enabled: true
    strategy: "product_id"
    cache_ttl: 3600
  
  data_validation:
    enabled: true
    strict_mode: false
    required_fields:
      - "title"
      - "price"
      - "url"
  
  output:
    format: "json"
    compress: false
    max_file_size: "100MB"
    export_path: "exports/"

security:
  api_rate_limit: 1000
  request_signature: true
  encryption_key: ""
  access_log: true
```

### 配置管理命令

#### 查看当前配置

```bash
# 查看所有配置
python main.py config show

# 查看特定模块配置
python main.py config show scraping.amazon

# 查看特定配置项
python main.py config get scraping.amazon.max_concurrent
```

#### 修改配置

```bash
# 设置配置项
python main.py config set scraping.amazon.max_concurrent 5
python main.py config set monitoring.log_level DEBUG

# 批量设置
python main.py config set-batch config/quick_settings.yaml
```

#### 配置验证

```bash
# 验证配置文件语法
python main.py config validate

# 测试连接配置
python main.py config test-connections

# 生成配置差异报告
python main.py config diff config/backup_config.yaml
```

### 环境变量配置

某些配置也可以通过环境变量设置：

```bash
# 数据库配置
export SCRAPER_DB_PATH="/custom/path/scraping.db"
export SCRAPER_DB_BACKUP_ENABLED="true"

# 代理配置
export SCRAPER_PROXY_URL="http://proxy.example.com:8080"
export SCRAPER_PROXY_USERNAME="user"
export SCRAPER_PROXY_PASSWORD="pass"

# 通知配置
export SCRAPER_EMAIL_SMTP_SERVER="smtp.example.com"
export SCRAPER_EMAIL_USERNAME="notification@example.com"
export SCRAPER_EMAIL_PASSWORD="password"
```

## 数据库管理

### 数据库结构

系统使用SQLite数据库，主要表结构：

#### 产品表 (products)
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform VARCHAR(50) NOT NULL,           -- 'amazon' 或 'tiktok'
    product_id VARCHAR(255) UNIQUE NOT NULL, -- 平台产品ID
    title TEXT NOT NULL,                      -- 产品标题
    brand VARCHAR(255),                       -- 品牌
    price DECIMAL(10,2),                      -- 价格
    currency VARCHAR(3) DEFAULT 'USD',        -- 货币
    category VARCHAR(255),                    -- 分类
    subcategory VARCHAR(255),                 -- 子分类
    rating DECIMAL(3,2),                      -- 评分
    review_count INTEGER DEFAULT 0,           -- 评价数量
    sales_rank INTEGER,                       -- 销量排名
    availability VARCHAR(50),                 -- 库存状态
    url TEXT,                                 -- 产品链接
    image_url TEXT,                           -- 图片链接
    description TEXT,                         -- 描述
    features TEXT,                            -- 特性JSON
    specifications TEXT,                      -- 规格JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_scraped DATETIME,                    -- 最后抓取时间
    
    INDEX idx_platform (platform),
    INDEX idx_category (category),
    INDEX idx_price (price),
    INDEX idx_platform_id (platform, product_id),
    INDEX idx_created (created_at),
    INDEX idx_last_scraped (last_scraped)
);
```

#### 抓取任务表 (scraping_tasks)
```sql
CREATE TABLE scraping_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    category VARCHAR(255),
    keywords TEXT,                            -- 关键词JSON数组
    status VARCHAR(50) DEFAULT 'pending',     -- 'pending', 'running', 'completed', 'failed'
    start_time DATETIME,
    end_time DATETIME,
    products_found INTEGER DEFAULT 0,
    products_new INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_platform (platform),
    INDEX idx_status (status),
    INDEX idx_created (created_at),
    INDEX idx_platform_status (platform, status)
);
```

#### 系统日志表 (system_logs)
```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(20) NOT NULL,               -- 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    module VARCHAR(100) NOT NULL,             -- 模块名称
    message TEXT NOT NULL,                    -- 日志消息
    details TEXT,                             -- 详细信息JSON
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    task_id VARCHAR(255),                     -- 关联任务ID
    
    INDEX idx_level (level),
    INDEX idx_module (module),
    INDEX idx_timestamp (timestamp),
    INDEX idx_task_id (task_id)
);
```

### 数据库操作

#### 日常维护命令

```bash
# 数据库状态检查
python main.py db status

# 数据库信息统计
python main.py db stats

# 数据清理
python main.py db cleanup --older-than 30    # 清理30天前的数据
python main.py db cleanup --empty-categories # 清理空分类
python main.py db cleanup --duplicates       # 清理重复数据

# 数据库优化
python main.py db optimize                   # 重建索引，压缩数据库
python main.py db vacuum                     # 清理碎片空间
```

#### 备份与恢复

```bash
# 手动备份
python main.py db backup --path /backup/scraping_$(date +%Y%m%d).db

# 自动备份设置
python main.py config set database.backup_enabled true
python main.py config set database.backup_interval "24h"
python main.py config set database.backup_path "/backup/"

# 备份恢复
python main.py db restore --path /backup/scraping_20231114.db
```

#### 数据导入导出

```bash
# 导出数据
python export_data.py --format json --output products.json
python export_data.py --format csv --output products.csv --platform amazon

# 导入数据
python import_data.py --file products_import.json --merge   # 合并模式
python import_data.py --file products_import.json --replace # 替换模式
```

### 性能优化

#### 查询优化

```sql
-- 分析查询性能
EXPLAIN QUERY PLAN SELECT * FROM products WHERE platform = 'amazon' AND price BETWEEN 50 AND 100;
EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'T-Shirt' ORDER BY created_at DESC LIMIT 100;

-- 创建复合索引（如果查询频繁）
CREATE INDEX idx_platform_category_price ON products(platform, category, price);
CREATE INDEX idx_platform_created ON products(platform, created_at);

-- 清理过期统计信息
ANALYZE products;
ANALYZE scraping_tasks;
ANALYZE system_logs;
```

#### 数据库维护脚本

创建自动维护脚本 `scripts/db_maintenance.sh`：

```bash
#!/bin/bash

# 数据库维护脚本
DB_PATH="/opt/tiktok-amazon-system/data/scraping.db"
BACKUP_PATH="/backup/scraping"
LOG_FILE="/var/log/scraper-db-maintenance.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "开始数据库维护"

# 1. 备份数据库
log_message "创建数据库备份"
cp "$DB_PATH" "$BACKUP_PATH/scraping_$(date +%Y%m%d_%H%M%S).db"

# 2. 清理旧数据（保留30天）
log_message "清理30天前的数据"
sqlite3 "$DB_PATH" "DELETE FROM products WHERE created_at < datetime('now', '-30 days');"
sqlite3 "$DB_PATH" "DELETE FROM system_logs WHERE timestamp < datetime('now', '-30 days');"

# 3. 清理空分类产品
log_message "清理空分类产品"
sqlite3 "$DB_PATH" "DELETE FROM products WHERE category IS NULL OR category = '';"

# 4. 重建索引
log_message "重建数据库索引"
sqlite3 "$DB_PATH" "REINDEX;"

# 5. 压缩数据库
log_message "压缩数据库"
sqlite3 "$DB_PATH" "VACUUM;"

# 6. 分析数据库统计
log_message "更新数据库统计"
sqlite3 "$DB_PATH" "ANALYZE;"

# 7. 清理备份文件（保留最近7天）
find "$BACKUP_PATH" -name "scraping_*.db" -mtime +7 -delete

log_message "数据库维护完成"
```

设置定时任务：
```bash
# 编辑crontab
crontab -e

# 添加每日凌晨2点执行维护
0 2 * * * /opt/tiktok-amazon-system/scripts/db_maintenance.sh
```

## 监控与告警

### 日志配置

#### 日志级别设置

```yaml
# config/config.yaml
monitoring:
  log_level: INFO                    # DEBUG, INFO, WARNING, ERROR
  log_format: "json"                 # "text" 或 "json"
  log_rotation:
    max_size: "100MB"               # 单个日志文件最大大小
    backup_count: 10                # 保留的日志文件数量
    compress: true                   # 是否压缩历史日志
  
  # 文件路径配置
  log_files:
    main: "logs/coordinator.log"
    scraping: "logs/scraping.log"
    database: "logs/database.log"
    errors: "logs/errors.log"
```

#### 日志查看命令

```bash
# 实时查看主要日志
tail -f logs/coordinator.log

# 查看错误日志
tail -f logs/errors.log

# 搜索特定错误
grep "ERROR" logs/coordinator.log | tail -20

# 按时间范围查看日志
grep "2025-11-14 10:" logs/coordinator.log

# 查看特定模块日志
grep "AmazonScraper" logs/scraping.log
```

### 性能监控

#### 系统指标监控

```bash
# CPU和内存使用率
python main.py monitor system --metrics cpu,memory,disk

# 抓取性能统计
python main.py monitor scraping --period 24h

# 数据库性能分析
python main.py monitor database --slow-queries

# 网络请求统计
python main.py monitor network --by-platform
```

#### 实时监控脚本

创建监控脚本 `scripts/monitor.sh`：

```bash
#!/bin/bash

# 系统监控脚本
MONITOR_LOG="/var/log/scraper-monitor.log"
ALERT_EMAIL="admin@example.com"

check_system_health() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    echo "[$(date)] CPU: ${cpu_usage}%, Memory: ${mem_usage}%, Disk: ${disk_usage}%" >> "$MONITOR_LOG"
    
    # 检查告警阈值
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        send_alert "CPU使用率过高: ${cpu_usage}%"
    fi
    
    if (( $(echo "$mem_usage > 85" | bc -l) )); then
        send_alert "内存使用率过高: ${mem_usage}%"
    fi
    
    if (( disk_usage > 90 )); then
        send_alert "磁盘使用率过高: ${disk_usage}%"
    fi
}

check_scraper_status() {
    local running_tasks=$(python main.py status --json | jq '.running_tasks')
    local failed_tasks=$(python main.py status --json | jq '.failed_tasks')
    local success_rate=$(python main.py status --json | jq '.success_rate')
    
    if (( $(echo "$success_rate < 0.8" | bc -l) )); then
        send_alert "抓取成功率过低: $success_rate"
    fi
    
    if (( failed_tasks > 5 )); then
        send_alert "失败任务数量过多: $failed_tasks"
    fi
}

send_alert() {
    local message="$1"
    echo "[ALERT] $message" >> "$MONITOR_LOG"
    
    # 发送邮件告警（需要配置邮件系统）
    # echo "$message" | mail -s "Scraper Alert" "$ALERT_EMAIL"
    
    # 发送到日志系统
    logger -t scraper-monitor "$message"
}

# 执行检查
check_system_health
check_scraper_status
```

### 告警配置

#### 邮件告警设置

```yaml
# config/config.yaml
monitoring:
  notification:
    email:
      enabled: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"  # 使用应用专用密码
      use_tls: true
      recipients:
        - "admin@example.com"
        - "ops-team@example.com"
      
    # 告警规则
    alert_rules:
      - name: "high_failure_rate"
        condition: "scraping.success_rate < 0.8"
        threshold: 3                 # 连续3次检查都触发才发送
        interval: "5m"               # 检查间隔
        message: "抓取任务失败率超过80%"
      
      - name: "system_resources"
        condition: "system.cpu_usage > 80 OR system.memory_usage > 85"
        threshold: 2
        interval: "1m"
        message: "系统资源使用率过高"
      
      - name: "database_issues"
        condition: "database.connection_errors > 0"
        threshold: 1
        interval: "30s"
        message: "数据库连接出现问题"
```

#### 告警测试

```bash
# 测试邮件告警
python main.py alert test --type email --message "这是一条测试告警消息"

# 测试所有告警规则
python main.py alert test --all

# 手动触发告警检查
python main.py alert check --now
```

## 数据抓取管理

### 任务调度

#### 定时抓取设置

```bash
# 添加定时任务
python main.py schedule add --name "amazon-morning" \
    --platform amazon \
    --cron "0 8 * * *" \
    --category "T-Shirt,Hoodie" \
    --keywords "print,graphic"

python main.py schedule add --name "tiktok-evening" \
    --platform tiktok \
    --cron "0 18 * * *" \
    --category "服装,时尚"

# 查看定时任务
python main.py schedule list

# 删除定时任务
python main.py schedule remove amazon-morning

# 启用/禁用任务
python main.py schedule enable amazon-morning
python main.py schedule disable tiktok-evening
```

#### 手动任务控制

```bash
# 开始新的抓取任务
python main.py scrape start --platform amazon --async

# 查看运行中的任务
python main.py task list --status running

# 停止任务
python main.py task stop <task-id>

# 重启失败的任务
python main.py task restart --platform amazon --since "2025-11-14 10:00"
```

### 抓取优化

#### 并发控制

```yaml
# 性能调优配置
scraping:
  amazon:
    # 基础并发设置
    max_concurrent: 3
    request_delay: 1.0
    
    # 高级优化设置
    connection_pool_size: 10
    timeout: 30
    retry_count: 3
    
    # 平台特定优化
    rate_limit:
      requests_per_minute: 60
      burst_limit: 10
    
    # 代理设置（可选）
    proxy:
      enabled: false
      rotation: false
      pool_size: 5
```

#### 数据质量控制

```yaml
# 数据验证配置
advanced:
  data_validation:
    enabled: true
    strict_mode: false
    
    # 必填字段验证
    required_fields:
      - "title"
      - "price" 
      - "url"
      - "platform"
    
    # 数据清洗规则
    cleaning_rules:
      - field: "title"
        rules:
          - "remove_html_tags"
          - "trim_whitespace"
          - "normalize_case"
      
      - field: "price"
        rules:
          - "extract_numeric"
          - "validate_currency"
          - "range_check:0,10000"
    
    # 重复数据检测
    deduplication:
      enabled: true
      strategy: "product_id"    # product_id, url, title, fingerprint
      confidence_threshold: 0.8
      
  # 质量评分系统
  quality_scoring:
    enabled: true
    weights:
      completeness: 0.3        # 数据完整度权重
      accuracy: 0.4            # 数据准确度权重
      freshness: 0.3           # 数据新鲜度权重
```

### 错误处理

#### 常见错误处理

```bash
# 查看失败任务详情
python main.py task details <failed-task-id> --errors

# 分析错误模式
python main.py error analysis --period 7d --by-type

# 清理失败任务
python main.py task cleanup --status failed --older-than 7d

# 错误统计报告
python main.py report error-trends --format html --output error_report.html
```

#### 错误恢复策略

```yaml
# config/config.yaml
retry:
  # 基础重试配置
  max_retries: 3
  backoff_factor: 2
  retry_delay: 5
  max_retry_delay: 300
  
  # 按错误类型定制策略
  error_strategies:
    "ConnectionError":
      max_retries: 5
      backoff_factor: 3
      retry_delay: 10
    
    "TimeoutError":
      max_retries: 3
      backoff_factor: 1.5
      retry_delay: 5
    
    "RateLimitError":
      max_retries: 2
      backoff_factor: 1
      retry_delay: 60
    
    "ValidationError":
      max_retries: 0         # 不重试验证错误
      skip_error: true

# 故障转移设置
failover:
  enabled: true
  proxy_rotation: true
  fallback_platforms:
    - "backup_amazon_endpoint"
    - "backup_tiktok_endpoint"
```

## 系统优化

### 性能调优

#### 系统级优化

```bash
# 检查系统资源使用情况
python main.py system resource-check

# 优化系统设置
# Linux系统
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
sysctl -p

# 数据库优化设置
python main.py config set database.optimization_enabled true
python main.py config set database.auto_vacuum true
python main.py config set database.cache_size 10000
```

#### 应用级优化

```yaml
# 性能调优配置
performance:
  # 内存管理
  memory:
    max_heap_size: "2GB"
    gc_threshold: 700
    object_cache_size: 1000
  
  # 缓存配置
  cache:
    enabled: true
    backend: "redis"              # "memory", "redis", "disk"
    ttl: 3600                     # 缓存生存时间
    max_size: "500MB"
    
    # Redis配置（如果使用Redis）
    redis:
      host: "localhost"
      port: 6379
      password: ""
      db: 0
  
  # 连接池配置
  connection_pool:
    enabled: true
    max_connections: 20
    min_connections: 5
    idle_timeout: 300
    connection_timeout: 30
```

### 容量规划

#### 存储容量计算

```bash
# 估算存储需求
python main.py capacity estimate \
    --daily-products 1000 \
    --retention-days 90 \
    --products-per-category 100

# 输出示例:
# 估算结果:
# - 每日新增产品: 1000个
# - 保留天数: 90天
# - 预计数据库大小: 2.3GB
# - 预计日志文件大小: 500MB
# - 总存储需求: 2.8GB
```

#### 扩容建议

```bash
# 性能基准测试
python main.py benchmark --duration 1h --load normal

# 扩容方案建议
python main.py scaling recommendation \
    --current-throughput 1000 \
    --target-throughput 5000
```

## 备份与恢复

### 自动化备份

#### 备份策略配置

```yaml
# backup策略配置
backup:
  enabled: true
  schedule:
    # 完整备份
    full_backup:
      enabled: true
      cron: "0 2 * * 0"         # 每周日凌晨2点
      retention: 4               # 保留4周
    
    # 增量备份  
    incremental_backup:
      enabled: true
      cron: "0 2 * * 1-6"       # 每天凌晨2点（周日除外）
      retention: 7               # 保留7天
  
  # 备份位置
  locations:
    local:
      path: "/backup/scraper/"
      compression: true
      encryption: false
    
    remote:
      enabled: false
      type: "s3"                 # "s3", "ftp", "sftp"
      bucket: "scraper-backups"
      region: "us-east-1"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
  
  # 备份内容
  include:
    - "data/scraping.db"
    - "logs/"
    - "config/"
    - "exports/"
  
  exclude:
    - "*.tmp"
    - "cache/"
    - "temp/"
```

#### 备份执行命令

```bash
# 手动执行完整备份
python main.py backup create --type full --comment "手动备份-$(date +%Y%m%d)"

# 手动执行增量备份
python main.py backup create --type incremental

# 查看备份历史
python main.py backup list --count 10

# 验证备份完整性
python main.py backup verify <backup-id>

# 清理过期备份
python main.py backup cleanup --older-than 30d
```

### 灾难恢复

#### 恢复流程

```bash
# 1. 停止服务
sudo systemctl stop tiktok-amazon-scraper

# 2. 备份当前数据
cp data/scraping.db data/scraping.db.emergency_backup

# 3. 从备份恢复
python main.py backup restore <backup-id> --target data/scraping.db

# 4. 验证数据完整性
python main.py db verify --fix-errors

# 5. 重启服务
sudo systemctl start tiktok-amazon-scraper

# 6. 验证服务状态
python main.py health-check
```

#### 灾难恢复计划

创建灾难恢复文档 `disaster_recovery.md`：

```markdown
# 灾难恢复计划

## 恢复目标时间 (RTO): 2小时
## 恢复点目标 (RPO): 24小时

## 恢复步骤

### 1. 服务中断 (< 5分钟)
- 停止所有相关服务
- 保护现场数据
- 通知相关人员

### 2. 环境重建 (30分钟)
- 重新部署系统环境
- 恢复配置文件
- 恢复数据库备份

### 3. 服务恢复 (60分钟)  
- 启动所有服务组件
- 验证数据完整性
- 执行功能测试

### 4. 业务验证 (25分钟)
- 验证核心功能
- 监控系统性能
- 用户验收测试

## 关键联系人
- 系统管理员: admin@example.com
- 技术支持: support@example.com  
- 业务负责人: business@example.com

## 资源清单
- 备用服务器: backup-server-01
- 备份存储: /backup/scraper/
- 恢复文档: /docs/disaster_recovery.md
```

## 安全设置

### 访问控制

#### 配置文件安全

```bash
# 设置配置文件权限
chmod 600 config/config.yaml
chown scraper:scraper config/config.yaml

# 加密敏感信息
python main.py config encrypt-secrets --output config/secrets.enc

# 验证配置文件完整性
python main.py config verify-integrity
```

#### API安全

```yaml
# 安全配置
security:
  # API访问控制
  api:
    rate_limit:
      enabled: true
      requests_per_minute: 100
      burst_limit: 20
    
    authentication:
      enabled: true
      method: "token"           # "token", "oauth", "basic"
      token_expiry: "24h"
    
    cors:
      enabled: true
      allowed_origins:
        - "https://dashboard.example.com"
        - "https://app.example.com"
      allowed_methods:
        - "GET"
        - "POST"
      allowed_headers:
        - "Content-Type"
        - "Authorization"
  
  # 数据加密
  encryption:
    enabled: true
    algorithm: "AES-256-GCM"
    key_rotation: "90d"        # 密钥轮换周期
  
  # 审计日志
  audit:
    enabled: true
    log_access: true
    log_changes: true
    retention: "1y"
```

#### 网络安全

```bash
# 配置防火墙规则
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 8000/tcp    # API服务
sudo ufw deny 3000/tcp     # 拒绝直接访问前端
sudo ufw enable

# 使用反向代理 (Nginx)
cat > /etc/nginx/sites-available/scraper << EOF
server {
    listen 80;
    server_name scraper.example.com;
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 限流
        limit_req zone=api burst=10 nodelay;
    }
    
    location / {
        root /opt/tiktok-amazon-system/fashion-dashboard/dist;
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/scraper /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 合规性管理

#### 数据合规检查

```bash
# 数据合规扫描
python main.py compliance scan --platform amazon --scope privacy

# 生成合规报告
python main.py compliance report --format pdf --output compliance_report.pdf

# 自动化合规检查
python main.py compliance monitor --alert-email admin@example.com
```

---

## 总结

本文档涵盖了TikTok & Amazon服装数据系统的完整管理维护操作，包括：

- **系统部署**：从安装到生产的完整流程
- **配置管理**：灵活的YAML配置系统
- **数据库管理**：性能优化和维护
- **监控告警**：全面的系统监控方案
- **备份恢复**：可靠的灾难恢复计划
- **安全设置**：生产环境安全配置

遵循本指南可以确保系统稳定、安全、高效地运行。如需更多技术细节，请参考API参考文档或联系技术支持团队。