# 故障排除指南

本文档提供TikTok & Amazon服装数据系统常见问题的诊断和解决方案，帮助用户快速定位和解决问题。

## 📋 目录

- [诊断工具](#诊断工具)
- [常见问题分类](#常见问题分类)
- [安装部署问题](#安装部署问题)
- [运行执行问题](#运行执行问题)
- [数据质量问题](#数据质量问题)
- [性能问题](#性能问题)
- [数据库问题](#数据库问题)
- [网络连接问题](#网络连接问题)
- [配置文件问题](#配置文件问题)
- [前端仪表板问题](#前端仪表板问题)
- [错误日志分析](#错误日志分析)
- [性能优化建议](#性能优化建议)

## 诊断工具

### 系统健康检查

#### 快速健康检查

```bash
# 全面系统健康检查
python main.py health-check --verbose

# 检查结果示例:
✅ 数据库连接: 正常
✅ 配置文件: 有效
✅ 依赖包: 已安装
⚠️  网络连接: Amazon连接超时
❌ 磁盘空间: 不足 (剩余 2GB)
❌ 内存使用: 过高 (85%)
```

#### 组件状态检查

```bash
# 检查各个组件状态
python main.py status --detailed

# 检查数据库状态
python main.py db status --verbose

# 检查抓取任务状态
python main.py task status --all

# 检查系统资源
python main.py system resources
```

#### 网络连接测试

```bash
# 测试所有平台连接
python main.py network test --all-platforms

# 测试特定平台
python main.py network test --platform amazon --timeout 30

# 详细网络诊断
python main.py network diagnose --verbose
```

### 日志分析工具

#### 日志查看命令

```bash
# 实时日志监控
tail -f logs/coordinator.log

# 查看特定级别的日志
grep "ERROR" logs/coordinator.log
grep "WARNING" logs/coordinator.log

# 按时间范围查看日志
grep "2025-11-14 10:" logs/coordinator.log

# 搜索特定模块日志
grep "AmazonScraper" logs/scraping.log

# 格式化输出日志
python main.py log analyze --format table --level ERROR --since "1h"
```

#### 错误统计

```bash
# 错误类型统计
python main.py error statistics --period 24h

# 错误趋势分析
python main.py error trends --format chart --period 7d

# 最常见错误排行
python main.py error top-errors --count 10
```

## 常见问题分类

### 按症状分类

| 问题症状 | 可能原因 | 快速解决 |
|---------|---------|---------|
| 无法启动 | 依赖缺失、配置错误 | 运行 `python main.py health-check` |
| 抓取失败 | 网络问题、平台限制 | 检查网络连接和配置 |
| 数据为空 | 关键词无效、选择器错误 | 验证配置和关键词 |
| 速度慢 | 并发过高、资源不足 | 调整并发数，检查系统资源 |
| 内存不足 | 数据量过大、缓存问题 | 清理数据，调整内存设置 |

### 按组件分类

- **数据库相关**：`database is locked`、`disk space`、`corruption`
- **网络相关**：`connection timeout`、`rate limit`、`proxy error`
- **配置相关**：`invalid yaml`、`missing parameter`、`permission denied`
- **依赖相关**：`module not found`、`version conflict`、`install failed`

## 安装部署问题

### 依赖安装失败

#### 问题：pip install失败

**症状**：
```bash
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**解决方案**：
```bash
# 方案1: 使用用户安装
pip install --user -r requirements.txt

# 方案2: 使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 方案3: 修复权限（Linux/macOS）
sudo chown -R $USER:$USER /path/to/project
chmod +x run.sh
```

#### 问题：版本冲突

**症状**：
```
ERROR: pip's dependency resolver does not currently work with packages that have conflicting dependencies
```

**解决方案**：
```bash
# 检查依赖冲突
pip check

# 升级pip和setuptools
pip install --upgrade pip setuptools

# 使用conda管理依赖（推荐）
conda create -n scraper python=3.9
conda activate scraper
conda install -c conda-forge requests beautifulsoup4 lxml

# 逐个安装依赖
pip install requests
pip install beautifulsoup4
pip install lxml
# ... 继续其他依赖
```

### Python环境问题

#### 问题：Python版本不兼容

**症状**：
```bash
SyntaxError: invalid syntax
# 或者
ImportError: module 'xxx' has no attribute 'yyy'
```

**解决方案**：
```bash
# 检查Python版本
python --version  # 需要 Python 3.8+

# 如果版本过低，升级Python
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv

# CentOS/RHEL
sudo yum install python39 python39-venv

# macOS (使用Homebrew)
brew install python@3.9

# 设置默认Python版本
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
```

#### 问题：模块导入错误

**症状**：
```bash
ModuleNotFoundError: No module named 'requests'
```

**解决方案**：
```bash
# 检查虚拟环境是否激活
which python
# 应该显示: /path/to/venv/bin/python

# 重新安装缺失模块
pip install requests beautifulsoup4 lxml pyyaml

# 验证安装
python -c "import requests; print('requests版本:', requests.__version__)"
```

### 数据库初始化失败

#### 问题：权限错误

**症状**：
```bash
sqlite3.OperationalError: unable to open database file
```

**解决方案**：
```bash
# 检查目录权限
ls -la data/
# 应该显示: drwxr-xr-x ... data/

# 修复权限
chmod 755 data/
chmod 664 data/scraping.db

# 或者重新创建目录
rm -rf data/
mkdir data/
python main.py db init

# 检查SELinux状态（CentOS/RHEL）
getenforce  # 如果是Enforcing，需要配置策略
```

#### 问题：磁盘空间不足

**症状**：
```bash
sqlite3.OperationalError: disk I/O error
```

**解决方案**：
```bash
# 检查磁盘空间
df -h
du -sh data/

# 清理临时文件
find . -name "*.tmp" -delete
find . -name "*.log" -type f -mtime +7 -delete

# 清理系统缓存
sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches

# 压缩数据库
python main.py db compress
```

## 运行执行问题

### 服务启动失败

#### 问题：端口被占用

**症状**：
```bash
OSError: [Errno 98] Address already in use
```

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :8000  # 检查8000端口
netstat -tlnp | grep 8000

# 终止占用进程
kill -9 <PID>

# 或者使用不同端口启动
python main.py daemon --port 8001

# 杀死所有相关进程
pkill -f "python main.py"
```

#### 问题：配置文件错误

**症状**：
```bash
yaml.scanner.ScannerError: mapping values are not allowed here
```

**解决方案**：
```bash
# 验证YAML语法
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# 常见错误修复
# 1. 缩进错误
# 错误: 
# key: value
#  another_key: value
# 正确:
# key: value
#   another_key: value

# 2. 冒号后需要空格
# 错误: key:value
# 正确: key: value

# 3. 引号问题
# 错误: key: "value with: colon"
# 正确: key: "value with: colon"

# 重置为默认配置
cp config/config.yaml config/config.yaml.backup
cp config/config.yaml.example config/config.yaml
```

### 抓取任务失败

#### 问题：网络连接超时

**症状**：
```bash
requests.exceptions.ConnectTimeout: HTTPSConnectionPool
```

**解决方案**：
```bash
# 测试网络连接
ping amazon.com
ping tiktok.com
nslookup amazon.com

# 增加超时时间
python main.py config set scraping.amazon.timeout 60
python main.py config set scraping.tiktok.timeout 60

# 测试代理连接（如果使用）
curl -x http://proxy:port http://httpbin.org/ip

# 禁用代理测试
python main.py config set scraping.amazon.proxy.enabled false
python main.py config set scraping.tiktok.proxy.enabled false
```

#### 问题：HTTP 403/429错误

**症状**：
```bash
HTTP 403 Forbidden
# 或
HTTP 429 Too Many Requests
```

**解决方案**：
```bash
# 1. 降低请求频率
python main.py config set scraping.amazon.request_delay 3.0
python main.py config set scraping.amazon.max_concurrent 1

# 2. 更新User-Agent
python main.py config set scraping.amazon.user_agent "Mozilla/5.0 (compatible; CustomBot/1.0)"

# 3. 增加重试次数
python main.py config set retry.max_retries 5

# 4. 使用代理轮换
python main.py config set scraping.amazon.proxy.enabled true
python main.py config set scraping.amazon.proxy.rotation true

# 5. 检查robots.txt
curl https://amazon.com/robots.txt
```

#### 问题：数据解析错误

**症状**：
```bash
ValueError: 'NoneType' object has no attribute 'text'
```

**解决方案**：
```bash
# 检查页面结构是否变化
python main.py scrape test --platform amazon --url "https://amazon.com"

# 更新选择器
# 1. 手动检查页面元素
# 2. 更新选择器配置
python main.py config update-selectors --platform amazon

# 增加错误容忍
python main.py config set advanced.data_validation.strict_mode false

# 检查数据格式
python main.py data validate --platform amazon --fix-errors
```

## 数据质量问题

### 数据为空或缺失

#### 问题：产品信息不完整

**症状**：
```bash
警告: 产品ID 12345 缺少价格信息
警告: 产品ID 67890 缺少图片链接
```

**解决方案**：
```bash
# 1. 检查关键词设置
python main.py config show scraping.amazon.keywords
# 确保关键词能匹配到产品

# 2. 调整选择器
python main.py config set advanced.data_validation.strict_mode false

# 3. 增加数据源
python main.py config set scraping.amazon.categories "T-Shirt,Hoodie,Sweatshirt"

# 4. 验证数据源
python main.py scrape test --platform amazon --category "T-Shirt" --limit 10
```

#### 问题：重复数据过多

**症状**：
```
数据库中存在 125 个重复产品记录
```

**解决方案**：
```bash
# 1. 检查去重配置
python main.py config show advanced.deduplication

# 2. 手动清理重复数据
python main.py db cleanup --duplicates

# 3. 调整去重策略
python main.py config set advanced.deduplication.strategy "product_id"
python main.py config set advanced.deduplication.confidence_threshold 0.9

# 4. 检查数据源是否有变化
python main.py data analyze-duplicates --platform amazon
```

### 数据格式问题

#### 问题：价格格式不一致

**症状**：
```sql
-- 数据库中的价格格式
$29.99
29.99
$30
30.00 USD
```

**解决方案**：
```bash
# 1. 更新数据清洗规则
python main.py config set advanced.data_cleaning.price.normalize true

# 2. 手动修复现有数据
python main.py data fix-prices --platform all --format "decimal(10,2)"

# 3. 验证修复结果
python main.py data validate-prices --platform amazon
```

#### 问题：编码问题

**症状**：
```bash
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**解决方案**：
```bash
# 1. 检查文件编码
file -i data/scraping.db

# 2. 设置正确的编码
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8

# 3. 修复编码问题
python main.py data fix-encoding --platform all --encoding utf-8

# 4. 重新导入数据（如果需要）
python main.py data reimport --encoding utf-8 --format json
```

## 性能问题

### 执行速度慢

#### 问题：抓取速度慢

**症状**：
```
单个产品抓取时间: 15.2秒 (目标: <3秒)
```

**解决方案**：
```bash
# 1. 优化并发设置
python main.py config set scraping.amazon.max_concurrent 5
python main.py config set scraping.amazon.request_delay 0.5

# 2. 优化网络配置
python main.py config set scraping.amazon.timeout 10
python main.py config set scraping.amazon.connection_pool_size 10

# 3. 启用缓存
python main.py config set performance.cache.enabled true
python main.py config set performance.cache.backend memory

# 4. 性能基准测试
python main.py benchmark --duration 5m --target-throughput 1000
```

#### 问题：数据库查询慢

**症状**：
```sql
-- 查询执行时间过长
SELECT * FROM products WHERE platform='amazon' AND price BETWEEN 50 AND 100;
-- 执行时间: 45.2秒
```

**解决方案**：
```bash
# 1. 分析查询性能
python main.py db explain "SELECT * FROM products WHERE platform='amazon'"

# 2. 重建索引
python main.py db reindex

# 3. 优化查询
python main.py db optimize-queries

# 4. 数据库统计信息更新
python main.py db analyze

# 5. 添加缺失索引
python main.py db add-indexes --suggested
```

### 内存使用过高

#### 问题：内存泄漏

**症状**：
```
系统内存使用: 87% (持续增长)
Python进程内存: 1.2GB (在增长)
```

**解决方案**：
```bash
# 1. 检查内存使用
python main.py system memory-profile --duration 10m

# 2. 启用垃圾回收
python main.py config set performance.memory.gc_threshold 700

# 3. 减少批量处理大小
python main.py config set advanced.batch_size 50

# 4. 启用流式处理
python main.py config set advanced.streaming_mode true

# 5. 重启服务释放内存
sudo systemctl restart tiktok-amazon-scraper
```

### 磁盘空间不足

**症状**：
```bash
df -h 显示磁盘使用率 95%
```

**解决方案**：
```bash
# 1. 清理日志文件
find logs/ -name "*.log" -mtime +7 -delete

# 2. 压缩旧日志
gzip logs/*.log.*

# 3. 清理临时文件
find . -name "*.tmp" -delete
find . -name "*.cache" -delete

# 4. 清理过期数据
python main.py db cleanup --older-than 30d

# 5. 压缩数据库
python main.py db compress

# 6. 设置自动清理
python main.py config set monitoring.auto_cleanup true
python main.py config set monitoring.cleanup_interval "24h"
```

## 数据库问题

### 数据库锁定

#### 问题：数据库被锁定

**症状**：
```bash
sqlite3.OperationalError: database is locked
```

**解决方案**：
```bash
# 1. 检查活跃连接
lsof data/scraping.db

# 2. 杀死占用进程
kill -9 <PID>

# 3. 重启服务
sudo systemctl restart tiktok-amazon-scraper

# 4. 检查是否有僵尸进程
ps aux | grep python

# 5. 强制解锁（最后手段）
python main.py db unlock --force

# 6. 修复数据库（如果需要）
python main.py db integrity-check --fix
```

### 数据损坏

#### 问题：数据库损坏

**症状**：
```bash
sqlite3.DatabaseError: database disk image is malformed
```

**解决方案**：
```bash
# 1. 备份当前数据库
cp data/scraping.db data/scraping.db.corrupted

# 2. 检查数据库完整性
sqlite3 data/scraping.db "PRAGMA integrity_check;"

# 3. 尝试修复
sqlite3 data/scraping.db ".dump" > backup.sql
rm data/scraping.db
sqlite3 data/scraping.db < backup.sql

# 4. 使用恢复工具
python main.py db recover --from-corrupted data/scraping.db.corrupted

# 5. 验证修复结果
python main.py db verify --fix-errors
```

### 备份恢复失败

#### 问题：备份文件损坏

**症状**：
```bash
Backup file is corrupted or incomplete
```

**解决方案**：
```bash
# 1. 验证备份文件
python main.py backup verify <backup-id>

# 2. 检查备份完整性
ls -la /backup/scraping_*.db
file /backup/scraping_*.db

# 3. 尝试不同备份
python main.py backup restore --backup-id latest --verify-only

# 4. 部分恢复
python main.py backup restore-partial --backup-id <id> --tables products

# 5. 从多个备份合并
python main.py backup merge --source backup1.db,backup2.db --output merged.db
```

## 网络连接问题

### DNS解析失败

#### 问题：无法解析域名

**症状**：
```bash
socket.gaierror: [Errno -2] Name or service not known
```

**解决方案**：
```bash
# 1. 测试DNS解析
nslookup amazon.com
dig tiktok.com

# 2. 检查网络连接
ping 8.8.8.8  # 测试基础连接
ping google.com  # 测试DNS解析

# 3. 更换DNS服务器
# 编辑 /etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4

# 4. 测试代理设置
curl -x http://proxy:port http://httpbin.org/ip

# 5. 临时禁用代理
export no_proxy="localhost,127.0.0.1,*.local"
```

### 防火墙阻止

#### 问题：连接被阻止

**症状**：
```bash
urllib3.exceptions.NewConnectionError: Failed to establish a new connection
```

**解决方案**：
```bash
# 1. 检查防火墙状态
sudo ufw status
sudo iptables -L

# 2. 临时关闭防火墙测试
sudo ufw disable

# 3. 添加允许规则
sudo ufw allow out 443/tcp
sudo ufw allow out 80/tcp

# 4. 测试特定端口
telnet amazon.com 443
telnet tiktok.com 443

# 5. 检查代理设置
echo $http_proxy
echo $https_proxy
```

### SSL证书问题

#### 问题：SSL验证失败

**症状**：
```bash
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**解决方案**：
```bash
# 1. 更新证书
sudo apt update && sudo apt install ca-certificates

# 2. 临时禁用SSL验证（不推荐）
python main.py config set scraping.ssl_verify false

# 3. 使用自定义证书
python main.py config set scraping.ssl_ca_bundle "/path/to/cert.pem"

# 4. 更新Python证书
pip install --upgrade certifi
python -m certifi

# 5. 测试SSL连接
openssl s_client -connect amazon.com:443
```

## 配置文件问题

### 语法错误

#### 问题：YAML格式错误

**症状**：
```bash
yaml.parser.ParserError: mapping values are not allowed here
```

**解决方案**：
```bash
# 1. 使用在线YAML验证器
# 或使用命令行验证
python -c "
import yaml
try:
    with open('config/config.yaml') as f:
        yaml.safe_load(f)
    print('YAML格式正确')
except yaml.YAMLError as e:
    print(f'YAML错误: {e}')
"

# 2. 常见错误修复
# 缩进必须使用空格，不使用Tab
# 冒号后必须有一个空格
# 字符串不需要引号（除非包含特殊字符）
# 列表项前必须使用'- '

# 3. 从示例配置重新开始
cp config/config.yaml.example config/config.yaml
```

### 配置不生效

#### 问题：修改配置后无效果

**症状**：
```bash
# 修改了配置但抓取行为没有改变
```

**解决方案**：
```bash
# 1. 验证配置是否正确应用
python main.py config show

# 2. 重启服务使配置生效
sudo systemctl restart tiktok-amazon-scraper

# 3. 检查配置文件路径
python main.py config locate

# 4. 重新加载配置
python main.py config reload

# 5. 验证环境变量覆盖
echo $SCRAPER_CONFIG_PATH
```

### 权限问题

#### 问题：配置文件无法访问

**症状**：
```bash
PermissionError: [Errno 13] Permission denied
```

**解决方案**：
```bash
# 1. 检查文件权限
ls -la config/

# 2. 修复权限
chmod 644 config/config.yaml
chmod 755 config/
chown $USER:$USER config/config.yaml

# 3. 检查SELinux上下文（CentOS）
ls -Z config/config.yaml
restorecon -v config/config.yaml

# 4. 检查是否在正确的目录
pwd
ls -la config/config.yaml
```

## 前端仪表板问题

### 启动失败

#### 问题：前端服务无法启动

**症状**：
```bash
Error: Cannot find module '@vitejs/plugin-react'
```

**解决方案**：
```bash
# 1. 重新安装依赖
cd fashion-dashboard
rm -rf node_modules package-lock.json
npm install

# 2. 清理npm缓存
npm cache clean --force
npm install

# 3. 使用yarn安装
yarn install

# 4. 检查Node.js版本
node --version  # 需要 16+
nvm use 16

# 5. 重新构建
npm run build
npm run preview
```

#### 问题：端口冲突

**症状**：
```bash
Error: Port 5173 is already in use
```

**解决方案**：
```bash
# 1. 查找占用进程
lsof -i :5173
netstat -tlnp | grep 5173

# 2. 杀死占用进程
kill -9 <PID>

# 3. 使用不同端口
npm run dev -- --port 3000

# 4. 启用自动端口选择
npm run dev -- --port 0
```

### 页面无法访问

#### 问题：浏览器无法打开

**症状**：
```
在浏览器中输入 http://localhost:5173 无法访问
```

**解决方案**：
```bash
# 1. 检查服务是否启动
curl http://localhost:5173

# 2. 检查网络接口
netstat -tlnp | grep 5173
# 应该显示: 0.0.0.0:5173 或 127.0.0.1:5173

# 3. 检查防火墙设置
sudo ufw status
sudo ufw allow 5173/tcp

# 4. 检查绑定地址
npm run dev -- --host 0.0.0.0

# 5. 使用IP地址访问
# 而不是localhost，使用：
# http://192.168.1.100:5173
```

### 数据不显示

#### 问题：仪表板显示空白

**症状**：
页面加载正常但没有数据显示

**解决方案**：
```bash
# 1. 检查API服务状态
curl http://localhost:8000/api/products

# 2. 检查浏览器控制台错误
# 打开浏览器开发者工具查看Console标签

# 3. 检查网络请求
# 查看Network标签中的API请求状态

# 4. 验证数据格式
python main.py export --format json --limit 5

# 5. 重新构建前端
cd fashion-dashboard
npm run build
npm run preview
```

## 错误日志分析

### 常见错误模式

#### 网络错误模式

```bash
# 连接超时错误
ERROR [2025-11-14 10:15:23] Connection timeout after 30s
- 解决：增加timeout或检查网络

# SSL证书错误  
ERROR [2025-11-14 10:15:45] SSL certificate verification failed
- 解决：更新证书或禁用验证

# 代理错误
ERROR [2025-11-14 10:16:12] Proxy connection failed: 407 Proxy Authentication Required
- 解决：检查代理凭据
```

#### 数据库错误模式

```bash
# 锁定错误
ERROR [2025-11-14 10:20:15] database is locked
- 解决：检查活跃连接，重启服务

# 完整性错误
ERROR [2025-11-14 10:20:30] foreign key constraint failed
- 解决：检查数据关联性

# 空间不足
ERROR [2025-11-14 10:21:45] disk I/O error
- 解决：清理磁盘空间
```

#### 解析错误模式

```bash
# 选择器错误
ERROR [2025-11-14 10:25:10] CSS selector '.product-title' not found
- 解决：更新选择器或检查页面结构

# 数据格式错误
ERROR [2025-11-14 10:25:25] Invalid price format: '$--invalid--'
- 解决：更新数据清洗规则

# 编码错误
ERROR [2025-11-14 10:25:40] UnicodeDecodeError: 'utf-8' codec can't decode
- 解决：设置正确的编码
```

### 日志分析工具

#### 自动化错误分析

```bash
# 分析错误趋势
python main.py log analyze-errors --period 7d --format chart

# 生成错误报告
python main.py log error-report --output errors.html --since 30d

# 实时错误监控
python main.py log monitor --level ERROR --notify-email admin@example.com
```

#### 日志聚合

```bash
# 合并多个日志文件
cat logs/*.log > combined.log

# 按级别筛选
grep "ERROR\|CRITICAL" combined.log > errors.log

# 按时间排序
sort -t ']' -k 2 combined.log > sorted.log

# 提取关键信息
grep -o "ERROR \[.*\] .*" combined.log | cut -d']' -f2
```

## 性能优化建议

### 系统级优化

#### 硬件优化

```bash
# CPU优化
# 1. 增加并发处理
python main.py config set scraping.amazon.max_concurrent 8
python main.py config set scraping.tiktok.max_concurrent 6

# 2. 使用多进程
python main.py config set performance.processes 4

# 内存优化
# 1. 调整批量大小
python main.py config set advanced.batch_size 100

# 2. 启用内存映射
python main.py config set database.memory_map true

# 存储优化
# 1. 使用SSD存储
# 2. 启用写入缓存
# 3. 定期清理碎片
```

#### 系统参数调优

```bash
# Linux内核参数优化
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
sysctl -p

# 文件描述符限制
echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf

# 数据库优化
python main.py config set database.optimization_level "maximum"
python main.py config set database.journal_mode WAL
python main.py config set database.synchronous NORMAL
```

### 应用级优化

#### 缓存策略

```yaml
# config/config.yaml
performance:
  cache:
    enabled: true
    backend: "redis"
    ttl: 3600
    max_size: "1GB"
    
  # 分层缓存
  layered_cache:
    memory_cache:
      enabled: true
      max_size: "100MB"
      ttl: 300
    
    disk_cache:
      enabled: true
      max_size: "500MB" 
      ttl: 3600
    
    database_cache:
      enabled: true
      ttl: 7200
```

#### 连接池优化

```yaml
# 数据库连接池
database:
  connection_pool:
    enabled: true
    pool_size: 20
    max_overflow: 30
    pool_timeout: 30
    pool_recycle: 3600

# HTTP连接池
scraping:
  connection_pool:
    max_connections: 100
    max_retries: 3
    retry_backoff: 0.1
    pool_timeout: 30
```

### 监控和基准测试

#### 性能监控

```bash
# 实时性能监控
python main.py monitor performance --interval 10s

# 生成性能报告
python main.py benchmark --duration 1h --output performance_report.html

# 容量测试
python main.py load-test --concurrent 50 --duration 10m

# 压力测试
python main.py stress-test --max-load 1000 --timeout 60
```

---

## 总结

本故障排除指南涵盖了TikTok & Amazon服装数据系统最常见的问题和解决方案：

- **快速诊断**：使用健康检查工具快速定位问题
- **分类解决**：按问题类型提供针对性解决方案
- **预防措施**：通过监控和优化避免问题发生
- **应急处理**：提供紧急情况下的快速处理方案

记住以下关键原则：

1. **先诊断后解决**：使用系统工具定位根本原因
2. **备份重要数据**：操作前备份关键配置和数据
3. **逐步优化**：避免一次性大幅修改设置
4. **监控变化**：记录修改内容和系统响应

如果问题仍然存在，请参考[常见问题FAQ](faq.md)或联系技术支持团队。