import React from 'react';
import { Sparkles, ShieldCheck, PieChart, TrendingUp, AlertCircle } from 'lucide-react';
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
  const moneyMood = insights?.money_mood || {
    mood: '🌿 Balanced',
    description: 'Your spending is currently under control.'
  };

  const list = insights?.insights || [];

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-20 md:pb-8">
      {/* Header */}
      <div className="border-b border-[#ebdcd0]/60 pb-4">
        <h1 className="text-2xl font-black text-[#1f2937] tracking-tight flex items-center gap-2">
          <span>✦</span> MoneyLens Financial Insights
        </h1>
        <p className="text-xs text-[#6b7280] font-medium mt-0.5">
          Rule-based spending insights and Money Mood engine generated 100% locally with Python.
        </p>
      </div>

      {/* Money Mood Card */}
      <div className="pin-card pastel-yellow rounded-3xl p-6 sm:p-8 space-y-3 shadow-sm">
        <div className="text-xs font-extrabold uppercase tracking-wider text-[#856404]">
          Your Current Money Mood
        </div>
        <div className="text-3xl font-black text-[#1f2937]">
          {moneyMood.mood}
        </div>
        <p className="text-xs sm:text-sm text-[#856404] leading-relaxed font-medium">
          {moneyMood.description}
        </p>
      </div>

      {/* Financial Insights List */}
      <div className="space-y-4">
        <h3 className="text-sm font-extrabold text-[#1f2937] uppercase tracking-wider flex items-center gap-1.5">
          <Sparkles className="w-4 h-4 text-[#5c3882]" /> Spending Discovery Pins
        </h3>

        {list.length === 0 ? (
          <div className="pastel-cream rounded-3xl p-8 text-center space-y-3 border border-[#ebdcd0]">
            <p className="text-xs text-[#6b7280]">
              No transactions recorded yet. Add expenses to unlock financial insights.
            </p>
            <button
              onClick={onLoadSample}
              disabled={loadingSample}
              className="px-5 py-2.5 rounded-full bg-[#1f2937] text-white text-xs font-bold shadow-md min-h-[44px]"
            >
              Try Sample Data
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {list.map((item, idx) => (
              <div
                key={idx}
                className="pin-card pastel-cream rounded-3xl p-6 border border-[#ebdcd0] space-y-2 shadow-sm"
              >
                <div className="text-base font-extrabold text-[#1f2937] flex items-center gap-2">
                  <span>✦</span> {item.title}
                </div>
                <p className="text-xs text-[#4b5563] leading-relaxed font-medium">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Privacy Guarantee Footer Note */}
      <div className="pastel-sage rounded-3xl p-5 border border-[#d4e5d4] flex items-center gap-3 text-xs text-[#2d5e2e]">
        <ShieldCheck className="w-5 h-5 shrink-0" />
        <span className="font-semibold">
          100% Local & Privacy Safe: Insights are computed entirely on your device using Python rules — zero data sent to external AI servers.
        </span>
      </div>
    </div>
  );
};
