# 🚀 快速入门指南

> 5分钟快速上手时尚数据分析系统

## 📋 快速检查清单

开始前请确认：
- [ ] 有GitHub账户
- [ ] 已安装Git和Python 3.8+
- [ ] 网络连接正常

## ⚡ 5分钟快速启动

### 1️⃣ 创建GitHub仓库 (2分钟)
```bash
# 在GitHub.com创建新仓库
# 仓库名: fashion-trend-analyzer
# 不要勾选README、.gitignore、license
```

### 2️⃣ 下载和推送代码 (2分钟)
```bash
# 复制项目文件到本地目录
cd fashion-trend-analyzer

# 推送到GitHub
git init
git add .
git commit -m "初始提交"
git remote add origin https://github.com/你的用户名/fashion-trend-analyzer.git
git branch -M main
git push -u origin main
```

### 3️⃣ 本地测试 (1分钟)
```bash
cd code
pip install -r requirements.txt
python main.py scrape --platform amazon --category "T-Shirt"
cd ../fashion-dashboard
python -m http.server 9000
# 访问 http://localhost:9000
```

## 🔑 API密钥配置

编辑 `config/.env` 文件：

```bash
# TikHub API (TikTok数据)
TIKHUB_API_KEY=your_tikhub_api_key

# Amazon SP-API
AMAZON_ACCESS_KEY=your_amazon_key
AMAZON_SECRET_KEY=your_amazon_secret

# 测试模式
ENVIRONMENT=development
```

## 📊 常用命令

```bash
# 数据抓取
python main.py scrape --platform amazon --category "T-Shirt"
python main.py scrape --platform tiktok --category "Printed"
python main.py scrape --all

# 查看统计
python main.py stats

# 导出数据
python main.py export --format json --output data/products.json

# 启动服务
python main.py serve --host 0.0.0.0 --port 9000

# 清理数据
python main.py clean
```

## 🌐 访问地址

- **本地仪表板**: http://localhost:9000
- **GitHub仓库**: https://github.com/你的用户名/fashion-trend-analyzer
- **云端访问**: https://你的用户名.vercel.app (部署后)

## 🆘 遇到问题？

1. **查看详细教程**: `docs/complete-step-by-step-tutorial.md`
2. **检查系统日志**: `tail -f code/logs/scraper.log`
3. **运行诊断**: `python main.py diagnose`
4. **创建GitHub Issue**: 包含错误日志和环境信息

## 🎯 下一步

1. 获取真实API密钥替换测试配置
2. 在GitHub设置中添加Secrets
3. 配置Vercel部署前端
4. 启用定时数据抓取

---

**✅ 系统启动后，您就可以开始分析时尚趋势数据了！**