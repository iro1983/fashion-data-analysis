#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试运行器
==============

执行所有集成测试并生成综合报告

作者：Claude
日期：2025-11-14
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"耗时: {duration:.2f}秒")
        print(f"返回码: {result.returncode}")
        
        if result.stdout:
            print("\n标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("\n错误输出:")
            print(result.stderr)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': duration
        }
        
    except Exception as e:
        print(f"命令执行异常: {e}")
        return {
            'success': False,
            'error': str(e),
            'duration': 0
        }


def setup_test_environment():
    """设置测试环境"""
    print("设置测试环境...")
    
    # 创建测试必要的目录
    test_dirs = [
        "tests/logs",
        "tests/reports", 
        "tests/temp",
        "code/data",
        "code/backup"
    ]
    
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")
    
    # 检查必需的Python模块
    print("\n检查Python模块依赖...")
    required_modules = [
        'sqlite3', 'json', 'logging', 'unittest', 
        'tempfile', 'shutil', 'threading', 'requests'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: 可用")
        except ImportError:
            print(f"❌ {module}: 不可用")
    
    print("\n环境设置完成")


def check_project_structure():
    """检查项目结构"""
    print("检查项目结构...")
    
    required_files = [
        "code/main.py",
        "code/database.py", 
        "code/data_cleaner.py",
        "code/amazon_scraper.py",
        "code/tiktok_scraper.py",
        "fashion-dashboard/src/App.tsx",
        "fashion-dashboard/package.json"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ 发现缺失文件: {len(missing_files)}个")
        return False
    else:
        print("\n✅ 项目结构检查通过")
        return True


def run_all_tests():
    """运行所有测试"""
    print("\n开始运行集成测试...")
    
    test_results = []
    
    # 1. 运行主集成测试
    result = run_command(
        "python tests/integration_tests.py",
        "主集成测试"
    )
    test_results.append(("主集成测试", result))
    
    # 2. 运行数据流测试
    result = run_command(
        "python tests/test_data_flow.py",
        "数据流测试"
    )
    test_results.append(("数据流测试", result))
    
    # 3. 运行错误处理测试
    result = run_command(
        "python tests/test_error_handling.py",
        "错误处理测试"
    )
    test_results.append(("错误处理测试", result))
    
    # 4. 运行用户界面测试
    result = run_command(
        "python tests/test_user_interface.py",
        "用户界面测试"
    )
    test_results.append(("用户界面测试", result))
    
    return test_results


def generate_test_summary(test_results):
    """生成测试摘要"""
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result['success'])
    failed_tests = total_tests - passed_tests
    
    total_duration = sum(result['duration'] for _, result in test_results)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'passed': passed_tests,
        'failed': failed_tests,
        'success_rate': f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
        'total_duration': f"{total_duration:.2f}秒",
        'test_details': []
    }
    
    for test_name, result in test_results:
        test_detail = {
            'name': test_name,
            'success': result['success'],
            'duration': f"{result['duration']:.2f}秒"
        }
        
        if not result['success']:
            test_detail['error'] = result.get('stderr', result.get('error', '未知错误'))
        
        summary['test_details'].append(test_detail)
    
    return summary


def save_test_report(summary):
    """保存测试报告"""
    report_path = "tests/reports/integration_test_summary.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试摘要已保存到: {report_path}")


def print_final_summary(summary):
    """打印最终摘要"""
    print("\n" + "="*60)
    print("🎯 集成测试最终结果")
    print("="*60)
    print(f"📊 测试总数: {summary['total_tests']}")
    print(f"✅ 通过: {summary['passed']}")
    print(f"❌ 失败: {summary['failed']}")
    print(f"📈 成功率: {summary['success_rate']}")
    print(f"⏱️ 总耗时: {summary['total_duration']}")
    
    print("\n📋 详细结果:")
    for detail in summary['test_details']:
        status = "✅" if detail['success'] else "❌"
        print(f"  {status} {detail['name']} ({detail['duration']})")
    
    print("\n" + "="*60)
    
    if summary['failed'] == 0:
        print("🎉 所有集成测试通过！系统可以投入使用。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查错误信息并修复问题。")
        return False


def main():
    """主函数"""
    print("🚀 启动集成测试套件")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 设置测试环境
    setup_test_environment()
    
    # 2. 检查项目结构
    if not check_project_structure():
        print("❌ 项目结构检查失败，请确保所有必要文件存在")
        sys.exit(1)
    
    # 3. 运行所有测试
    test_results = run_all_tests()
    
    # 4. 生成测试摘要
    summary = generate_test_summary(test_results)
    
    # 5. 保存测试报告
    save_test_report(summary)
    
    # 6. 打印最终摘要
    success = print_final_summary(summary)
    
    # 7. 退出
    if success:
        print("\n✅ 集成测试成功完成")
        sys.exit(0)
    else:
        print("\n❌ 集成测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()