# ❓ 常见问题解答 (FAQ)

> 快速解决您在使用过程中遇到的问题

## 🚀 安装和部署问题

### Q1: Git 安装失败或版本过旧
**问题**: 运行 `git --version` 显示错误或版本低于2.0

**解决方案**:
```bash
# Windows用户
# 访问 https://git-scm.com/download/win 下载最新版本

# Mac用户
brew install git
# 或从官网下载: https://git-scm.com/download/mac

# Linux用户
sudo apt update
sudo apt install git
```

### Q2: Python版本不符合要求
**问题**: Python版本低于3.8或命令找不到

**解决方案**:
```bash
# 检查当前版本
python --version

# 如果版本过低，升级Python
# Windows: 从 https://python.org 下载新版本
# Mac: brew install python3
# Linux: sudo apt install python3.9

# 验证安装
python3 --version
```

### Q3: pip 安装依赖失败
**问题**: 安装requirements.txt时出现网络错误或权限问题

**解决方案**:
```bash
# 方法1: 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 方法2: 用户安装模式
pip install --user -r requirements.txt

# 方法3: 升级pip后重试
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 💾 数据库和配置问题

### Q4: 数据库初始化失败
**问题**: 创建数据库时出现错误

**解决方案**:
```bash
# 检查目录权限
mkdir -p data
chmod 755 data

# 重新初始化数据库
cd code
python -c "
from database import Database
import os
os.makedirs('../data', exist_ok=True)
db = Database('../data/fashion_data.db')
db.create_tables()
print('数据库初始化成功')
"
```

### Q5: 环境变量配置错误
**问题**: .env文件配置不正确或未生效

**解决方案**:
```bash
# 检查.env文件是否存在
ls -la .env

# 如果不存在，重新创建
cp .env.example .env

# 编辑配置文件
# Windows: notepad .env
# Mac/Linux: nano .env

# 验证配置加载
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('TIKHUB_API_KEY:', os.getenv('TIKHUB_API_KEY', 'Not found'))
print('AMAZON_ACCESS_KEY:', os.getenv('AMAZON_ACCESS_KEY', 'Not found'))
"
```

### Q6: 数据抓取返回空结果
**问题**: 抓取命令执行但没有获取到数据

**解决方案**:
```bash
# 1. 检查API密钥配置
python -c "
import os
print('API配置状态:')
print('TIKHUB_API_KEY:', '已配置' if os.getenv('TIKHUB_API_KEY') != 'test_key' else '测试模式')
print('AMAZON_ACCESS_KEY:', '已配置' if os.getenv('AMAZON_ACCESS_KEY') != 'test_key' else '测试模式')
"

# 2. 查看详细错误日志
python main.py scrape --platform amazon --category "T-Shirt" --verbose

# 3. 测试数据库连接
python -c "
from database import Database
db = Database()
print('数据库连接:', '成功' if db.test_connection() else '失败')
"

# 4. 检查网络连接
curl -I https://www.amazon.com
```

## 🌐 Web仪表板问题

### Q7: Web服务器无法启动
**问题**: 访问localhost:9000显示错误或无响应

**解决方案**:
```bash
# 1. 检查端口占用
netstat -tlnp | grep 9000
# Windows: netstat -an | findstr :9000

# 2. 使用其他端口
python -m http.server 9001

# 3. 检查防火墙设置
# Windows: 允许Python通过防火墙
# Mac/Linux: sudo ufw allow 9000

# 4. 查看详细启动日志
python -m http.server 9000 --bind 0.0.0.0 --verbose
```

### Q8: 仪表板页面显示空白或错误
**问题**: Web页面无法正常显示数据

**解决方案**:
```bash
# 1. 检查浏览器控制台错误
# F12 → Console → 查看红色错误信息

# 2. 验证数据文件存在
ls -la fashion-dashboard/data/
# 如果没有data目录，复制示例数据

# 3. 检查文件权限
chmod -R 755 fashion-dashboard/

# 4. 清除浏览器缓存
# Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac)
```

## 🔧 API和集成问题

### Q9: TikTok API调用失败
**问题**: TikHub API返回错误或无数据

**解决方案**:
```bash
# 1. 验证API密钥状态
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.tikhub.io/v1/status

# 2. 检查API使用量限制
# 登录TikHub控制台查看剩余配额

# 3. 测试API连通性
python -c "
import requests
import os
api_key = os.getenv('TIKHUB_API_KEY')
if api_key and api_key != 'test_key':
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get('https://api.tikhub.io/v1/channels', headers=headers)
    print('API状态码:', response.status_code)
else:
    print('请配置有效的TikHub API密钥')
"

# 4. 更新API密钥
# 编辑.env文件中的TIKHUB_API_KEY
```

### Q10: Amazon SP-API权限问题
**问题**: Amazon API返回权限不足或认证失败

**解决方案**:
```bash
# 1. 检查Amazon开发者控制台
# 访问 https://developer.amazon.com/developer-console/
# 确认应用程序状态为 "Live"

# 2. 验证Marketplace ID
# 确保 AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER (美国)

# 3. 测试API连接
python -c "
import requests
import os
from datetime import datetime
import hmac
import hashlib

access_key = os.getenv('AMAZON_ACCESS_KEY')
secret_key = os.getenv('AMAZON_SECRET_KEY')

if access_key and access_key != 'test_key':
    print('Amazon API密钥已配置')
    print('请检查Amazon开发者控制台中的权限设置')
else:
    print('请配置有效的Amazon SP-API密钥')
"

