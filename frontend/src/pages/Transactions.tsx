import React, { useState } from 'react';
import {
  Search,
  Filter,
  Trash2,
  Receipt,
  Plus
} from 'lucide-react';
import { Transaction } from '../types';
import { CategoryBadge } from '../components/CategoryBadge';
import { api } from '../services/api';

interface TransactionsProps {
  transactions: Transaction[];
  onRefresh: () => void;
  onNavigate: (tab: string) => void;
}

const CATEGORIES = [
  'All', 'Food', 'Travel', 'Shopping', 'Entertainment',
  'Bills', 'Healthcare', 'Housing', 'Education', 'Income', 'Other'
];

export const TransactionsPage: React.FC<TransactionsProps> = ({
  transactions,
  onRefresh,
  onNavigate
}) => {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const filtered = transactions.filter((tx) => {
    const matchesSearch =
      tx.description.toLowerCase().includes(search.toLowerCase()) ||
      tx.category.toLowerCase().includes(search.toLowerCase());
    const matchesCategory =
      categoryFilter === 'All' || tx.category.toLowerCase() === categoryFilter.toLowerCase();
    return matchesSearch && matchesCategory;
  });

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this transaction record?')) {
      await api.deleteTransaction(id);
      onRefresh();
    }
  };

  return (
    <div className="space-y-6 pb-20 md:pb-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[#ebdcd0]/60 pb-4">
        <div>
          <h1 className="text-2xl font-black text-[#1f2937] tracking-tight flex items-center gap-2">
            <span>≡</span> Transaction Feed
          </h1>
          <p className="text-xs text-[#6b7280] font-medium mt-0.5">
            Visual transaction card feed with instant search and category filtering.
          </p>
        </div>

        <button
          onClick={() => onNavigate('add-expense')}
          className="px-5 py-2.5 rounded-full bg-[#1f2937] hover:bg-[#374151] text-white font-bold text-xs shadow-md flex items-center gap-2 min-h-[44px]"
        >
          <Plus className="w-4 h-4" /> Add Expense
        </button>
      </div>

      {/* Search & Category Filter Controls */}
      <div className="pastel-cream rounded-3xl p-4 border border-[#ebdcd0] flex flex-col sm:flex-row items-center gap-3 shadow-sm">
        {/* Search */}
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-[#9ca3af] absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search transactions by description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-full bg-[#faf7f2] border border-[#ebdcd0] text-[#1f2937] text-xs placeholder-[#9ca3af] focus:outline-none focus:border-[#1f2937] min-h-[44px]"
          />
        </div>

        {/* Category Filter */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-[#9ca3af] shrink-0" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2.5 rounded-full bg-[#faf7f2] border border-[#ebdcd0] text-[#1f2937] text-xs font-semibold focus:outline-none focus:border-[#1f2937] w-full sm:w-48 min-h-[44px]"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>Category: {cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Visual Transaction Cards Feed (Mobile-First Card Layout) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.length === 0 ? (
          <div className="md:col-span-2 text-center py-10 text-xs text-[#6b7280] pastel-cream rounded-3xl p-8 border border-[#ebdcd0]">
            No transaction cards match your search query.
          </div>
        ) : (
          filtered.map((tx) => (
            <div
              key={tx.id}
              className="pin-card pastel-cream rounded-3xl p-5 border border-[#ebdcd0] space-y-3 relative flex flex-col justify-between"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="font-extrabold text-base text-[#1f2937] leading-snug">
                    {tx.description}
                  </div>
                  <div className="text-xs text-[#6b7280] font-medium">
                    {tx.date}
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span className={`text-lg font-black ${
                    tx.transaction_type === 'income' ? 'text-[#216833]' : 'text-[#1f2937]'
                  }`}>
                    {tx.transaction_type === 'income' ? '+' : '-'}₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-[#f0eae1]">
                <CategoryBadge category={tx.category} />

                <button
                  onClick={() => handleDelete(tx.id)}
                  className="p-2 rounded-full text-[#9ca3af] hover:text-[#993d29] hover:bg-[#fbebe6] transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                  title="Delete transaction"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
