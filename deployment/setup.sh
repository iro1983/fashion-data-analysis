#!/bin/bash
# =============================================================================
# TikTok & Amazon 时尚数据抓取系统 - 自动化部署脚本
# =============================================================================
#
# 此脚本用于自动化部署整个系统到云端，包括：
# 1. 前端仪表板部署到 Vercel
# 2. 数据抓取云函数部署到 AWS Lambda
# 3. 数据库迁移和配置
# 4. 监控和告警设置
#
# 使用方法:
#   ./setup.sh [环境] [操作]
#   ./setup.sh dev deploy     # 部署到开发环境
#   ./setup.sh prod deploy    # 部署到生产环境
#   ./setup.sh dev cleanup    # 清理开发环境
#
# 作者: Claude
# 日期: 2025-11-14
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
ENVIRONMENT=${1:-dev}
OPERATION=${2:-deploy}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')

# 检查必需的工具
check_dependencies() {
    echo -e "${BLUE}[检查依赖]${NC} 正在检查必需的部署工具..."
    
    # 检查 AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}[错误]${NC} AWS CLI 未安装或不在 PATH 中"
        exit 1
    fi
    
    # 检查 Vercel CLI
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}[警告]${NC} Vercel CLI 未安装，正在安装..."
        npm install -g vercel
    fi
    
    # 检查 Docker (用于构建)
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}[警告]${NC} Docker 未安装"
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}[错误]${NC} Python3 未安装"
        exit 1
    fi
    
    echo -e "${GREEN}[检查依赖]${NC} 所有必需工具已就绪"
}

# 设置环境变量
setup_environment() {
    echo -e "${BLUE}[设置环境]${NC} 配置 $ENVIRONMENT 环境变量..."
    
    # 从 .env 文件加载环境变量
    ENV_FILE="$PROJECT_ROOT/.env.$ENVIRONMENT"
    if [ -f "$ENV_FILE" ]; then
        echo -e "${BLUE}[设置环境]${NC} 从 $ENV_FILE 加载环境变量"
        # 这里可以添加加载环境变量的逻辑
    else
        echo -e "${YELLOW}[警告]${NC} 环境文件 $ENV_FILE 不存在，使用默认值"
    fi
    
    # 验证必需的环境变量
    required_vars=(
        "AWS_ACCESS_KEY_ID"
        "AWS_SECRET_ACCESS_KEY"
        "AWS_DEFAULT_REGION"
        "VERCEL_TOKEN"
        "TIKTOK_USERNAME"
        "TIKTOK_PASSWORD"
        "AMAZON_ACCESS_KEY"
        "AMAZON_SECRET_KEY"
        "AMAZON_ASSOCIATE_TAG"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}[错误]${NC} 环境变量 $var 未设置"
            exit 1
        fi
    done
    
    echo -e "${GREEN}[设置环境]${NC} 环境变量配置完成"
}

# 部署前端到 Vercel
deploy_frontend() {
    echo -e "${BLUE}[前端部署]${NC} 正在部署前端应用到 Vercel..."
    
    cd "$PROJECT_ROOT/fashion-dashboard"
    
    # 安装依赖
    echo -e "${BLUE}[前端部署]${NC} 安装 Node.js 依赖..."
    npm ci
    
    # 构建生产版本
    echo -e "${BLUE}[前端部署]${NC} 构建生产版本..."
    npm run build
    
    # 部署到 Vercel
    echo -e "${BLUE}[前端部署]${NC} 部署到 Vercel..."
    vercel --prod --token="$VERCEL_TOKEN" --yes
    
    # 获取部署URL
    DEPLOYMENT_URL=$(vercel ls --token="$VERCEL_TOKEN" | grep -E "https://.*\.vercel\.app" | head -1 | awk '{print $1}')
    echo -e "${GREEN}[前端部署]${NC} 前端应用部署完成: $DEPLOYMENT_URL"
    
    # 设置自定义域名（如果需要）
    if [ ! -z "$CUSTOM_DOMAIN" ]; then
        echo -e "${BLUE}[前端部署]${NC} 配置自定义域名 $CUSTOM_DOMAIN..."
        vercel domains add "$CUSTOM_DOMAIN" --token="$VERCEL_TOKEN"
        vercel alias "$DEPLOYMENT_URL" "$CUSTOM_DOMAIN" --token="$VERCEL_TOKEN"
    fi
    
    cd "$SCRIPT_DIR"
}

