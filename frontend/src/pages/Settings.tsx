import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Trash2,
  RefreshCw,
  ShieldCheck,
  Lock,
  AlertTriangle,
  FileCheck
} from 'lucide-react';
import { api } from '../services/api';

interface SettingsProps {
  onRefresh: () => void;
  onResetSample: () => void;
  loadingSample: boolean;
}

export const SettingsPage: React.FC<SettingsProps> = ({
  onRefresh,
  onResetSample,
  loadingSample
}) => {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const handleDeleteAll = async () => {
    setDeleting(true);
    try {
      await api.deleteAllData();
      setShowDeleteModal(false);
      setMsg('All transactions have been deleted.');
      onRefresh();
    } catch (err: any) {
      alert(`Failed to delete data: ${err.message}`);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-20 md:pb-8">
      {/* Header */}
      <div className="border-b border-[#ebdcd0]/60 pb-4">
        <h1 className="text-2xl font-black text-[#1f2937] tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-[#6b7280]" /> Settings & Data
        </h1>
        <p className="text-xs text-[#6b7280] font-medium mt-0.5">
          Reset sample data, manage local database storage, and view privacy information.
        </p>
      </div>

      {msg && (
        <div className="p-4 rounded-2xl bg-[#edf4ed] border border-[#d4e5d4] text-[#2d5e2e] text-xs font-bold">
          {msg}
        </div>
      )}

      {/* Privacy Information Card */}
      <div className="pastel-cream rounded-3xl p-6 border border-[#ebdcd0] space-y-4 shadow-sm">
        <h3 className="text-base font-extrabold text-[#1f2937] flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-[#216833]" />
          <span>100% Local & Private Guarantee</span>
        </h3>
        <p className="text-xs text-[#4b5563] leading-relaxed font-medium">
          MoneyLens AI runs completely offline on your computer. Financial data is stored in your local SQLite database and never leaves your device.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3.5 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] flex items-center gap-2.5 text-[#1f2937] font-semibold">
            <Lock className="w-4 h-4 text-[#216833] shrink-0" />
            <span>Zero Bank Passwords or Passcodes</span>
          </div>

          <div className="p-3.5 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] flex items-center gap-2.5 text-[#1f2937] font-semibold">
            <FileCheck className="w-4 h-4 text-[#216833] shrink-0" />
            <span>Zero Paid / External AI APIs</span>
          </div>
        </div>
      </div>

      {/* Reset Sample Data Card */}
      <div className="pastel-yellow rounded-3xl p-6 border border-[#f5ebbd] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <h3 className="text-sm font-extrabold text-[#856404] flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            <span>Reset Sample Data</span>
          </h3>
          <p className="text-xs text-[#856404] mt-0.5 font-medium">
            Load sample dataset to test Money Mood, category pins, and visual analytics.
          </p>
        </div>

        <button
          onClick={onResetSample}
          disabled={loadingSample}
          className="px-5 py-2.5 rounded-full bg-[#856404] hover:bg-[#664d03] text-white font-bold text-xs shadow-md transition-all min-h-[44px] shrink-0"
        >
          {loadingSample ? 'Loading...' : 'Reset Sample Data'}
        </button>
      </div>

      {/* Delete All Data Card */}
      <div className="pastel-terracotta rounded-3xl p-6 border border-[#f5d5cc] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
        <div>
          <h3 className="text-sm font-extrabold text-[#993d29] flex items-center gap-2">
            <Trash2 className="w-4 h-4" />
            <span>Delete All Data</span>
          </h3>
          <p className="text-xs text-[#993d29] mt-0.5 font-medium">
            Permanently delete all stored expense records from your local database.
          </p>
        </div>

        <button
          onClick={() => setShowDeleteModal(true)}
          className="px-5 py-2.5 rounded-full bg-[#993d29] hover:bg-[#7a3121] text-white font-bold text-xs shadow-md transition-all min-h-[44px] shrink-0"
        >
          Delete All Data
        </button>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#1f2937]/50 backdrop-blur-sm">
          <div className="pastel-cream rounded-3xl w-full max-w-md p-6 border border-[#ebdcd0] shadow-2xl space-y-4">
            <div className="flex items-center gap-3 text-[#993d29]">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h4 className="text-base font-extrabold text-[#1f2937]">Delete All Transactions?</h4>
            </div>

            <p className="text-xs text-[#4b5563] leading-relaxed font-medium">
              Are you sure you want to delete all your transactions? This action will clear your database.
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 rounded-full text-xs font-bold text-[#6b7280] hover:text-[#1f2937] min-h-[44px]"
              >
                Cancel
              </button>

              <button
                onClick={handleDeleteAll}
                disabled={deleting}
                className="px-5 py-2.5 rounded-full bg-[#993d29] hover:bg-[#7a3121] text-white font-bold text-xs shadow-md min-h-[44px]"
              >
                {deleting ? 'Deleting...' : 'Yes, Delete All'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
