import React, { useState } from 'react';
import {
  Upload,
  PlusCircle,
  AlertCircle,
  CheckCircle2,
  Paperclip,
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
      setCsvError('Please choose a CSV file first.');
      return;
    }

    setUploading(true);
    setCsvError(null);

    try {
      const res = await api.uploadCSV(file);
      setCsvSuccessMsg(`Imported ${res.length} transactions successfully!`);
      setFile(null);
      setTimeout(() => {
        onSuccess();
      }, 1000);
    } catch (err: any) {
      setCsvError(err.message || 'Failed to parse CSV file.');
    } finally {
      setUploading(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!desc || !amount || Number(amount) <= 0) {
      setManualError('Please enter a description and valid positive amount.');
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
      setManualError(err.message || 'Failed to save expense.');
    } finally {
      setSubmittingManual(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto pb-20 md:pb-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#ebdcd0]/60 pb-4">
        <div>
          <h1 className="text-2xl font-black text-[#1f2937] tracking-tight">
            Add Expense
          </h1>
          <p className="text-xs text-[#6b7280] font-medium mt-0.5">
            Log expenses manually or drop a transaction CSV file.
          </p>
        </div>
      </div>

      {/* Switcher Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => setActiveTab('csv')}
          className={`p-3.5 rounded-full border text-center font-bold text-xs transition-all min-h-[44px] ${
            activeTab === 'csv'
              ? 'bg-[#1f2937] text-white border-[#1f2937] shadow-sm'
              : 'pastel-cream border-[#ebdcd0] text-[#4b5563] hover:bg-[#eae3d8]'
          }`}
        >
          Upload CSV File
        </button>

        <button
          onClick={() => setActiveTab('manual')}
          className={`p-3.5 rounded-full border text-center font-bold text-xs transition-all min-h-[44px] ${
            activeTab === 'manual'
              ? 'bg-[#1f2937] text-white border-[#1f2937] shadow-sm'
              : 'pastel-cream border-[#ebdcd0] text-[#4b5563] hover:bg-[#eae3d8]'
          }`}
        >
          Manual Entry Form
        </button>
      </div>

      {/* CSV Dropzone Area (Requirement #18) */}
      {activeTab === 'csv' && (
        <form onSubmit={handleCsvSubmit} className="pastel-cream rounded-3xl p-6 sm:p-8 border border-[#ebdcd0] space-y-5 shadow-sm">
          {csvError && (
            <div className="p-4 rounded-2xl bg-[#fbebe6] border border-[#f5d5cc] text-[#993d29] text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{csvError}</span>
            </div>
          )}

          {csvSuccessMsg && (
            <div className="p-4 rounded-2xl bg-[#edf4ed] border border-[#d4e5d4] text-[#2d5e2e] text-xs flex items-center gap-2 font-bold">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{csvSuccessMsg}</span>
            </div>
          )}

          <div className="border-2 border-dashed border-[#ebdcd0] hover:border-[#1f2937] rounded-3xl p-8 text-center transition-all bg-[#faf7f2]/60">
            <input
              type="file"
              id="csv-dropzone-input"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="csv-dropzone-input" className="cursor-pointer flex flex-col items-center gap-3">
              <div className="w-14 h-14 rounded-full bg-[#f3eefa] text-[#5c3882] flex items-center justify-center text-xl">
                <Paperclip className="w-6 h-6" />
              </div>

              <div className="space-y-1">
                <div className="text-sm font-extrabold text-[#1f2937]">
                  {file ? file.name : 'Drop your CSV here'}
                </div>
                <p className="text-xs text-[#6b7280]">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : 'or choose a file from your computer'}
                </p>
              </div>
            </label>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
            <button
              type="button"
              onClick={onLoadSample}
              disabled={loadingSample}
              className="w-full sm:w-auto px-5 py-2.5 rounded-full bg-[#edf4ed] text-[#2d5e2e] border border-[#d4e5d4] font-bold text-xs transition-all min-h-[44px] flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {loadingSample ? 'Loading...' : 'Try Sample Data'}
            </button>

            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full sm:w-auto px-6 py-3 rounded-full bg-[#1f2937] hover:bg-[#374151] disabled:opacity-50 text-white font-bold text-xs shadow-md min-h-[44px]"
            >
              {uploading ? 'Parsing CSV...' : 'Upload Transactions'}
            </button>
          </div>
        </form>
      )}

      {/* Manual Expense Form */}
      {activeTab === 'manual' && (
        <form onSubmit={handleManualSubmit} className="pastel-cream rounded-3xl p-6 sm:p-8 border border-[#ebdcd0] space-y-4 shadow-sm">
          <h3 className="text-base font-extrabold text-[#1f2937]">Add Expense Record</h3>

          {manualError && (
            <div className="p-3.5 rounded-2xl bg-[#fbebe6] border border-[#f5d5cc] text-[#993d29] text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{manualError}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-[#4b5563] uppercase tracking-wider mb-1">
              Description
            </label>
            <input
              type="text"
              placeholder="e.g. Swiggy, Uber, Amazon"
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] text-[#1f2937] text-xs placeholder-[#9ca3af] focus:outline-none focus:border-[#1f2937] min-h-[44px]"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#4b5563] uppercase tracking-wider mb-1">
                Amount (₹)
              </label>
              <input
                type="number"
                step="0.01"
                placeholder="₹450"
                value={amount}
                onChange={(e) => setAmount(e.target.value ? parseFloat(e.target.value) : '')}
                required
                className="w-full px-4 py-3 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] text-[#1f2937] text-xs focus:outline-none focus:border-[#1f2937] min-h-[44px]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#4b5563] uppercase tracking-wider mb-1">
                Date
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] text-[#1f2937] text-xs focus:outline-none focus:border-[#1f2937] min-h-[44px]"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#4b5563] uppercase tracking-wider mb-1">
                Type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as 'expense' | 'income')}
                className="w-full px-4 py-3 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] text-[#1f2937] text-xs font-semibold focus:outline-none focus:border-[#1f2937] min-h-[44px]"
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#4b5563] uppercase tracking-wider mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-3 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] text-[#1f2937] text-xs font-semibold focus:outline-none focus:border-[#1f2937] min-h-[44px]"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end pt-3">
            <button
              type="submit"
              disabled={submittingManual}
              className="px-6 py-3 rounded-full bg-[#1f2937] hover:bg-[#374151] text-white font-bold text-xs shadow-md min-h-[44px]"
            >
              {submittingManual ? 'Saving Expense...' : 'Add Expense'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