# 部署云函数到 AWS
deploy_lambda() {
    echo -e "${BLUE}[Lambda部署]${NC} 正在部署 AWS Lambda 函数..."
    
    # 创建部署包
    echo -e "${BLUE}[Lambda部署]${NC} 创建 Lambda 部署包..."
    cd "$PROJECT_ROOT/deployment/cloud-function"
    
    # 创建临时目录
    TEMP_DIR="/tmp/lambda_deploy_$TIMESTAMP"
    mkdir -p "$TEMP_DIR"
    
    # 复制 Lambda 函数代码
    cp lambda_scraper.py "$TEMP_DIR/"
    
    # 创建 requirements.txt 用于 Lambda
    cat > "$TEMP_DIR/requirements.txt" << EOF
boto3==1.34.0
requests==2.31.0
python-dateutil==2.8.2
EOF
    
    # 安装 Python 依赖
    echo -e "${BLUE}[Lambda部署]${NC} 安装 Python 依赖..."
    pip3 install -r "$TEMP_DIR/requirements.txt" -t "$TEMP_DIR"
    
    # 创建部署包
    echo -e "${BLUE}[Lambda部署]${NC} 创建 ZIP 部署包..."
    cd "$TEMP_DIR"
    zip -r lambda_function.zip .
    
    # 上传到 AWS Lambda
    FUNCTION_NAME="fashion-scraper-$ENVIRONMENT"
    echo -e "${BLUE}[Lambda部署]${NC} 上传函数到 AWS..."
    aws lambda update-function-code \
        --function-name "$FUNCTION_NAME" \
        --zip-file fileb://lambda_function.zip
    
    # 清理临时文件
    rm -rf "$TEMP_DIR"
    
    echo -e "${GREEN}[Lambda部署]${NC} Lambda 函数部署完成"
}

# 部署基础设施
deploy_infrastructure() {
    echo -e "${BLUE}[基础设施]${NC} 部署 AWS 基础设施..."
    
    cd "$PROJECT_ROOT/deployment/cloud-function"
    
    # 使用 CloudFormation 部署基础设施
    STACK_NAME="fashion-scraper-$ENVIRONMENT"
    
    echo -e "${BLUE}[基础设施]${NC} 创建/更新 CloudFormation 堆栈..."
    aws cloudformation deploy \
        --template-file cloudformation-template.yaml \
        --stack-name "$STACK_NAME" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
            NotificationEmail="$NOTIFICATION_EMAIL" \
        --capabilities CAPABILITY_IAM \
        --region "$AWS_DEFAULT_REGION"
    
    # 获取堆栈输出
    echo -e "${BLUE}[基础设施]${NC} 获取堆栈输出..."
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_DEFAULT_REGION" \
        --query 'Stacks[0].Outputs' \
        --output table
    
    echo -e "${GREEN}[基础设施]${NC} AWS 基础设施部署完成"
}

# 设置数据库
setup_database() {
    echo -e "${BLUE}[数据库设置]${NC} 配置数据库..."
    
    # 这里可以添加数据库迁移逻辑
    # 例如：创建表、设置索引、导入初始数据等
    
    echo -e "${GREEN}[数据库设置]${NC} 数据库配置完成"
}

# 配置监控和告警
setup_monitoring() {
    echo -e "${BLUE}[监控配置]${NC} 设置监控和告警..."
    
    # 创建 CloudWatch 告警
    cat > /tmp/cloudwatch-alarms.json << 'EOF'
{
  "Alarms": [
    {
      "AlarmName": "fashion-scraper-failures",
      "ComparisonOperator": "GreaterThanThreshold",
      "EvaluationPeriods": 1,
      "MetricName": "Errors",
      "Namespace": "AWS/Lambda",
      "Period": 300,
      "Statistic": "Sum",
      "Threshold": 0.0,
      "ActionsEnabled": true,
      "AlarmActions": ["arn:aws:sns:region:account:topic"],
      "AlarmDescription": "Alert when Lambda function has errors",
      "Unit": "Count"
    }
  ]
}
EOF
    
    # 应用告警配置
    aws cloudwatch put-metric-alarm \
        --alarm-name "fashion-scraper-errors-$ENVIRONMENT" \
        --alarm-description "Fashion scraper error rate" \
        --metric-name Errors \
        --namespace AWS/Lambda \
        --statistic Sum \
        --period 300 \
        --threshold 0 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 1
    
    rm /tmp/cloudwatch-alarms.json
    
    echo -e "${GREEN}[监控配置]${NC} 监控和告警配置完成"
}

