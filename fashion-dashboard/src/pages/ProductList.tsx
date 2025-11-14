import React, { useState, useEffect } from 'react';
import { Search, Filter, ExternalLink, Star, ShoppingCart, Heart } from 'lucide-react';
import { dataService, Product } from '../lib/dataService';

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recent');

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    filterAndSortProducts();
  }, [products, searchTerm, platformFilter, categoryFilter, sortBy]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await dataService.getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortProducts = async () => {
    const filters = {
      search: searchTerm,
      platform: platformFilter,
      category: categoryFilter,
      sortBy
    };
    
    const filtered = await dataService.getFilteredProducts(filters);
    setFilteredProducts(filtered);
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

  const formatPrice = (price: number, originalPrice?: number) => {
    const discount = originalPrice ? Math.round((1 - price / originalPrice) * 100) : 0;
    return {
      current: `$${price.toFixed(2)}`,
      original: originalPrice ? `$${originalPrice.toFixed(2)}` : null,
      discount
    };
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">产品列表</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">浏览和管理所有产品数据</p>
        </div>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          共 {filteredProducts.length} 个产品
        </div>
      </div>

      {/* 筛选和搜索 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 搜索 */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="搜索产品名称或店铺..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* 平台筛选 */}
          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">所有平台</option>
            <option value="tiktok">TikTok</option>
            <option value="amazon">Amazon</option>
          </select>

          {/* 分类筛选 */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">所有分类</option>
            <option value="tshirt">T恤</option>
            <option value="hoodie">卫衣</option>
            <option value="sweatshirt">连帽衫</option>
          </select>

          {/* 排序 */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="recent">最近更新</option>
            <option value="sales_desc">销量排序</option>
            <option value="rating_desc">评分排序</option>
            <option value="price_asc">价格从低到高</option>
            <option value="price_desc">价格从高到低</option>
          </select>
        </div>
      </div>

      {/* 产品网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredProducts.map((product) => {
          const priceInfo = formatPrice(product.price, product.original_price);
          return (
            <div key={product.id} className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow duration-200">
              {/* 产品图片 */}
              <div className="relative aspect-square overflow-hidden rounded-t-lg">
                <img
                  src={product.main_image_url || 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400'}
                  alt={product.product_name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.src = 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400';
                  }}
                />
                {priceInfo.discount > 0 && (
                  <div className="absolute top-2 left-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                    -{priceInfo.discount}%
                  </div>
                )}
              </div>

              {/* 产品信息 */}
              <div className="p-4">
                {/* 标签 */}
                <div className="flex gap-2 mb-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${getPlatformColor(product.platform)}`}>
                    {product.platform === 'tiktok' ? 'TikTok' : 'Amazon'}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded-full ${getCategoryColor(product.category)}`}>
                    {product.category === 'tshirt' ? 'T恤' : 
                     product.category === 'hoodie' ? '卫衣' : '连帽衫'}
                  </span>
                </div>

                {/* 产品名称 */}
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                  {product.product_name}
                </h3>

                {/* 评分和销量 */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm text-gray-600 dark:text-gray-400 ml-1">
                      {product.rating || 0}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-500 ml-2">
                      ({product.review_count || 0} 评价)
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {product.sales_count ? `${product.sales_count.toLocaleString()} 销量` : '暂无销量数据'}
                  </div>
                </div>

                {/* 价格 */}
                <div className="mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl font-bold text-red-600 dark:text-red-400">
                      {priceInfo.current}
                    </span>
                    {priceInfo.original && (
                      <span className="text-sm text-gray-500 dark:text-gray-400 line-through">
                        {priceInfo.original}
                      </span>
                    )}
                  </div>
                </div>

                {/* 店铺信息 */}
                {product.store_name && (
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    <span className="font-medium">店铺:</span> {product.store_name}
                  </div>
                )}

                {/* 操作按钮 */}
                <div className="flex space-x-2">
                  <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 rounded-lg text-sm transition-colors">
                    查看详情
                  </button>
                  <button className="p-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <Heart className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>

                {/* 外部链接 */}
                {product.product_url && (
                  <div className="mt-2">
                    <a
                      href={product.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center text-sm text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      <ExternalLink className="w-3 h-3 mr-1" />
                      查看原链接
                    </a>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* 空状态 */}
      {filteredProducts.length === 0 && !loading && (
        <div className="text-center py-12">
          <Filter className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            未找到匹配的产品
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            请尝试调整搜索条件或筛选条件
          </p>
        </div>
      )}
    </div>
  );
};

export default ProductList;
