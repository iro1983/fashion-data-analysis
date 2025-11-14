#!/bin/bash
# Amazon与TikTok数据抓取协调器运行脚本
# =====================================

set -e

echo "Amazon与TikTok数据抓取协调器"
echo "=============================="

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python版本检查通过: $python_version"
else
    echo "❌ Python版本需要 >= $required_version，当前版本: $python_version"
    exit 1
fi

# 检查依赖
echo "检查依赖包..."
python3 -c "import yaml, asyncio, concurrent.futures, sqlite3, json, datetime, pathlib" 2>/dev/null || {
    echo "❌ 缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
}

# 创建必要目录
echo "创建必要目录..."
mkdir -p data logs reports config

# 赋予执行权限
chmod +x demo.py
chmod +x test_main.py

# 显示菜单
echo ""
echo "请选择操作:"
echo "1. 查看帮助"
echo "2. 运行演示"
echo "3. 执行测试"
echo "4. 抓取Amazon平台"
echo "5. 抓取TikTok平台"
echo "6. 抓取所有平台"
echo "7. 查看系统状态"
echo "8. 配置管理"
echo "9. 退出"
echo ""

read -p "请输入选项 (1-9): " choice

case $choice in
    1)
        echo "显示帮助信息:"
        python3 main.py --help
        ;;
    2)
        echo "运行演示:"
        python3 demo.py
        ;;
    3)
        echo "执行测试:"
        python3 test_main.py
        ;;
    4)
        echo "抓取Amazon平台:"
        read -p "请输入产品类别 (多个用空格分隔): " categories
        read -p "请输入关键词 (多个用空格分隔): " keywords
        read -p "请输入最大页数 (默认5): " max_pages
        max_pages=${max_pages:-5}
        
        python3 main.py scrape --platform amazon --category $categories --keyword $keywords --max-pages $max_pages
        ;;
    5)
        echo "抓取TikTok平台:"
        read -p "请输入产品类别 (多个用空格分隔): " categories
        read -p "请输入关键词 (多个用空格分隔): " keywords
        read -p "请输入最大页数 (默认5): " max_pages
        max_pages=${max_pages:-5}
        
        python3 main.py scrape --platform tiktok --category $categories --keyword $keywords --max-pages $max_pages
        ;;
    6)
        echo "抓取所有平台:"
        read -p "请输入产品类别 (多个用空格分隔): " categories
        read -p "请输入关键词 (多个用空格分隔): " keywords
        read -p "请输入最大页数 (默认5): " max_pages
        max_pages=${max_pages:-5}
        
        python3 main.py scrape --platform all --category $categories --keyword $keywords --max-pages $max_pages
        ;;
    7)
        echo "查看系统状态:"
        python3 main.py status
        ;;
    8)
        echo "配置管理:"
        echo "1. 显示配置"
        echo "2. 设置配置"
        read -p "请选择操作 (1-2): " config_choice
        case $config_choice in
            1)
                python3 main.py config show
                ;;
            2)
                read -p "请输入配置键 (如: scraping.amazon.max_concurrent): " config_key
                read -p "请输入配置值: " config_value
                python3 main.py config set "$config_key" "$config_value"
                ;;
        esac
        ;;
    9)
        echo "退出程序"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "操作完成！"
echo ""
echo "生成的文件:"
echo "  - 数据库: data/scraping.db"
echo "  - 日志: logs/coordinator.log"
echo "  - 报告: reports/"
echo ""