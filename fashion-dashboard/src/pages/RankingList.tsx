import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Star, ShoppingCart, ExternalLink } from 'lucide-react';
import { dataService, Product } from '../lib/dataService';

const RankingList: React.FC = () => {
  const [topProducts, setTopProducts] = useState<Product[]>([]);
  const [rankingType, setRankingType] = useState<'sales' | 'rating' | 'price'>('sales');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTopProducts();
  }, [rankingType]);

  const loadTopProducts = async () => {
    try {
      setLoading(true);
      const data = await dataService.getTopProducts(20);
      setTopProducts(data);
    } catch (error) {
      console.error('Failed to load top products:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankingIcon = (type: string) => {
    switch (type) {
      case 'sales':
        return <ShoppingCart className="w-5 h-5" />;
      case 'rating':
        return <Star className="w-5 h-5" />;
      case 'price':
        return <TrendingUp className="w-5 h-5" />;
      default:
        return <Trophy className="w-5 h-5" />;
    }
  };

  const getPlatformColor = (platform: string) => {
    return platform === 'tiktok' ? 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200' 
                                 : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      tshirt: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      hoodie: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      sweatshirt: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  const getRankingPosition = (index: number) => {
    const colors = [
      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200', // 1st
      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200', // 2nd
      'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200', // 3rd
      'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' // others
    ];
    return colors[Math.min(index, 3)];
  };

  const calculateScore = (product: Product) => {
    const salesWeight = 0.6;
    const ratingWeight = 0.4;
    
    const sales = product.sales_count || 0;
    const rating = product.rating || 0;
    
    return sales * salesWeight + rating * 1000;
  };

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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">热度排行</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">基于销量和评分的热门产品排行</p>
        </div>
        
        {/* 排行类型选择 */}
        <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setRankingType('sales')}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              rankingType === 'sales'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <ShoppingCart className="w-4 h-4 mr-2" />
            销量排行
          </button>
          <button
            onClick={() => setRankingType('rating')}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              rankingType === 'rating'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <Star className="w-4 h-4 mr-2" />
            评分排行
          </button>
          <button
            onClick={() => setRankingType('price')}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              rankingType === 'price'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            价格排行
          </button>
        </div>
      </div>

      {/* 排行列表 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <Trophy className="w-6 h-6 text-yellow-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {rankingType === 'sales' ? '销量排行榜' : 
               rankingType === 'rating' ? '评分排行榜' : '价格排行榜'}
            </h2>
          </div>
        </div>

        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {topProducts.map((product, index) => (
            <div key={product.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <div className="flex items-center space-x-4">
                {/* 排名 */}
                <div className="flex-shrink-0">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${getRankingPosition(index)}`}>
                    {index < 3 ? (
                      <span>
                        {index === 0 && '🥇'}
                        {index === 1 && '🥈'}
                        {index === 2 && '🥉'}
                      </span>
                    ) : (
                      index + 1
                    )}
                  </div>
                </div>

                {/* 产品图片 */}
                <div className="flex-shrink-0">
                  <img
                    src={product.main_image_url || 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=80'}
                    alt={product.product_name}
                    className="w-16 h-16 rounded-lg object-cover"
                    onError={(e) => {
                      e.currentTarget.src = 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=80';
                    }}
                  />
                </div>

                {/* 产品信息 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* 产品名称 */}
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1 truncate">
                        {product.product_name}
                      </h3>

                      {/* 标签 */}
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${getPlatformColor(product.platform)}`}>
                          {product.platform === 'tiktok' ? 'TikTok' : 'Amazon'}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getCategoryColor(product.category)}`}>
                          {product.category === 'tshirt' ? 'T恤' : 
                           product.category === 'hoodie' ? '卫衣' : '连帽衫'}
                        </span>
                      </div>

                      {/* 评分和销量 */}
                      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center">
                          <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                          <span>{product.rating || 0} ({product.review_count || 0})</span>
                        </div>
                        <div className="flex items-center">
                          <ShoppingCart className="w-4 h-4 mr-1" />
                          <span>{product.sales_count ? product.sales_count.toLocaleString() : 0} 销量</span>
                        </div>
                        {product.store_name && (
                          <span>店铺: {product.store_name}</span>
                        )}
                      </div>
                    </div>

                    {/* 价格和操作 */}
                    <div className="flex-shrink-0 text-right">
                      <div className="text-xl font-bold text-red-600 dark:text-red-400 mb-1">
                        ${product.price.toFixed(2)}
                      </div>
                      {product.original_price && product.original_price > product.price && (
                        <div className="text-sm text-gray-500 dark:text-gray-400 line-through mb-2">
                          ${product.original_price.toFixed(2)}
                        </div>
                      )}
                      
                      {/* 综合评分 */}
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        综合评分: {calculateScore(product).toFixed(0)}
                      </div>

                      {/* 操作按钮 */}
                      <div className="flex space-x-2">
                        <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-md transition-colors">
                          查看
                        </button>
                        {product.product_url && (
                          <a
                            href={product.product_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-1 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-sm rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors flex items-center"
                          >
                            <ExternalLink className="w-3 h-3 mr-1" />
                            链接
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg shadow p-6 text-white">
          <div className="flex items-center">
            <Trophy className="w-8 h-8 mr-3" />
            <div>
              <h3 className="text-lg font-semibold">排行榜TOP1</h3>
              <p className="text-yellow-100">
                {topProducts[0]?.product_name || '暂无数据'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow p-6 text-white">
          <div className="flex items-center">
            <Star className="w-8 h-8 mr-3" />
            <div>
              <h3 className="text-lg font-semibold">最高评分</h3>
              <p className="text-blue-100">
                {Math.max(...topProducts.map(p => p.rating || 0)).toFixed(1)} 星
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-teal-600 rounded-lg shadow p-6 text-white">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 mr-3" />
            <div>
              <h3 className="text-lg font-semibold">最高销量</h3>
              <p className="text-green-100">
                {Math.max(...topProducts.map(p => p.sales_count || 0)).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RankingList;
