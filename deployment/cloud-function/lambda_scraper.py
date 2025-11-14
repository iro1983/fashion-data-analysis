#!/usr/bin/env python3
"""
AWS Lambda 数据抓取云函数
===========================

这是一个部署在AWS Lambda上的数据抓取函数，
用于定时执行Amazon和TikTok数据抓取任务。

触发方式：
- CloudWatch Events (定时触发)
- API Gateway (手动触发)
- S3 Events (文件触发)

作者：Claude
日期：2025-11-14
"""

import json
import logging
import os
import sys
import boto3
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import traceback

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS服务客户端
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    AWS Lambda主处理函数
    
    Args:
        event: Lambda事件对象
        context: Lambda上下文对象
    
    Returns:
        dict: 响应结果
    """
    try:
        logger.info("开始执行数据抓取任务...")
        logger.info(f"触发事件: {json.dumps(event, default=str)}")
        
        # 解析事件参数
        platforms = event.get('platforms', ['amazon', 'tiktok'])
        force_run = event.get('force_run', False)
        
        # 执行数据抓取
        result = run_scraping_tasks(platforms, force_run)
        
        # 保存结果到S3
        save_result_to_s3(result)
        
        # 发送成功通知
        send_success_notification(result)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': '数据抓取任务执行成功',
                'data': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"执行数据抓取任务失败: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 发送失败通知
        send_failure_notification(str(e))
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }

def run_scraping_tasks(platforms, force_run=False):
    """
    执行数据抓取任务
    
    Args:
        platforms (list): 要抓取的平台列表
        force_run (bool): 是否强制运行
    
    Returns:
        dict: 抓取结果
    """
    start_time = datetime.now(timezone.utc)
    results = {
        'start_time': start_time.isoformat(),
        'platforms': platforms,
        'success': True,
        'errors': [],
        'data': {
            'amazon': {},
            'tiktok': {}
        }
    }
    
    # 执行Amazon数据抓取
    if 'amazon' in platforms:
        try:
            logger.info("开始抓取Amazon数据...")
            amazon_result = scrape_amazon_data()
            results['data']['amazon'] = amazon_result
            logger.info(f"Amazon数据抓取完成: {amazon_result}")
        except Exception as e:
            error_msg = f"Amazon数据抓取失败: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
    
    # 执行TikTok数据抓取
    if 'tiktok' in platforms:
        try:
            logger.info("开始抓取TikTok数据...")
            tiktok_result = scrape_tiktok_data()
            results['data']['tiktok'] = tiktok_result
            logger.info(f"TikTok数据抓取完成: {tiktok_result}")
        except Exception as e:
            error_msg = f"TikTok数据抓取失败: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
    
    # 如果有错误，标记为失败
    if results['errors']:
        results['success'] = False
    
    end_time = datetime.now(timezone.utc)
    results['end_time'] = end_time.isoformat()
    results['duration_seconds'] = (end_time - start_time).total_seconds()
    
    return results

def scrape_amazon_data():
    """抓取Amazon数据"""
    # 这里应该调用实际的Amazon API
    # 由于在Lambda环境中，我们需要将抓取逻辑集成到这里
    
    try:
        # 模拟数据抓取过程
        import time
        time.sleep(2)  # 模拟API调用延迟
        
        # 从环境变量获取Amazon API凭据
        access_key = os.environ.get('AMAZON_ACCESS_KEY')
        secret_key = os.environ.get('AMAZON_SECRET_KEY')
        associate_tag = os.environ.get('AMAZON_ASSOCIATE_TAG')
        
        if not all([access_key, secret_key, associate_tag]):
            raise ValueError("Amazon API凭据未配置")
        
        # 这里应该调用实际的Amazon API
        # 现在返回模拟数据
        return {
            'status': 'success',
            'products_count': 50,
            'categories': ['服装', '配饰', '鞋类'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise Exception(f"Amazon数据抓取异常: {str(e)}")

def scrape_tiktok_data():
    """抓取TikTok数据"""
    # 这里应该调用实际的TikTok API
    try:
        # 模拟数据抓取过程
        import time
        time.sleep(2)  # 模拟API调用延迟
        
        # 从环境变量获取TikTok凭据
        username = os.environ.get('TIKTOK_USERNAME')
        password = os.environ.get('TIKTOK_PASSWORD')
        
        if not all([username, password]):
            raise ValueError("TikTok凭据未配置")
        
        # 这里应该调用实际的TikTok API
        # 现在返回模拟数据
        return {
            'status': 'success',
            'posts_count': 30,
            'hashtags': ['fashion', 'clothing', 'style'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise Exception(f"TikTok数据抓取异常: {str(e)}")

def save_result_to_s3(result):
    """
    将抓取结果保存到S3
    
    Args:
        result (dict): 抓取结果
    """
    try:
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        if not bucket_name:
            logger.warning("S3 bucket name未配置，跳过结果保存")
            return
        
        # 生成文件路径
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f"scraping_results/result_{timestamp}.json"
        
        # 保存到S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(result, indent=2, default=str),
            ContentType='application/json',
            ServerSideEncryption='AES256'
        )
        
        logger.info(f"结果已保存到S3: s3://{bucket_name}/{key}")
        
    except Exception as e:
        logger.error(f"保存结果到S3失败: {str(e)}")
        # 不抛出异常，避免影响主流程

def send_success_notification(result):
    """发送成功通知"""
    try:
        # 这里可以集成Slack、邮件等通知方式
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        if webhook_url:
            # 发送Slack通知
            import requests
            
            message = {
                "text": "✅ 数据抓取任务执行成功!",
                "attachments": [
                    {
                        "color": "good",
                        "fields": [
                            {
                                "title": "开始时间",
                                "value": result['start_time'],
                                "short": True
                            },
                            {
                                "title": "执行时长",
                                "value": f"{result.get('duration_seconds', 0):.2f}秒",
                                "short": True
                            },
                            {
                                "title": "抓取平台",
                                "value": ", ".join(result['platforms']),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            requests.post(webhook_url, json=message)
            logger.info("成功通知已发送")
            
    except Exception as e:
        logger.error(f"发送通知失败: {str(e)}")
        # 不抛出异常，避免影响主流程

def send_failure_notification(error_message):
    """发送失败通知"""
    try:
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        if webhook_url:
            import requests
            
            message = {
                "text": "❌ 数据抓取任务执行失败!",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {
                                "title": "错误信息",
                                "value": error_message,
                                "short": False
                            },
                            {
                                "title": "发生时间",
                                "value": datetime.now(timezone.utc).isoformat(),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            requests.post(webhook_url, json=message)
            logger.info("失败通知已发送")
            
    except Exception as e:
        logger.error(f"发送通知失败: {str(e)}")

# 测试函数（本地调试用）
def test_handler():
    """测试Lambda处理函数"""
    test_event = {
        'platforms': ['amazon', 'tiktok'],
        'force_run': True
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    test_handler()