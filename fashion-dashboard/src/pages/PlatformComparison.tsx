import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Zap, Users, DollarSign, ShoppingBag } from 'lucide-react';
import { dataService, PlatformStats } from '../lib/dataService';

const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#F97316'];

const PlatformComparison: React.FC = () => {
  const [platformStats, setPlatformStats] = useState<PlatformStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlatformStats();
  }, []);

  const loadPlatformStats = async () => {
    try {
      setLoading(true);
      const data = await dataService.getPlatformStats();
      setPlatformStats(data);
    } catch (error) {
      console.error('Failed to load platform stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatData = () => {
    const tiktokData = platformStats.filter(stat => stat.platform === 'tiktok');
    const amazonData = platformStats.filter(stat => stat.platform === 'amazon');

    // TikTok数据
    const tiktokProducts = tiktokData.reduce((sum, stat) => sum + stat.count, 0);
    const tiktokAvgPrice = tiktokData.reduce((sum, stat) => sum + parseFloat(stat.avg_price), 0) / tiktokData.length || 0;
    const tiktokAvgRating = tiktokData.reduce((sum, stat) => sum + parseFloat(stat.avg_rating), 0) / tiktokData.length || 0;
    const tiktokSales = tiktokData.reduce((sum, stat) => sum + stat.total_sales, 0);

    // Amazon数据
    const amazonProducts = amazonData.reduce((sum, stat) => sum + stat.count, 0);
    const amazonAvgPrice = amazonData.reduce((sum, stat) => sum + parseFloat(stat.avg_price), 0) / amazonData.length || 0;
    const amazonAvgRating = amazonData.reduce((sum, stat) => sum + parseFloat(stat.avg_rating), 0) / amazonData.length || 0;
    const amazonSales = amazonData.reduce((sum, stat) => sum + stat.total_sales, 0);

    return {
      tiktok: {
        products: tiktokProducts,
        avgPrice: tiktokAvgPrice,
        avgRating: tiktokAvgRating,
        sales: tiktokSales
      },
      amazon: {
        products: amazonProducts,
        avgPrice: amazonAvgPrice,
        avgRating: amazonAvgRating,
        sales: amazonSales
      }
    };
  };

  const comparisonData = formatData();

  // 分类对比数据
  const categoryComparison = ['tshirt', 'hoodie', 'sweatshirt'].map(category => {
    const tiktokStat = platformStats.find(stat => stat.platform === 'tiktok' && stat.category === category);
    const amazonStat = platformStats.find(stat => stat.platform === 'amazon' && stat.category === category);
    
    return {
      category: category === 'tshirt' ? 'T恤' : category === 'hoodie' ? '卫衣' : '连帽衫',
      tiktok: tiktokStat ? tiktokStat.count : 0,
      amazon: amazonStat ? amazonStat.count : 0,
      tiktokPrice: tiktokStat ? parseFloat(tiktokStat.avg_price) : 0,
      amazonPrice: amazonStat ? parseFloat(amazonStat.avg_price) : 0
    };
  });

  // 平台分布数据
  const platformDistribution = [
    { name: 'TikTok', value: comparisonData.tiktok.products, color: '#EF4444' },
    { name: 'Amazon', value: comparisonData.amazon.products, color: '#FF9500' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">平台对比分析</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">TikTok vs Amazon 数据对比</p>
      </div>

      {/* 平台概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* TikTok概览 */}
        <div className="bg-gradient-to-br from-pink-500 to-red-600 rounded-lg shadow p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Zap className="w-8 h-8 mr-3" />
              <h3 className="text-xl font-bold">TikTok Shop</h3>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{comparisonData.tiktok.products}</div>
              <div className="text-pink-200">产品数量</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-pink-200">平均价格</div>
              <div className="text-lg font-semibold">${comparisonData.tiktok.avgPrice.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-pink-200">平均评分</div>
              <div className="text-lg font-semibold">{comparisonData.tiktok.avgRating.toFixed(1)}</div>
            </div>
            <div className="col-span-2">
              <div className="text-sm text-pink-200">总销量</div>
              <div className="text-lg font-semibold">{comparisonData.tiktok.sales.toLocaleString()}</div>
            </div>
          </div>
        </div>

        {/* Amazon概览 */}
        <div className="bg-gradient-to-br from-orange-500 to-yellow-600 rounded-lg shadow p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <ShoppingBag className="w-8 h-8 mr-3" />
              <h3 className="text-xl font-bold">Amazon</h3>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{comparisonData.amazon.products}</div>
              <div className="text-orange-200">产品数量</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-orange-200">平均价格</div>
              <div className="text-lg font-semibold">${comparisonData.amazon.avgPrice.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-sm text-orange-200">平均评分</div>
              <div className="text-lg font-semibold">{comparisonData.amazon.avgRating.toFixed(1)}</div>
            </div>
            <div className="col-span-2">
              <div className="text-sm text-orange-200">总销量</div>
              <div className="text-lg font-semibold">{comparisonData.amazon.sales.toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 详细对比图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 分类产品数量对比 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">各分类产品数量对比</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryComparison}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--tooltip-bg)',
                  border: '1px solid var(--tooltip-border)',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="tiktok" fill="#EF4444" name="TikTok" />
              <Bar dataKey="amazon" fill="#FF9500" name="Amazon" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 平台产品分布 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">平台产品分布</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={platformDistribution}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {platformDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 价格对比 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">各分类平均价格对比</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={categoryComparison}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis tickFormatter={(value) => `$${value}`} />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'var(--tooltip-bg)',
                border: '1px solid var(--tooltip-border)',
                borderRadius: '8px'
              }}
              formatter={(value: any) => [`$${value}`, '平均价格']}
            />
            <Bar dataKey="tiktokPrice" fill="#EF4444" name="TikTok" />
            <Bar dataKey="amazonPrice" fill="#FF9500" name="Amazon" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* 平台优势分析 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">平台优势分析</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* TikTok优势 */}
          <div className="border border-pink-200 dark:border-pink-800 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <Zap className="w-6 h-6 text-pink-500 mr-2" />
              <h4 className="font-semibold text-gray-900 dark:text-white">TikTok 优势</h4>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center">
                <div className="w-2 h-2 bg-pink-500 rounded-full mr-2"></div>
                更低的平均价格区间
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-pink-500 rounded-full mr-2"></div>
                快速传播和病毒式营销
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-pink-500 rounded-full mr-2"></div>
                年轻用户群体，时尚敏感度高
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-pink-500 rounded-full mr-2"></div>
                短视频展示，互动性强
              </li>
            </ul>
          </div>

          {/* Amazon优势 */}
          <div className="border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <ShoppingBag className="w-6 h-6 text-orange-500 mr-2" />
              <h4 className="font-semibold text-gray-900 dark:text-white">Amazon 优势</h4>
            </div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                更成熟的产品数量和品类
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                完善的物流和售后服务
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                更高的用户信任度
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                稳定的购买转化率
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlatformComparison;
