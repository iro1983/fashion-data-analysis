import React from 'react';
import { Menu, Bell, User, Search } from 'lucide-react';

interface HeaderProps {
  onSidebarToggle: () => void;
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
}

const Header: React.FC<HeaderProps> = ({ onSidebarToggle, theme, onThemeToggle }) => {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* 左侧 */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onSidebarToggle}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors lg:hidden"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          
          {/* 搜索框 */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="搜索产品、店铺或关键词..."
              className="pl-10 pr-4 py-2 w-80 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* 右侧 */}
        <div className="flex items-center space-x-4">
          {/* 主题切换 */}
          <button
            onClick={onThemeToggle}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title={theme === 'light' ? '切换到深色模式' : '切换到浅色模式'}
          >
            {theme === 'light' ? (
              <div className="w-5 h-5 text-yellow-500">🌙</div>
            ) : (
              <div className="w-5 h-5 text-yellow-400">☀️</div>
            )}
          </button>

          {/* 通知 */}
          <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative">
            <Bell className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {/* 用户头像 */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="hidden md:block">
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                管理员
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                超级用户
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 移动端搜索 */}
      <div className="mt-4 md:hidden">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="搜索产品、店铺或关键词..."
            className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
