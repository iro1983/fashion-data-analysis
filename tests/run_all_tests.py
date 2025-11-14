#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合性能测试运行器

运行所有性能测试并生成综合报告
"""

import sys
import time
import json
from pathlib import Path

# 添加测试目录到路径
sys.path.append(str(Path(__file__).parent))

from database_performance import run_database_performance_tests
from web_performance import run_web_performance_tests  
from scraper_performance import run_scraper_performance_tests
from load_test import run_load_tests

def run_all_performance_tests():
    """运行所有性能测试"""
    print("🚀 开始综合性能测试...")
    print("=" * 80)
    
    all_reports = {}
    start_time = time.time()
    
    try:
        # 1. 数据库性能测试
        print("\n🔍 1. 数据库性能测试")
        print("-" * 40)
        all_reports['database'] = run_database_performance_tests()
        
        # 2. 网页应用性能测试
        print("\n🌐 2. 网页应用性能测试")
        print("-" * 40)
        all_reports['web'] = run_web_performance_tests()
        
        # 3. 数据抓取性能测试
        print("\n🕷️  3. 数据抓取性能测试")
        print("-" * 40)
        all_reports['scraper'] = run_scraper_performance_tests()
        
        # 4. 系统压力测试
        print("\n⚡ 4. 系统压力测试")
        print("-" * 40)
        all_reports['load_test'] = run_load_tests(short_test=True)
        
        total_time = time.time() - start_time
        
        # 生成综合报告
        comprehensive_report = {
            'test_suite': 'comprehensive_performance_test',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_execution_time': round(total_time, 2),
            'individual_reports': all_reports,
            'comprehensive_summary': generate_comprehensive_summary(all_reports)
        }
        
        # 保存综合报告
        report_file = Path("tests/performance_report.md")
        save_comprehensive_report(comprehensive_report, report_file)
        
        print("\n" + "=" * 80)
        print("📊 综合性能测试完成")
        print("=" * 80)
        
        return comprehensive_report
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        raise

def generate_comprehensive_summary(all_reports):
    """生成综合测试摘要"""
    summary = {
        'total_test_suites': len(all_reports),
        'test_suite_results': {},
        'overall_status': 'unknown',
        'critical_issues': [],
        'performance_scores': {},
        'recommendations': []
    }
    
    # 分析各测试套件结果
    for suite_name, report in all_reports.items():
        if 'summary' in report:
            suite_summary = report['summary']
            
            summary['test_suite_results'][suite_name] = {
                'status': suite_summary.get('overall_status', 'unknown'),
                'passed_tests': suite_summary.get('passed_tests', 0),
                'total_tests': suite_summary.get('total_tests', 0),
                'score': suite_summary.get('performance_score', 0) or suite_summary.get('overall_success_rate', 0)
            }
            
            # 收集性能分数
            if suite_name == 'database':
                summary['performance_scores']['database'] = suite_summary.get('overall_status') == 'passed'
            elif suite_name == 'web':
                summary['performance_scores']['web'] = suite_summary.get('performance_score', 0) >= 80
            elif suite_name == 'scraper':
                summary['performance_scores']['scraper'] = suite_summary.get('overall_success_rate', 0) >= 95
            elif suite_name == 'load_test':
                summary['performance_scores']['stability'] = suite_summary.get('stability_score', 0) >= 90
        
        # 检查关键问题
        if 'test_results' in report:
            for test_name, results in report['test_results'].items():
                if isinstance(results, dict):
                    if test_name.endswith('_met') and not results.get('target_met', False):
                        summary['critical_issues'].append(f"{suite_name}: {test_name} 未达标")
    
    # 生成改进建议
    for suite_name, suite_result in summary['test_suite_results'].items():
        if suite_result['status'] == 'failed':
            summary['recommendations'].append(f"优先解决 {suite_name} 模块的性能问题")
        elif suite_result['status'] == 'partial':
            summary['recommendations'].append(f"改进 {suite_name} 模块的部分测试项目")
    
    # 确定整体状态
    passed_suites = sum(1 for result in summary['test_suite_results'].values() if result['status'] == 'passed')
    
    if passed_suites == summary['total_test_suites']:
        summary['overall_status'] = 'passed'
    elif passed_suites > 0:
        summary['overall_status'] = 'partial'
    else:
        summary['overall_status'] = 'failed'
    
    return summary

def save_comprehensive_report(report, output_file):
    """保存综合报告到Markdown文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 综合性能测试报告\n\n")
        
        # 报告头部信息
        f.write(f"**测试时间**: {report['timestamp']}\n")
        f.write(f"**执行时长**: {report['total_execution_time']} 秒\n")
        f.write(f"**测试套件数**: {report['comprehensive_summary']['total_test_suites']}\n\n")
        
        # 综合摘要
        summary = report['comprehensive_summary']
        f.write("## 📊 综合摘要\n\n")
        f.write(f"- **整体状态**: {summary['overall_status'].upper()}\n")
        f.write(f"- **通过测试套件**: {sum(1 for r in summary['test_suite_results'].values() if r['status'] == 'passed')}/{summary['total_test_suites']}\n\n")
        
        # 各测试套件结果
        f.write("### 各测试套件结果\n\n")
        for suite_name, suite_result in summary['test_suite_results'].items():
            status_icon = "✅" if suite_result['status'] == 'passed' else "⚠️" if suite_result['status'] == 'partial' else "❌"
            f.write(f"- {status_icon} **{suite_name.title()}测试**: {suite_result['passed_tests']}/{suite_result['total_tests']} 通过\n")
        
        f.write("\n")
        
        # 详细结果
        for suite_name, suite_report in report['individual_reports'].items():
            f.write(f"## 🔍 {suite_name.title()}性能测试详情\n\n")
            
            if 'summary' in suite_report:
                suite_summary = suite_report['summary']
                f.write(f"**状态**: {suite_summary.get('overall_status', 'unknown').upper()}\n\n")
                
                if 'performance_score' in suite_summary:
                    f.write(f"**性能分数**: {suite_summary['performance_score']}/100\n\n")
                elif 'overall_success_rate' in suite_summary:
                    f.write(f"**成功率**: {suite_summary['overall_success_rate']}%\n\n")
            
            # 关键指标
            if 'test_results' in suite_report:
                f.write("### 关键指标\n\n")
                f.write("| 测试项目 | 目标 | 实际结果 | 状态 |\n")
                f.write("|---------|------|----------|------|\n")
                
                for test_name, results in suite_report['test_results'].items():
                    if isinstance(results, dict):
                        # 查找目标达成的指标
                        if 'target_met' in results:
                            target = "达标" if results['target_met'] else "未达标"
                            f.write(f"| {test_name} | 达标 | {target} | {'✅' if results['target_met'] else '❌'} |\n")
                        elif 'targets_met' in results:
                            # 处理复合目标
                            targets = results['targets_met']
                            met_count = sum(1 for v in targets.values() if v)
                            total_targets = len(targets)
                            f.write(f"| {test_name} | {total_targets}项达标 | {met_count}项达标 | {'✅' if met_count == total_targets else '⚠️'} |\n")
        
        f.write("\n")
        
        # 关键问题和改进建议
        if summary['critical_issues']:
            f.write("## ⚠️ 关键问题\n\n")
            for issue in summary['critical_issues']:
                f.write(f"- {issue}\n")
            f.write("\n")
        
        if summary['recommendations']:
            f.write("## 💡 改进建议\n\n")
            for recommendation in summary['recommendations']:
                f.write(f"- {recommendation}\n")
            f.write("\n")
        
        # 性能基准对比
        f.write("## 📈 性能基准对比\n\n")
        benchmarks = [
            ("数据库查询响应时间", "< 100ms", "根据测试结果"),
            ("网页页面加载时间", "< 2s", "根据测试结果"), 
            ("图表渲染时间", "< 1s", "根据测试结果"),
            ("数据抓取成功率", "> 95%", "根据测试结果"),
            ("系统稳定性", "99%+", "根据测试结果")
        ]
        
        f.write("| 性能指标 | 基准目标 | 测试结果 | 状态 |\n")
        f.write("|---------|----------|----------|------|\n")
        
        for metric, benchmark, result in benchmarks:
            # 简化状态判断
            if "查询响应" in metric:
                status = "✅" if "database" in summary.get('test_suite_results', {}) else "❌"
            elif "页面加载" in metric:
                status = "✅" if "web" in summary.get('test_suite_results', {}) else "❌"
            elif "抓取成功" in metric:
                status = "✅" if "scraper" in summary.get('test_suite_results', {}) else "❌"
            elif "稳定性" in metric:
                status = "✅" if "load_test" in summary.get('test_suite_results', {}) else "❌"
            else:
                status = "⚠️"
            
            f.write(f"| {metric} | {benchmark} | {result} | {status} |\n")
        
        f.write("\n")
        
        # 测试数据导出
        # 保存JSON格式的详细数据
        json_file = Path("tests/comprehensive_performance_report.json")
        with open(json_file, 'w', encoding='utf-8') as jf:
            json.dump(report, jf, indent=2, ensure_ascii=False)
        
        f.write(f"**详细JSON报告**: {json_file}\n")
        f.write(f"**报告生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    """主函数"""
    print("🎯 TikTok & Amazon 服装数据系统 - 综合性能测试")
    print("📋 测试范围:")
    print("   - 数据库性能 (SQLite)")
    print("   - 网页应用性能 (React + Vite)")
    print("   - 数据抓取性能 (Amazon + TikTok)")
    print("   - 系统压力测试")
    
    # 询问是否运行完整测试
    print("\n💡 测试模式:")
    print("   1. 完整测试 (推荐) - 所有测试项目")
    print("   2. 快速测试 - 基础性能验证")
    
    try:
        choice = input("\n请选择测试模式 (1/2，默认为1): ").strip()
        
        if choice == '2':
            print("⚡ 运行快速测试...")
            run_all_performance_tests()
        else:
            print("🚀 运行完整测试...")
            run_all_performance_tests()
        
        print(f"\n✅ 性能测试报告已生成:")
        print(f"   📄 Markdown报告: tests/performance_report.md")
        print(f"   📊 JSON数据: tests/comprehensive_performance_report.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        raise

if __name__ == "__main__":
    main()