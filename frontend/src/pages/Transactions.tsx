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
    <div className="space-y-5 pb-20 md:pb-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <Receipt className="w-6 h-6 text-teal-600" />
            <span>Transaction Ledger</span>
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Search, filter, and delete personal expense and income records.
          </p>
        </div>

        <button
          onClick={() => onNavigate('add-expense')}
          className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm flex items-center gap-2 min-h-[44px]"
        >
          <Plus className="w-4 h-4" /> Add Expense
        </button>
      </div>

      {/* Filter Controls */}
      <div className="fintech-card p-4 flex flex-col sm:flex-row items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by merchant or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs placeholder-slate-400 focus:outline-none focus:border-slate-900 min-h-[44px]"
          />
        </div>

        {/* Category Dropdown */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs font-semibold focus:outline-none focus:border-slate-900 w-full sm:w-44 min-h-[44px]"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>Category: {cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Mobile-Friendly Transaction Cards (<640px Viewports) */}
      <div className="block sm:hidden space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500 fintech-card p-6">
            No transaction records match your search filter.
          </div>
        ) : (
          filtered.map((tx) => (
            <div key={tx.id} className="fintech-card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">{tx.date}</span>
                <CategoryBadge category={tx.category} />
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="font-bold text-sm text-slate-900 truncate max-w-[200px]">{tx.description}</span>
                <span className={`text-base font-extrabold ${tx.transaction_type === 'income' ? 'text-emerald-600' : 'text-slate-900'}`}>
                  {tx.transaction_type === 'income' ? '+' : '-'}₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="flex items-center justify-end pt-2 border-t border-slate-100">
                <button
                  onClick={() => handleDelete(tx.id)}
                  className="px-3 py-1.5 rounded-lg text-rose-600 hover:bg-rose-50 text-xs font-semibold flex items-center gap-1.5 min-h-[44px]"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Desktop Responsive Table (>=640px Viewports) */}
      <div className="hidden sm:block fintech-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold uppercase text-slate-500 tracking-wider">
                <th className="py-3.5 px-4">Date</th>
                <th className="py-3.5 px-4">Description</th>
                <th className="py-3.5 px-4">Category</th>
                <th className="py-3.5 px-4 text-right">Amount</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs font-medium">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No transactions match your search filter.
                  </td>
                </tr>
              ) : (
                filtered.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-semibold text-slate-600 whitespace-nowrap">
                      {tx.date}
                    </td>

                    <td className="py-3 px-4 font-extrabold text-slate-900 max-w-xs truncate">
                      {tx.description}
                    </td>

                    <td className="py-3 px-4">
                      <CategoryBadge category={tx.category} />
                    </td>

                    <td className={`py-3 px-4 font-black text-right whitespace-nowrap ${
                      tx.transaction_type === 'income' ? 'text-emerald-600' : 'text-slate-900'
                    }`}>
                      {tx.transaction_type === 'income' ? '+' : '-'}₹{tx.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>

                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={() => handleDelete(tx.id)}
                        className="p-2 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors min-h-[44px] min-w-[44px] inline-flex items-center justify-center"
                        title="Delete transaction"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
