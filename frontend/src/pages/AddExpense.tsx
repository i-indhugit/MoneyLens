import React, { useState } from 'react';
import {
  Upload,
  PlusCircle,
  AlertCircle,
  CheckCircle2,
  FileSpreadsheet,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';

interface AddExpenseProps {
  onSuccess: () => void;
  onLoadSample: () => void;
  loadingSample: boolean;
}

const CATEGORIES = [
  'Auto Detect', 'Food', 'Travel', 'Shopping', 'Entertainment',
  'Bills', 'Healthcare', 'Housing', 'Education', 'Income', 'Other'
];

export const AddExpensePage: React.FC<AddExpenseProps> = ({
  onSuccess,
  onLoadSample,
  loadingSample
}) => {
  const [activeTab, setActiveTab] = useState<'csv' | 'manual'>('csv');

  // CSV State
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [csvError, setCsvError] = useState<string | null>(null);
  const [csvSuccessMsg, setCsvSuccessMsg] = useState<string | null>(null);

  // Manual Form State
  const [desc, setDesc] = useState('');
  const [amount, setAmount] = useState<number | ''>('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [type, setType] = useState<'expense' | 'income'>('expense');
  const [category, setCategory] = useState('Auto Detect');
  const [submittingManual, setSubmittingManual] = useState(false);
  const [manualError, setManualError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setCsvError(null);
      setCsvSuccessMsg(null);
    }
  };

  const handleCsvSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setCsvError('Please select a CSV file first.');
      return;
    }

    setUploading(true);
    setCsvError(null);
    setCsvSuccessMsg(null);

    try {
      const res = await api.uploadCSV(file);
      setCsvSuccessMsg(`Successfully imported ${res.length} transactions from CSV!`);
      setFile(null);
      setTimeout(() => {
        onSuccess();
      }, 1000);
    } catch (err: any) {
      setCsvError(err.message || 'Failed to upload CSV file.');
    } finally {
      setUploading(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!desc || !amount || Number(amount) <= 0) {
      setManualError('Please provide a description and a valid positive amount.');
      return;
    }

    setSubmittingManual(true);
    setManualError(null);

    try {
      const finalCat = category === 'Auto Detect' ? undefined : category;
      await api.addTransaction({
        description: desc,
        amount: Number(amount),
        date,
        transaction_type: type,
        category: finalCat
      });
      setDesc('');
      setAmount('');
      onSuccess();
    } catch (err: any) {
      setManualError(err.message || 'Failed to add manual expense.');
    } finally {
      setSubmittingManual(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-20 md:pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <PlusCircle className="w-6 h-6 text-teal-600" />
            <span>Add Expenses / Upload CSV</span>
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Import CSV statements or quickly log manual expense and income items.
          </p>
        </div>

        <button
          onClick={onLoadSample}
          disabled={loadingSample}
          className="px-4 py-2 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 font-bold text-xs flex items-center gap-2 min-h-[44px]"
        >
          <Sparkles className="w-4 h-4 text-teal-600" />
          {loadingSample ? 'Loading...' : 'Load Sample Data'}
        </button>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => setActiveTab('csv')}
          className={`p-3.5 rounded-xl border text-center font-bold text-xs transition-all min-h-[44px] flex items-center justify-center gap-2 ${
            activeTab === 'csv'
              ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
              : 'fintech-card text-slate-600 hover:bg-slate-50'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4 text-teal-400" />
          <span>Upload CSV File</span>
        </button>

        <button
          onClick={() => setActiveTab('manual')}
          className={`p-3.5 rounded-xl border text-center font-bold text-xs transition-all min-h-[44px] flex items-center justify-center gap-2 ${
            activeTab === 'manual'
              ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
              : 'fintech-card text-slate-600 hover:bg-slate-50'
          }`}
        >
          <PlusCircle className="w-4 h-4 text-teal-400" />
          <span>Manual Entry Form</span>
        </button>
      </div>

      {/* Option A: CSV Upload */}
      {activeTab === 'csv' && (
        <form onSubmit={handleCsvSubmit} className="fintech-card p-6 sm:p-8 space-y-5">
          <div>
            <h3 className="text-base font-extrabold text-slate-900">Upload CSV Statement</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Upload any CSV statement containing Date, Description, and Amount columns. Categorization occurs automatically on import.
            </p>
          </div>

          {csvError && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start gap-2.5 font-medium">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{csvError}</span>
            </div>
          )}

          {csvSuccessMsg && (
            <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 text-xs flex items-center gap-2 font-bold">
              <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
              <span>{csvSuccessMsg}</span>
            </div>
          )}

          <div className="border-2 border-dashed border-slate-300 hover:border-slate-800 rounded-2xl p-8 text-center transition-all bg-slate-50/50">
            <input
              type="file"
              id="csv-file-input"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="csv-file-input" className="cursor-pointer flex flex-col items-center gap-3">
              <div className="p-3.5 rounded-xl bg-slate-200 text-slate-700">
                <Upload className="w-7 h-7 text-teal-600" />
              </div>
              <div>
                <span className="text-xs font-bold text-slate-900">
                  {file ? file.name : 'Click or drop a CSV file here'}
                </span>
                <p className="text-[11px] text-slate-500 mt-0.5 font-medium">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Supports Date, Description, Amount columns'}
                </p>
              </div>
            </label>
          </div>

          <div className="flex items-center justify-end pt-2">
            <button
              type="submit"
              disabled={uploading || !file}
              className="px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white font-bold text-xs shadow-sm min-h-[44px] flex items-center gap-2"
            >
              {uploading ? 'Processing CSV...' : 'Upload & Categorize'}
            </button>
          </div>
        </form>
      )}

      {/* Option B: Manual Expense Form */}
      {activeTab === 'manual' && (
        <form onSubmit={handleManualSubmit} className="fintech-card p-6 sm:p-8 space-y-4">
          <h3 className="text-base font-extrabold text-slate-900">Manual Expense Entry</h3>

          {manualError && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2 font-medium">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{manualError}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
              Description / Merchant *
            </label>
            <input
              type="text"
              placeholder="e.g. Swiggy, Uber, Amazon"
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              required
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs placeholder-slate-400 focus:outline-none focus:border-slate-900 min-h-[44px]"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
                Amount (₹) *
              </label>
              <input
                type="number"
                step="0.01"
                placeholder="450"
                value={amount}
                onChange={(e) => setAmount(e.target.value ? parseFloat(e.target.value) : '')}
                required
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs placeholder-slate-400 focus:outline-none focus:border-slate-900 min-h-[44px]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
                Date *
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs font-semibold focus:outline-none focus:border-slate-900 min-h-[44px]"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
                Type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as 'expense' | 'income')}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs font-semibold focus:outline-none focus:border-slate-900 min-h-[44px]"
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs font-semibold focus:outline-none focus:border-slate-900 min-h-[44px]"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end pt-2">
            <button
              type="submit"
              disabled={submittingManual}
              className="px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm min-h-[44px]"
            >
              {submittingManual ? 'Saving Expense...' : 'Save Expense Record'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