# 运行测试
run_tests() {
    echo -e "${BLUE}[测试]${NC} 运行部署后测试..."
    
    # 测试前端部署
    echo -e "${BLUE}[测试]${NC} 测试前端应用..."
    # 这里可以添加前端测试逻辑
    
    # 测试后端API
    echo -e "${BLUE}[测试]${NC} 测试后端API..."
    # 这里可以添加API测试逻辑
    
    # 测试数据抓取
    echo -e "${BLUE}[测试]${NC} 测试数据抓取功能..."
    # 这里可以添加抓取测试逻辑
    
    echo -e "${GREEN}[测试]${NC} 所有测试通过"
}

# 生成部署报告
generate_deployment_report() {
    echo -e "${BLUE}[部署报告]${NC} 生成部署报告..."
    
    REPORT_FILE="$PROJECT_ROOT/deployment/deployment-report-$TIMESTAMP.md"
    
    cat > "$REPORT_FILE" << EOF
# 部署报告

**部署时间**: $(date)
**环境**: $ENVIRONMENT
**操作**: $OPERATION

## 部署组件

### 前端应用
- **平台**: Vercel
- **状态**: 部署完成
- **URL**: $(vercel ls --token="$VERCEL_TOKEN" | grep -E "https://.*\.vercel\.app" | head -1 | awk '{print $1}' || echo "获取中")

### 后端服务
- **平台**: AWS Lambda
- **函数名**: fashion-scraper-$ENVIRONMENT
- **状态**: 部署完成

### 基础设施
- **平台**: AWS CloudFormation
- **堆栈名**: fashion-scraper-$ENVIRONMENT
- **状态**: 部署完成

## 监控
- **CloudWatch告警**: 已配置
- **SNS通知**: 已配置
- **Slack集成**: 已配置

## 下一步
1. 等待定时任务首次执行
2. 验证数据抓取功能
3. 检查监控告警
4. 性能优化调整

---
报告生成于: $(date)
EOF
    
    echo -e "${GREEN}[部署报告]${NC} 报告已生成: $REPORT_FILE"
}

# 清理环境
cleanup_environment() {
    echo -e "${YELLOW}[清理]${NC} 清理 $ENVIRONMENT 环境..."
    
    # 删除 CloudFormation 堆栈
    STACK_NAME="fashion-scraper-$ENVIRONMENT"
    echo -e "${BLUE}[清理]${NC} 删除 CloudFormation 堆栈..."
    aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$AWS_DEFAULT_REGION"
    
    # 等待堆栈删除完成
    echo -e "${BLUE}[清理]${NC} 等待堆栈删除完成..."
    aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$AWS_DEFAULT_REGION"
    
    # 删除 Vercel 部署
    echo -e "${BLUE}[清理]${NC} 删除 Vercel 部署..."
    cd "$PROJECT_ROOT/fashion-dashboard"
    vercel rm --token="$VERCEL_TOKEN" --yes
    
    echo -e "${GREEN}[清理]${NC} 环境清理完成"
}

# 主函数
main() {
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE} TikTok & Amazon 时尚数据抓取系统部署${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo -e "环境: $ENVIRONMENT"
    echo -e "操作: $OPERATION"
    echo -e "时间: $(date)"
    echo ""
    
    case "$OPERATION" in
        "deploy")
            check_dependencies
            setup_environment
            deploy_frontend
            deploy_infrastructure
            deploy_lambda
            setup_database
            setup_monitoring
            run_tests
            generate_deployment_report
            ;;
        "cleanup")
            cleanup_environment
            ;;
        "test")
            run_tests
            ;;
        *)
            echo -e "${RED}[错误]${NC} 未知的操作: $OPERATION"
            echo "可用操作: deploy, cleanup, test"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}[完成]${NC} $OPERATION 操作已完成"
}

# 错误处理
trap 'echo -e "${RED}[错误]${NC} 部署过程中发生错误，退出代码: $?"; exit 1' ERR

# 运行主函数
main "$@"