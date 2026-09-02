import React from 'react';
import { Sparkles, ShieldCheck, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';
import { InsightsResponse } from '../types';

interface InsightsPageProps {
  insights: InsightsResponse | null;
  onNavigate: (tab: string) => void;
  onLoadSample: () => void;
  loadingSample: boolean;
}

export const InsightsPage: React.FC<InsightsPageProps> = ({
  insights,
  onNavigate,
  onLoadSample,
  loadingSample
}) => {
  const moneyHealth = insights?.money_health || {
    status: 'Stable',
    summary: 'Your overall personal expenses are tracked and balanced.'
  };

  const list = insights?.insights || [];

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-20 md:pb-8">
      {/* Header */}
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-teal-600" />
          <span>MoneyLens Insights & Money Health</span>
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-0.5">
          Automated rule-based financial insights and Money Health summary computed locally with Python.
        </p>
      </div>

      {/* Money Health Summary Banner */}
      <div className="fintech-card p-6 bg-slate-900 text-white space-y-3">
        <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
          <span>Money Health Status</span>
          <ShieldCheck className="w-4 h-4 text-teal-400" />
        </div>
        <div className="text-2xl font-black text-white">
          {moneyHealth.status}
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-medium">
          {moneyHealth.summary}
        </p>
      </div>

      {/* MoneyLens Insights List */}
      <div className="space-y-4">
        <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-teal-600" /> Automated Financial Insights
        </h3>

        {list.length === 0 ? (
          <div className="fintech-card p-8 text-center space-y-3">
            <p className="text-xs text-slate-500 font-medium">
              No expense records found. Import data or log expenses to generate automated financial insights.
            </p>
            <button
              onClick={onLoadSample}
              disabled={loadingSample}
              className="px-5 py-2.5 rounded-xl bg-slate-900 text-white text-xs font-bold shadow-sm min-h-[44px]"
            >
              Load Sample Data
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {list.map((item, idx) => (
              <div
                key={idx}
                className="fintech-card p-5 space-y-2"
              >
                <div className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
                  <span>{item.title}</span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed font-medium pl-6">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Privacy Guarantee Note */}
      <div className="fintech-card p-4 bg-slate-50 border-slate-200 flex items-center gap-3 text-xs text-slate-600 font-medium">
        <ShieldCheck className="w-5 h-5 text-teal-600 shrink-0" />
        <span>
          100% Local & Private: Insights are computed entirely on your device using Python rules — zero data sent to external AI servers.
        </span>
      </div>
    </div>
  );
};
