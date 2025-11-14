import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ProductList from './pages/ProductList';
import PriceAnalysis from './pages/PriceAnalysis';
import PlatformComparison from './pages/PlatformComparison';
import RankingList from './pages/RankingList';
import './App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    // 从本地存储加载主题设置
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark';
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return (
    <Router>
      <div className={`flex h-screen bg-gray-50 dark:bg-gray-900 ${theme === 'dark' ? 'dark' : ''}`}>
        {/* 侧边栏 */}
        <Sidebar 
          isOpen={sidebarOpen} 
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          theme={theme}
        />
        
        {/* 主内容区域 */}
        <div className={`flex-1 flex flex-col transition-all duration-300 ${
          sidebarOpen ? 'ml-64' : 'ml-16'
        }`}>
          {/* 顶部导航 */}
          <Header 
            onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
            theme={theme}
            onThemeToggle={toggleTheme}
          />
          
          {/* 主内容 */}
          <main className="flex-1 overflow-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/products" element={<ProductList />} />
              <Route path="/price-analysis" element={<PriceAnalysis />} />
              <Route path="/platform-comparison" element={<PlatformComparison />} />
              <Route path="/ranking" element={<RankingList />} />
            </Routes>
          </main>
        </div>
      </div>
      
      {/* Toast 通知 */}
      <Toaster 
        position="top-right" 
        theme={theme}
        toastOptions={{
          duration: 4000,
          style: {
            background: theme === 'dark' ? '#374151' : '#ffffff',
            color: theme === 'dark' ? '#f9fafb' : '#111827',
          }
        }}
      />
    </Router>
  );
}

export default App;
