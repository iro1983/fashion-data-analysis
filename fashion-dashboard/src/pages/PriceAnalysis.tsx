import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Calendar } from 'lucide-react';
import { dataService, PriceTrend } from '../lib/dataService';

const PriceAnalysis: React.FC = () => {
  const [priceTrends, setPriceTrends] = useState<PriceTrend[]>([]);
  const [timeRange, setTimeRange] = useState('30');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPriceTrends();
  }, [timeRange]);

  const loadPriceTrends = async () => {
    try {
      setLoading(true);
      // 这里可以根据时间范围过滤数据
      const data = await dataService.getPriceTrends();
      setPriceTrends(data);
    } catch (error) {
      console.error('Failed to load price trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = (trends: PriceTrend[]) => {
    return trends.map(trend => ({
      date: new Date(trend.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
      price: parseFloat(trend.avg_price),
      products: trend.product_count,
      discount: trend.avg_discount
    }));
  };

  const calculateStats = (trends: PriceTrend[]) => {
    if (trends.length === 0) return null;

    const prices = trends.map(t => parseFloat(t.avg_price));
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
    
    const firstPrice = prices[0];
    const lastPrice = prices[prices.length - 1];
    const priceChange = lastPrice - firstPrice;
    const priceChangePercent = ((priceChange / firstPrice) * 100).toFixed(2);

    return {
      maxPrice,
      minPrice,
      avgPrice,
      priceChange,
      priceChangePercent
    };
  };

  const chartData = formatChartData(priceTrends);
  const stats = calculateStats(priceTrends);

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">价格分析</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">价格趋势和市场分析</p>
        </div>
        
        {/* 时间范围选择 */}
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="7">最近7天</option>
          <option value="30">最近30天</option>
          <option value="90">最近90天</option>
        </select>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">平均价格</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">${stats.avgPrice.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">最高价格</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">${stats.maxPrice.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                <TrendingDown className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">最低价格</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">${stats.minPrice.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg ${
                parseFloat(stats.priceChangePercent) >= 0 
                  ? 'bg-green-100 dark:bg-green-900' 
                  : 'bg-red-100 dark:bg-red-900'
              }`}>
                <Calendar className={`w-6 h-6 ${
                  parseFloat(stats.priceChangePercent) >= 0 
                    ? 'text-green-600 dark:text-green-400' 
                    : 'text-red-600 dark:text-red-400'
                }`} />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">价格变化</p>
                <div className="flex items-center">
                  <p className={`text-2xl font-bold ${
                    parseFloat(stats.priceChangePercent) >= 0 
                      ? 'text-green-600 dark:text-green-400' 
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {parseFloat(stats.priceChangePercent) >= 0 ? '+' : ''}{stats.priceChangePercent}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 价格趋势图表 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">价格趋势</h3>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              fontSize={12}
            />
            <YAxis 
              fontSize={12}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'var(--tooltip-bg)',
                border: '1px solid var(--tooltip-border)',
                borderRadius: '8px'
              }}
              formatter={(value: any) => [`$${value}`, '平均价格']}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#3B82F6"
              strokeWidth={2}
              fill="url(#priceGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* 产品数量趋势 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">产品数量趋势</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'var(--tooltip-bg)',
                border: '1px solid var(--tooltip-border)',
                borderRadius: '8px'
              }}
              formatter={(value: any) => [value, '产品数量']}
            />
            <Line 
              type="monotone" 
              dataKey="products" 
              stroke="#10B981" 
              strokeWidth={3}
              dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 折扣趋势 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">平均折扣率</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" fontSize={12} />
            <YAxis 
              fontSize={12}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'var(--tooltip-bg)',
                border: '1px solid var(--tooltip-border)',
                borderRadius: '8px'
              }}
              formatter={(value: any) => [`${value}%`, '平均折扣']}
            />
            <Line 
              type="monotone" 
              dataKey="discount" 
              stroke="#F59E0B" 
              strokeWidth={3}
              dot={{ fill: '#F59E0B', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PriceAnalysis;
