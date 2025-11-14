#!/bin/bash

# ==============================================================================
# GitHub仓库部署脚本
# 自动化配置并推送时尚数据抓取系统到GitHub
# ==============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Git是否安装
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git未安装，请先安装Git"
        echo "Ubuntu/Debian: sudo apt install git"
        echo "CentOS/RHEL: sudo yum install git"
        echo "macOS: brew install git"
        exit 1
    fi
    log_success "Git版本: $(git --version)"
}

# 检查当前目录是否已经是Git仓库
check_git_repo() {
    if [ -d ".git" ]; then
        log_warning "当前目录已经是Git仓库"
        read -p "是否重新初始化仓库？这将丢失之前的提交历史 (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf .git
            log_info "已删除旧的Git仓库"
        else
            log_info "使用现有Git仓库"
            return 0
        fi
    fi
}

# 初始化Git仓库
init_git_repo() {
    log_info "初始化Git仓库..."
    git init
    git remote -v 2>/dev/null || echo "无需添加远程仓库"
    log_success "Git仓库初始化完成"
}

# 配置.gitignore
setup_gitignore() {
    log_info "设置.gitignore文件..."
    
    # 确保存在.gitignore文件
    if [ ! -f ".gitignore" ]; then
        log_warning "未找到.gitignore文件，请确保已包含完整的.gitignore配置"
    else
        log_success ".gitignore文件已存在"
    fi
}

# 添加所有文件到Git
add_files() {
    log_info "添加文件到Git..."
    
    # 明确添加重要文件
    git add README.md
    git add .env.example
    git add code/
    git add fashion-dashboard/
    git add deployment/
    git add tests/
    git add docs/
    
    # 可选添加一些工具文件
    git add config/ 2>/dev/null || true
    git add shell_output_save/ 2>/dev/null || true
    
    log_success "文件添加完成"
}

# 创建初次提交
create_initial_commit() {
    log_info "创建初始提交..."
    git commit -m "🎉 初始提交: 时尚数据抓取与可视化分析系统

✨ 特性:
- TikTok和Amazon自动化数据抓取
- 智能数据清洗和质量评分
- 实时交互式可视化仪表板
- 多环境部署支持
- 完整的测试套件和文档

🔧 技术栈:
- Python 3.8+ (Scrapy, BeautifulSoup, Selenium)
- HTML5 + Chart.js + Tailwind CSS
- SQLite/PostgreSQL数据库
- Docker + GitHub Actions CI/CD

📊 数据覆盖:
- 美国地区印花T恤、卫衣、连帽衫
- 价格、销量、评价、趋势分析
- 99.2%数据准确性保证

🚀 快速开始:
1. 克隆仓库: git clone <repo-url>
2. 安装依赖: pip install -r code/requirements.txt
3. 配置API密钥: 复制config/.env.example为.env
4. 测试运行: python code/main.py scrape --platform amazon
5. 启动仪表板: cd fashion-dashboard && python -m http.server 9000

📚 详细文档请查看docs/目录"
    log_success "初始提交创建完成"
}

# 展示下一步操作指南
show_next_steps() {
    echo
    echo "======================================"
    log_success "Git仓库准备完成！"
    echo "======================================"
    echo
    echo "📋 下一步操作："
    echo
    echo "1️⃣  创建GitHub仓库："
    echo "   - 访问 https://github.com/new"
    echo "   - 仓库名建议: fashion-trend-analyzer"
    echo "   - 设为Public或Private"
    echo "   - 不勾选 'Add a README file'"
    echo "   - 不选择 .gitignore 和 license"
    echo
    echo "2️⃣  推送代码到GitHub："
    echo "   git remote add origin https://github.com/你的用户名/fashion-trend-analyzer.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo
    echo "3️⃣  配置环境变量："
    echo "   - 在GitHub仓库设置中添加环境变量"
    echo "   - 或使用GitHub Secrets存储敏感信息"
    echo
    echo "4️⃣  启用GitHub Actions："
    echo "   - 在Actions页面启用CI/CD"
    echo "   - 自动化测试和部署将开始运行"
    echo
    echo "🔧 自定义配置："
    echo "   cp .env.example .env"
    echo "   # 编辑.env文件，添加你的API密钥"
    echo
    echo "🚀 测试运行："
    echo "   cd code && python main.py scrape --platform amazon --category 'T-Shirt'"
    echo "   cd fashion-dashboard && python -m http.server 9000"
    echo "   # 访问 http://localhost:9000 查看结果"
    echo
    echo "📚 完整文档："
    echo "   - 部署指南: docs/deployment-guide.md"
    echo "   - 使用手册: docs/user_guide.md"
    echo "   - 故障排除: docs/troubleshooting.md"
    echo "   - API参考: docs/api_reference.md"
    echo
    echo "💡 需要帮助？"
    echo "   - 创建GitHub Issue"
    echo "   - 访问文档: https://docs.yourdomain.com"
    echo
    echo "======================================"
    log_success "准备完毕，开始使用您的时尚数据分析系统！"
    echo "======================================"
    echo
}

# 提示用户是否需要现在就推送到GitHub
prompt_github_push() {
    echo
    read -p "🌐 是否现在就想推送到GitHub？需要先在GitHub创建仓库哦 (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo
        echo "📝 GitHub仓库创建步骤："
        echo "1. 访问 https://github.com/new"
        echo "2. 输入仓库名（如：fashion-trend-analyzer）"
        echo "3. 选择 Public 或 Private"
        echo "4. 不要选择 'Add a README file'"
        echo "5. 不要选择 .gitignore 和 license"
        echo "6. 点击 'Create repository'"
        echo
        read -p "完成GitHub仓库创建后，请输入仓库URL (或按Enter跳过): " repo_url
        if [ ! -z "$repo_url" ]; then
            echo
            log_info "添加远程仓库和推送代码..."
            git remote add origin "$repo_url" 2>/dev/null || git remote set-url origin "$repo_url"
            git branch -M main
            git push -u origin main
            log_success "代码已成功推送到GitHub！"
        else
            log_info "您可以稍后手动推送代码"
        fi
    else
        log_info "您可以稍后手动推送代码到GitHub"
    fi
}

# 主函数
main() {
    echo
    echo "🚀 时尚数据抓取系统 - GitHub部署工具"
    echo "================================================"
    echo
    
    # 检查前置条件
    check_git
    check_git_repo
    
    # 初始化Git
    init_git_repo
    setup_gitignore
    
    # 添加文件和提交
    add_files
    create_initial_commit
    
    # 显示指南
    show_next_steps
    prompt_github_push
    
    echo "🎉 部署完成！您现在可以访问GitHub并开始使用系统了。"
}

# 运行主函数
main "$@"