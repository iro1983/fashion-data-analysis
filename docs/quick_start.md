# 快速入门指南

本指南将在5分钟内帮您完成系统的安装、配置和首次使用。

## 🚀 系统概述

TikTok & Amazon 服装数据系统是一个自动化数据抓取和分析工具，帮助您：
- 自动收集TikTok和Amazon的服装产品数据
- 通过Web界面查看实时数据和分析结果
- 导出数据进行深度分析
- 监控竞品价格和市场趋势

## 📋 环境准备

### 系统要求检查

在开始之前，请确认您的系统满足以下要求：

```bash
# 检查Python版本
python --version
# 需要 Python 3.8 或更高版本

# 检查Node.js版本（仅前端仪表板需要）
node --version
# 需要 Node.js 16 或更高版本
```

### 必备软件安装

**Python依赖安装**：
```bash
# 进入项目目录
cd /path/to/tiktok-amazon-system

# 安装Python依赖
pip install -r requirements.txt
```

**前端仪表板依赖**（可选）：
```bash
# 进入前端目录
cd fashion-dashboard

# 安装Node.js依赖
npm install
# 或者使用pnpm
pnpm install
```

## 🔧 快速配置

### 1. 基础配置

系统提供了开箱即用的默认配置。在大多数情况下，您可以直接使用默认配置开始抓取数据。

**检查默认配置**：
```bash
python main.py config show
```

**修改抓取关键词**（可选）：
编辑 `config/config.yaml` 文件：

```yaml
# 修改Amazon抓取关键词
scraping:
  amazon:
    keywords:
      - "T-shirt"        # 添加您关注的关键词
      - "hoodie"
      - "sweatshirt"
  
  # 修改TikTok抓取关键词
  tiktok:
    keywords:
      - "服装"           # 中文关键词
      - "时尚"
      - "潮流"
```

### 2. 数据库初始化

```bash
# 初始化数据库（首次运行会自动创建）
python main.py status
```

## ⚡ 快速开始

### 第一次数据抓取

选择以下任一方式开始抓取数据：

**方式一：抓取Amazon数据**
```bash
python main.py scrape --platform amazon
```

**方式二：抓取TikTok数据**
```bash
python main.py scrape --platform tiktok
```

**方式三：同时抓取两个平台数据**
```bash
python main.py scrape --platform all
```

### 抓取过程监控

系统运行时会显示实时状态：

```
🔄 开始执行数据抓取任务...
✅ Amazon抓取开始...
✅ TikTok抓取开始...

📊 任务统计:
  - 总任务数: 2
  - 成功任务: 1  
  - 失败任务: 0
  - 总产品数: 45
  - 平均执行时间: 3.2秒
```

### 查看抓取结果

```bash
# 查看系统状态
python main.py status

# 查看最新的数据报告
ls reports/
```

## 📊 数据可视化

### 启动Web仪表板

```bash
# 进入前端目录
cd fashion-dashboard

# 启动开发服务器
npm run dev
# 或者
pnpm dev
```

### 访问仪表板

打开浏览器访问：`http://localhost:5173`

您将看到：
- **概览页面**：显示总产品数、抓取成功率等统计信息
- **产品列表**：浏览和搜索所有抓取的产品
- **图表分析**：价格分布、热门类别等可视化分析
- **数据导出**：将数据导出为Excel或CSV格式

### 仪表板功能预览

```
┌─────────────────────────────────────────────┐
│  TikTok & Amazon 数据仪表板                   │
├─────────────────────────────────────────────┤
│  📈 总产品数: 156    📊 今日新增: 23          │
│  🎯 成功率: 98%     ⏱️ 最后更新: 5分钟前     │
├─────────────────────────────────────────────┤
│  [概览] [产品列表] [数据分析] [设置]           │
├─────────────────────────────────────────────┤
│  📋 最近产品                              📊  │
│  ├─ Nike Air Max 2023        $129.99      │
│  ├─ Adidas Classic Hoodie    $79.99       │
│  └─ Supreme Box Logo Tee     $89.99       │
└─────────────────────────────────────────────┘
```