# 4. 重新获取API凭证
# 在Amazon Developer Console重新生成密钥对
```

## ☁️ 部署和自动化问题

### Q11: GitHub Actions 执行失败
**问题**: CI/CD流程出现红色失败状态

**解决方案**:
```bash
# 1. 查看详细错误日志
# 在GitHub Actions页面点击失败的workflow → 查看job详情

# 2. 检查GitHub Secrets配置
# Settings → Secrets and variables → Actions
# 确认所有必需的secrets都已添加

# 3. 手动触发测试
# Actions页面 → Run workflow → 选择分支手动运行

# 4. 检查代码语法
# 本地运行: python -m py_compile code/*.py
```

### Q12: Vercel 部署失败
**问题**: 前端部署到Vercel后无法访问

**解决方案**:
```bash
# 1. 检查Vercel部署日志
# 在Vercel控制台查看build失败原因

# 2. 验证项目配置
# 确保选择了正确的framework: "Other"
# 确保root directory: "fashion-dashboard"

# 3. 本地测试构建
cd fashion-dashboard
python -m http.server 3000
# 在本地测试确认文件正常

# 4. 重新部署
# Vercel控制台 → Project → Redeploy
```

### Q13: 定时任务不执行
**问题**: GitHub Actions的定时任务没有按预期运行

**解决方案**:
```bash
# 1. 检查时区设置
# GitHub Actions使用UTC时间
# 凌晨2点UTC = 上午10点中国时间

# 2. 验证workflow文件
# .github/workflows/ci-cd.yml中的schedule设置
# cron: '0 2 * * *' # 每天2点UTC

# 3. 查看Actions历史
# 确认是否有定时触发的workflows

# 4. 手动测试
# Actions → Run workflow → 验证任务能否正常执行
```

## 📊 数据分析问题

### Q14: 数据质量差或重复
**问题**: 抓取到的数据有大量重复或质量不高

**解决方案**:
```bash
# 1. 启用数据清洗
python main.py clean --aggressive

# 2. 调整质量阈值
# 编辑config/quality_settings.py
QUALITY_THRESHOLD = 0.8
DEDUPLICATION_THRESHOLD = 0.9

# 3. 手动清理重复数据
python main.py dedupe --method fuzzy

# 4. 重新抓取高质量数据
python main.py scrape --platform amazon --category "T-Shirt" --quality-filter
```

### Q15: 价格数据不准确
**问题**: 显示的价格与实际Amazon页面不符

**解决方案**:
```bash
# 1. 检查价格解析逻辑
python main.py debug --platform amazon --url "具体的Amazon产品URL"

# 2. 更新选择器
# 编辑amazon_scraper.py中的CSS选择器

# 3. 考虑多币种问题
# 确认货币符号和单位解析正确

# 4. 验证实时价格
python main.py verify --platform amazon --product-id "产品ID"
```

## 🔒 安全和权限问题

### Q16: API密钥泄露
**问题**: 不小心将API密钥提交到GitHub

**解决方案**:
```bash
# 1. 立即轮换密钥
# 登录API提供商控制台生成新密钥

# 2. 删除GitHub历史记录
git filter-branch --tree-filter 'rm -f config/.env' HEAD
git push origin --force --all

# 3. 使用GitHub Secrets
# 永远不要在代码中硬编码API密钥

# 4. 监控使用情况
# 检查API使用日志确认是否有异常访问
```

### Q17: 数据库权限错误
**问题**: 无法写入数据库文件

**解决方案**:
```bash
# 1. 检查文件权限
ls -la data/fashion_data.db
chmod 664 data/fashion_data.db

# 2. 修复目录权限
chmod -R 755 data/
chown -R $USER:$USER data/

# 3. 使用绝对路径
# 确保DATABASE_PATH使用完整路径

# 4. 检查磁盘空间
df -h
# 确保有足够的磁盘空间
```

## 🆘 紧急问题处理

### Q18: 系统完全无法启动
**问题**: 任何命令都无法执行或启动

**解决方案**:
```bash
# 1. 检查系统环境
python --version
pip --version
git --version

# 2. 重新安装依赖
pip install --force-reinstall -r requirements.txt

# 3. 清除缓存
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 4. 使用诊断工具
python main.py diagnose --full
```

### Q19: 数据丢失
**问题**: 数据库文件损坏或数据意外删除

**解决方案**:
```bash
# 1. 检查备份
ls -la data/backups/
# 恢复备份: python main.py restore --file backup_20231114.db

# 2. 检查Git历史
git log --oneline
# 回退到之前版本: git reset --hard 提交ID

# 3. 检查文件恢复
# Windows: 检查回收站
# Mac: 检查Time Machine备份
# Linux: 检查文件历史版本

# 4. 从GitHub重新开始
git clone https://github.com/你的用户名/fashion-trend-analyzer.git
```

---

## 📞 获取更多帮助

### 文档资源
- **完整教程**: `docs/complete-step-by-step-tutorial.md`
- **快速入门**: `docs/quick-start-guide.md`
- **用户手册**: `docs/user_guide.md`
- **API文档**: `docs/api_reference.md`

### 社区支持
- **GitHub Issues**: 创建详细的问题报告
- **GitHub Discussions**: 参与社区讨论
- **Stack Overflow**: 搜索技术问题解决方案

### 诊断工具
```bash
# 运行完整系统诊断
python main.py diagnose --full

# 检查系统状态
python main.py status

# 生成问题报告
python main.py report --output system_report.txt
```

---

**💡 提示**: 遇到问题时，先查看错误日志，然后尝试重新运行相关命令。如果问题持续存在，请创建GitHub Issue并包含完整的错误信息。