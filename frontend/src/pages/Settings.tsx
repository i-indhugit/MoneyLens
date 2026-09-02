import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Trash2,
  RefreshCw,
  ShieldCheck,
  Lock,
  AlertTriangle,
  FileCheck,
  Smartphone,
  Download
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

  // PWA Prompt State
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
  }, []);

  const handleInstallPWA = async () => {
    if (!deferredPrompt) {
      alert("To install MoneyLens AI on your mobile or desktop device:\n\nChrome/Edge: Click the install icon in the address bar.\nSafari (iOS): Tap Share -> Add to Home Screen.");
      return;
    }
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setDeferredPrompt(null);
    }
  };

  const handleDeleteAll = async () => {
    setDeleting(true);
    try {
      await api.deleteAllData();
      setShowDeleteModal(false);
      setMsg('All transactions have been permanently deleted.');
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
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-slate-600" />
          <span>Settings & Data Management</span>
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-0.5">
          Manage local database storage, load sample dataset, install PWA app, and review privacy guarantees.
        </p>
      </div>

      {msg && (
        <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 text-xs font-bold">
          {msg}
        </div>
      )}

      {/* PWA App Install Banner */}
      <div className="fintech-card p-6 bg-slate-900 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-teal-400 font-bold text-xs">
            <Smartphone className="w-4 h-4" />
            <span>PROGRESSIVE WEB APP (PWA)</span>
          </div>
          <h3 className="text-base font-extrabold text-white">Install MoneyLens AI App</h3>
          <p className="text-xs text-slate-300 font-medium leading-relaxed">
            Add MoneyLens AI directly to your home screen for full-screen standalone application access.
          </p>
        </div>

        <button
          onClick={handleInstallPWA}
          className="px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-black text-xs shadow-sm flex items-center gap-2 shrink-0 min-h-[44px]"
        >
          <Download className="w-4 h-4" /> Install App
        </button>
      </div>

      {/* Privacy Information Card */}
      <div className="fintech-card p-6 space-y-4">
        <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-teal-600" />
          <span>100% Local & Privacy Guarantee</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed font-medium">
          MoneyLens AI operates completely offline on your device. Financial data is stored in your local database and never transmitted to external AI APIs.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-2.5 text-slate-800 font-semibold">
            <Lock className="w-4 h-4 text-teal-600 shrink-0" />
            <span>Zero Bank Credentials / Passwords</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-2.5 text-slate-800 font-semibold">
            <FileCheck className="w-4 h-4 text-teal-600 shrink-0" />
            <span>Zero External / Paid AI APIs</span>
          </div>
        </div>
      </div>

      {/* Reset Sample Data Card */}
      <div className="fintech-card p-6 bg-slate-50 border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
            <RefreshCw className="w-4 h-4 text-amber-600" />
            <span>Load Sample Data</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">
            Populate sample dataset transactions to test financial analytics and insights.
          </p>
        </div>

        <button
          onClick={onResetSample}
          disabled={loadingSample}
          className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm transition-all min-h-[44px] shrink-0"
        >
          {loadingSample ? 'Loading...' : 'Load Sample Data'}
        </button>
      </div>

      {/* Delete All Data Card */}
      <div className="fintech-card p-6 bg-rose-50/50 border-rose-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-extrabold text-rose-700 flex items-center gap-2">
            <Trash2 className="w-4 h-4" />
            <span>Delete All Data</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">
            Permanently clear all transaction records from your local database.
          </p>
        </div>

        <button
          onClick={() => setShowDeleteModal(true)}
          className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm transition-all min-h-[44px] shrink-0"
        >
          Delete All Data
        </button>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="fintech-card w-full max-w-md p-6 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center gap-3 text-rose-600">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h4 className="text-base font-extrabold text-slate-900">Delete All Transactions?</h4>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              Are you sure you want to permanently delete all transactions? This action will clear your local database.
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-500 hover:text-slate-900 min-h-[44px]"
              >
                Cancel
              </button>

              <button
                onClick={handleDeleteAll}
                disabled={deleting}
                className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-sm min-h-[44px]"
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
