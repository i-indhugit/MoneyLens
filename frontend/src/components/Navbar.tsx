import React, { useState } from 'react';
import {
  LayoutDashboard,
  Receipt,
  PlusCircle,
  TrendingUp,
  MessageSquare,
  Settings,
  ShieldCheck,
  Menu,
  X,
  PieChart
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', mobileLabel: 'Home', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions', mobileLabel: 'Transactions', icon: Receipt },
    { id: 'add-expense', label: 'Add Expense', mobileLabel: 'Add', icon: PlusCircle },
    { id: 'insights', label: 'Insights', mobileLabel: 'Insights', icon: TrendingUp },
    { id: 'ask', label: 'Ask MoneyLens', mobileLabel: 'Ask', icon: MessageSquare },
    { id: 'settings', label: 'Settings', mobileLabel: 'Settings', icon: Settings },
  ];

  const handleTabClick = (id: string) => {
    setActiveTab(id);
    setMobileMenuOpen(false);
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Professional Brand Logo */}
            <div
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => handleTabClick('dashboard')}
            >
              <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white shadow-sm">
                <PieChart className="w-5 h-5 text-teal-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-lg text-slate-900 tracking-tight">
                    MoneyLens AI
                  </span>
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-teal-50 text-teal-700 border border-teal-200">
                    100% Free & Local
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 font-medium hidden sm:block">
                  Understand your money. Make better decisions.
                </p>
              </div>
            </div>

            {/* Desktop Links */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleTabClick(item.id)}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-slate-900 text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                    {item.label}
                  </button>
                );
              })}
            </nav>

            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Hamburger Drawer Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-b border-slate-200 px-4 py-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleTabClick(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-xs font-bold transition-all min-h-[44px] ${
                    isActive
                      ? 'bg-slate-900 text-white'
                      : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </header>

      {/* Mobile Bottom Navigation Bar (320px–414px viewports) */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-slate-200 px-2 py-1.5 flex items-center justify-around shadow-lg">
        {navItems.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleTabClick(item.id)}
              className={`flex flex-col items-center justify-center py-1 px-2 rounded-lg text-[10px] font-semibold min-h-[44px] min-w-[44px] ${
                isActive ? 'text-slate-900 font-bold bg-slate-100' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              <Icon className={`w-4 h-4 mb-0.5 ${isActive ? 'text-teal-600' : 'text-slate-400'}`} />
              <span>{item.mobileLabel}</span>
            </button>
          );
        })}
      </div>
    </>
  );
};
