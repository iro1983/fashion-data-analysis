// Vercel API 路由配置
// 用于处理数据查询、手动触发抓取等API请求

import { NextApiRequest, NextApiResponse } from 'next';
import { 
  triggerScraping, 
  getScrapingStatus, 
  getDashboardData,
  exportData 
} from '../../../lib/api';

// CORS 头配置
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Max-Age': '86400',
  'Access-Control-Allow-Credentials': 'false'
};

// 处理OPTIONS请求
function handleOptions(req: NextApiRequest, res: NextApiResponse) {
  res.writeHead(200, corsHeaders);
  res.end();
}

// API路由处理器
export default async function handler(
  req: NextApiRequest, 
  res: NextApiResponse
) {
  // 处理CORS预检请求
  if (req.method === 'OPTIONS') {
    return handleOptions(req, res);
  }

  try {
    // 设置CORS头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    // 路由处理
    const { method } = req;
    const path = req.query.path as string[];

    switch (path?.[0]) {
      // 触发数据抓取
      case 'trigger':
        if (req.method === 'POST') {
          const { platforms, force_run } = req.body;
          
          // 验证请求参数
          if (!platforms || !Array.isArray(platforms)) {
            return res.status(400).json({
              error: 'Invalid platforms parameter',
              message: 'Platforms must be an array'
            });
          }

          const result = await triggerScraping({
            platforms,
            force_run: force_run || false
          });

          return res.status(200).json({
            success: true,
            data: result
          });
        }
        break;

      // 获取抓取状态
      case 'status':
        if (req.method === 'GET') {
          const { job_id } = req.query;
          
          if (!job_id) {
            return res.status(400).json({
              error: 'Missing job_id parameter'
            });
          }

          const status = await getScrapingStatus(job_id as string);

          return res.status(200).json({
            success: true,
            data: status
          });
        }
        break;

      // 获取仪表板数据
      case 'dashboard':
        if (req.method === 'GET') {
          const { 
            start_date, 
            end_date, 
            platform, 
            category,
            limit = 100,
            offset = 0 
          } = req.query;

          const data = await getDashboardData({
            start_date: start_date as string,
            end_date: end_date as string,
            platform: platform as string,
            category: category as string,
            limit: parseInt(limit as string),
            offset: parseInt(offset as string)
          });

          return res.status(200).json({
            success: true,
            data
          });
        }
        break;

      // 导出数据
      case 'export':
        if (req.method === 'GET') {
          const { format = 'json', platform, category } = req.query;
          
          const exportData_result = await exportData({
            format: format as string,
            platform: platform as string,
            category: category as string
          });

          // 设置响应头
          if (format === 'csv') {
            res.setHeader('Content-Type', 'text/csv');
            res.setHeader('Content-Disposition', `attachment; filename="fashion-data-${Date.now()}.csv"`);
          } else {
            res.setHeader('Content-Type', 'application/json');
          }

          return res.status(200).send(exportData_result);
        }
        break;

      // 健康检查
      case 'health':
        if (req.method === 'GET') {
          return res.status(200).json({
            status: 'healthy',
            timestamp: new Date().toISOString(),
            services: {
              database: 'connected',
              api: 'operational',
              scraping: 'available'
            }
          });
        }
        break;

      // 默认路由
      default:
        return res.status(404).json({
          error: 'API endpoint not found',
          available_endpoints: [
            '/api/v1/trigger',
            '/api/v1/status',
            '/api/v1/dashboard',
            '/api/v1/export',
            '/api/v1/health'
          ]
        });
    }

    // 方法不支持
    return res.status(405).json({
      error: 'Method not allowed',
      allowed_methods: ['GET', 'POST']
    });

  } catch (error) {
    console.error('API Error:', error);
    
    return res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    });
  }
}

// 限制请求大小（10MB）
export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
  },
}