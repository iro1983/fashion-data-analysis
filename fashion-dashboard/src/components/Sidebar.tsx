import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Package, 
  TrendingUp, 
  BarChart3, 
  Trophy,
  Menu,
  X
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  theme: 'light' | 'dark';
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle, theme }) => {
  const menuItems = [
    { path: '/dashboard', icon: Home, label: '仪表板', description: '数据概览' },
    { path: '/products', icon: Package, label: '产品列表', description: '所有产品' },
    { path: '/price-analysis', icon: TrendingUp, label: '价格分析', description: '价格趋势' },
    { path: '/platform-comparison', icon: BarChart3, label: '平台对比', description: '数据对比' },
    { path: '/ranking', icon: Trophy, label: '热度排行', description: '热门产品' },
  ];

  return (
    <>
      {/* 侧边栏 */}
      <div className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 shadow-lg transition-all duration-300 z-30 ${
        isOpen ? 'w-64' : 'w-16'
      }`}>
        {/* Logo 和标题 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          {isOpen && (
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                服装数据平台
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                TikTok & Amazon
              </p>
            </div>
          )}
          <button
            onClick={onToggle}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {isOpen ? (
              <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            )}
          </button>
        </div>

        {/* 导航菜单 */}
        <nav className="mt-6">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 mx-2 rounded-lg transition-all duration-200 group ${
                    isActive
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-r-2 border-blue-700 dark:border-blue-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`
                }
              >
                <Icon className={`w-5 h-5 ${isOpen ? 'mr-3' : 'mx-auto'}`} />
                {isOpen && (
                  <div>
                    <div className="font-medium">{item.label}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {item.description}
                    </div>
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* 底部信息 */}
        {isOpen && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
              <div className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                实时数据监控
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                数据更新: 每小时
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-500">
                最后更新: {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 移动端遮罩 */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={onToggle}
        />
      )}
    </>
  );
};

export default Sidebar;