## 🔍 常用操作

### 查看特定平台数据

```bash
# 只查看Amazon产品
python main.py query --platform amazon --category "T-Shirt"

# 查看价格范围在$50-100的产品
python main.py query --price-min 50 --price-max 100
```

### 数据导出

```bash
# 导出为JSON格式
python export_data.py --format json --output results.json

# 导出为Excel格式  
python export_data.py --format excel --output results.xlsx

# 导出特定类别的数据
python export_data.py --category "Hoodie" --format csv
```

### 系统监控

```bash
# 查看实时日志
tail -f logs/coordinator.log

# 检查系统健康状态
python main.py health-check
```

## ⚙️ 个性化配置

### 修改抓取频率

编辑 `config/config.yaml`：

```yaml
# 增加并发数以提高抓取速度
scraping:
  amazon:
    max_concurrent: 5      # 默认3
    request_delay: 0.5     # 默认1.0秒
  
  tiktok:
    max_concurrent: 3      # 默认2
    request_delay: 1.0     # 默认2.0秒
```

### 添加新的产品类别

```yaml
scraping:
  amazon:
    categories:
      - "T-Shirt"          # T恤
      - "Hoodie"           # 卫衣
      - "Sweatshirt"       # 运动衫
      - "Jeans"            # 牛仔裤（新增）
      - "Jacket"           # 夹克（新增）
```

### 启用数据备份

```yaml
database:
  backup_enabled: true     # 启用自动备份
  backup_interval: "24h"   # 24小时备份一次
```

## 🚨 常见问题快速解决

### 问题1：抓取失败

**症状**：显示"连接失败"或"超时"错误

**解决方案**：
```bash
# 检查网络连接
ping amazon.com
ping tiktok.com

# 增加请求延迟
python main.py config set scraping.amazon.request_delay 3.0
```

### 问题2：数据库错误

**症状**：`database is locked`错误

**解决方案**：
```bash
# 停止所有运行中的进程
pkill -f "python main.py"

# 检查数据库文件权限
ls -la data/scraping.db

# 重新初始化数据库
rm data/scraping.db
python main.py status
```

### 问题3：前端仪表板无法访问

**症状**：浏览器无法打开 `http://localhost:5173`

**解决方案**：
```bash
# 检查端口是否被占用
lsof -i :5173

# 使用不同端口启动
npm run dev -- --port 3000
```

## 🎯 第一次成功体验

按照以下步骤，您将在5分钟内完成首次数据抓取：

1. ✅ **安装依赖**：`pip install -r requirements.txt`
2. ✅ **检查配置**：`python main.py config show`
3. ✅ **执行抓取**：`python main.py scrape --platform amazon`
4. ✅ **启动仪表板**：`npm run dev` (在fashion-dashboard目录)
5. ✅ **访问界面**：打开 `http://localhost:5173`

成功后您将看到：
- 终端显示抓取进度和统计结果
- Web仪表板显示抓取的产品数据
- 可以浏览、搜索和导出数据

## 📚 下一步学习

完成快速入门后，建议您：

1. 📖 阅读[完整用户指南](user_guide.md)了解所有功能
2. 🔧 学习[管理维护指南](administration_guide.md)进行系统优化
3. 🛠️ 查看[API参考文档](api_reference.md)进行程序化访问
4. ❓ 参考[故障排除指南](troubleshooting.md)解决问题

## 💡 小贴士

- **定期备份**：重要数据请定期备份数据库文件
- **合理配置**：避免过高并发以防被平台限制
- **监控日志**：定期检查日志文件了解系统状态
- **渐进使用**：从少量数据开始，逐步增加抓取规模

---

**开始您的数据探索之旅！** 🚀

如果在快速入门过程中遇到任何问题，请查看[故障排除指南](troubleshooting.md)或参考[常见问题FAQ](faq.md)。