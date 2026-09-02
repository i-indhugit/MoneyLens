import React, { useState } from 'react';
import {
  Home,
  Receipt,
  PlusCircle,
  Sparkles,
  MessageSquare,
  Settings,
  Menu,
  X
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Home', icon: Home, mobileLabel: 'Home' },
    { id: 'transactions', label: 'Transactions', icon: Receipt, mobileLabel: 'Transactions' },
    { id: 'add-expense', label: 'Add Expense', icon: PlusCircle, mobileLabel: 'Add' },
    { id: 'insights', label: 'Insights', icon: Sparkles, mobileLabel: 'Insights' },
    { id: 'ask', label: 'Ask MoneyLens', icon: MessageSquare, mobileLabel: 'Ask' },
    { id: 'settings', label: 'Settings', icon: Settings, mobileLabel: 'Settings' },
  ];

  const handleTabClick = (id: string) => {
    setActiveTab(id);
    setMobileDrawerOpen(false);
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-[#faf7f2]/90 backdrop-blur-md border-b border-[#ebdcd0]/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Pinterest Style Brand Logo */}
            <div
              className="flex items-center gap-2 cursor-pointer"
              onClick={() => handleTabClick('dashboard')}
            >
              <span className="w-8 h-8 rounded-full bg-[#1f2937] text-white flex items-center justify-center text-sm font-black shadow-sm">
                ◉
              </span>
              <div>
                <span className="font-extrabold text-xl tracking-tight text-[#1f2937] lowercase">
                  moneylens
                </span>
                <span className="text-[10px] text-[#857567] font-medium block leading-none">
                  Your money, beautifully understood.
                </span>
              </div>
            </div>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1.5">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleTabClick(item.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-[#1f2937] text-white shadow-md'
                        : 'text-[#4b5563] hover:text-[#1f2937] hover:bg-[#eae3d8]'
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-[#6b7280]'}`} />
                    {item.label}
                  </button>
                );
              })}
            </nav>

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileDrawerOpen(!mobileDrawerOpen)}
              className="md:hidden p-2 rounded-xl text-[#1f2937] hover:bg-[#eae3d8] focus:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-label="Toggle Navigation"
            >
              {mobileDrawerOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Drawer */}
        {mobileDrawerOpen && (
          <div className="md:hidden bg-[#faf7f2] border-b border-[#ebdcd0] px-4 py-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleTabClick(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-bold transition-all min-h-[44px] ${
                    isActive
                      ? 'bg-[#1f2937] text-white shadow-sm'
                      : 'text-[#4b5563] hover:bg-[#eae3d8]'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-[#6b7280]'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </header>

      {/* Mobile Bottom Navigation Bar (320px–414px viewports) */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-[#faf7f2]/95 backdrop-blur-md border-t border-[#ebdcd0] px-2 py-1.5 flex items-center justify-around shadow-lg">
        {navItems.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleTabClick(item.id)}
              className={`flex flex-col items-center justify-center py-1 px-2 rounded-2xl text-[10px] font-bold min-h-[44px] min-w-[44px] ${
                isActive ? 'text-[#1f2937] bg-[#eae3d8]/70' : 'text-[#6b7280] hover:text-[#1f2937]'
              }`}
            >
              <Icon className={`w-4 h-4 mb-0.5 ${isActive ? 'text-[#1f2937]' : 'text-[#6b7280]'}`} />
              <span>{item.mobileLabel}</span>
            </button>
          );
        })}
      </div>
    </>
  );
};
