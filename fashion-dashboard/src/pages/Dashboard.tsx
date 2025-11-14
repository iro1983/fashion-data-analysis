import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';
import { TrendingUp, Package, DollarSign, Users } from 'lucide-react';
import { dataService, DatabaseStats, PlatformStats, PriceTrend } from '../lib/dataService';

const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#F97316'];

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [platformStats, setPlatformStats] = useState<PlatformStats[]>([]);
  const [priceTrends, setPriceTrends] = useState<PriceTrend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, platformData, trendsData] = await Promise.all([
        dataService.getDatabaseStats(),
        dataService.getPlatformStats(),
        dataService.getPriceTrends()
      ]);
      
      setStats(statsData);
      setPlatformStats(platformData);
      setPriceTrends(trendsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const platformChartData = platformStats.map(stat => ({
    name: `${stat.platform}-${stat.category}`,
    count: stat.count,
    avgPrice: parseFloat(stat.avg_price)
  }));

  const categoryPieData = stats?.category_distribution.map(item => ({
    name: item.category,
    value: item.count
  })) || [];

  const trendingData = priceTrends.slice(-7).map(trend => ({
    date: new Date(trend.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
    price: parseFloat(trend.avg_price),
    products: trend.product_count
  }));

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">数据仪表板</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">TikTok & Amazon 热销服装数据概览</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Package className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">总产品数</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.total_products || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <Users className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">活跃产品</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.active_products || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <TrendingUp className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">今日新增</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.today_new_products || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <DollarSign className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">数据库大小</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.database_size_mb || 0}MB</p>
            </div>
          </div>
        </div>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 平台分类统计 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">平台分类分布</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={platformChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--tooltip-bg)',
                  border: '1px solid var(--tooltip-border)',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="count" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 分类饼图 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">产品分类占比</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryPieData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {categoryPieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 价格趋势 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">近期价格趋势</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendingData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'var(--tooltip-bg)',
                border: '1px solid var(--tooltip-border)',
                borderRadius: '8px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#10B981" 
              strokeWidth={3}
              dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Dashboard;
