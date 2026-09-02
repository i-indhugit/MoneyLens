import React from 'react';
import {
  ShieldCheck,
  Upload,
  Bot,
  PieChart,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  FileSpreadsheet,
  FileText,
  Lock
} from 'lucide-react';
import { PrivacyBanner } from '../components/PrivacyBanner';

interface HomeProps {
  setActiveTab: (tab: string) => void;
  onTryDemo: () => void;
  loadingDemo: boolean;
}

export const Home: React.FC<HomeProps> = ({ setActiveTab, onTryDemo, loadingDemo }) => {
  return (
    <div className="space-y-8 py-2">
      <PrivacyBanner />

      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 p-8 sm:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-semibold">
            <Sparkles className="w-4 h-4" /> AI + Data Analytics for Personal Finance
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            See your spending.{' '}
            <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Understand your money.
            </span>{' '}
            Spend smarter.
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            MoneyLens AI analyzes your bank statements, CSVs, and Excel files to automatically categorize expenses, detect unusual spending, visualize financial patterns, and answer natural-language questions without requiring your bank credentials.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={() => setActiveTab('import')}
              className="px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-xl shadow-blue-600/25 transition-all flex items-center gap-2"
            >
              <Upload className="w-4 h-4" />
              Import Statement / File
            </button>

            <button
              onClick={onTryDemo}
              disabled={loadingDemo}
              className="px-6 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-sm transition-all flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-amber-400" />
              {loadingDemo ? 'Loading Demo Data...' : 'Try Demo Dataset'}
            </button>

            <button
              onClick={() => setActiveTab('assistant')}
              className="px-6 py-3.5 rounded-xl bg-indigo-950/60 hover:bg-indigo-900/60 text-indigo-300 border border-indigo-500/30 font-semibold text-sm transition-all flex items-center gap-2"
            >
              <Bot className="w-4 h-4 text-indigo-400" />
              Ask MoneyLens AI
            </button>
          </div>
        </div>
      </div>

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card glass-card-hover rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 w-fit border border-blue-500/20">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">4 Import Methods</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Upload CSVs, multi-sheet Excel files, PDF bank statements, or enter transactions manually.
          </p>
        </div>

        <div className="glass-card glass-card-hover rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 w-fit border border-indigo-500/20">
            <PieChart className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Hybrid Categorization</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Deterministic merchant keyword mapping with user correction memory for perfect categorization.
          </p>
        </div>

        <div className="glass-card glass-card-hover rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 w-fit border border-amber-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Isolation Forest ML</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Machine-learning anomaly detection flags unusual spending relative to your typical baseline.
          </p>
        </div>

        <div className="glass-card glass-card-hover rounded-2xl p-6 border border-slate-800 space-y-3">
          <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 w-fit border border-emerald-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Ask MoneyLens AI</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Ask natural language questions. All math is calculated 100% deterministically by Python & Pandas.
          </p>
        </div>
      </div>

      {/* Extensible PDF Statement Banner */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0">
            <FileText className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Extensible Bank Statement PDF Parser</h3>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Extracts tabular transactions, ignores bank header/footer noise, detects dates & amounts, and flags low-confidence records for human review before final import.
            </p>
          </div>
        </div>

        <button
          onClick={() => setActiveTab('import')}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs whitespace-nowrap flex items-center gap-2 shrink-0 shadow-lg shadow-indigo-600/20"
        >
          Try PDF Import <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
