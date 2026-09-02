import React from 'react';
import {
  Upload,
  PlusCircle,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  Layers,
  CheckCircle2,
  PieChart as PieIcon
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import {
  SummaryResponse,
  CategorySpending,
  MonthlySpending,
  AnomalyResponse,
  InsightsResponse
} from '../types';
import { CategoryBadge } from '../components/CategoryBadge';

interface DashboardProps {
  summary: SummaryResponse | null;
  categories: CategorySpending[];
  monthly: MonthlySpending[];
  anomalies: AnomalyResponse | null;
  insights: InsightsResponse | null;
  onNavigate: (tab: string) => void;
  onLoadSample: () => void;
  loadingSample: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({
  summary,
  categories,
  monthly,
  anomalies,
  insights,
  onNavigate,
  onLoadSample,
  loadingSample
}) => {

  // Empty State View
  if (!summary || summary.transaction_count === 0) {
    return (
      <div className="pastel-cream rounded-3xl p-8 sm:p-14 text-center border border-[#ebdcd0] space-y-6 my-6 shadow-sm max-w-2xl mx-auto">
        <div className="w-16 h-16 rounded-full bg-[#f3eefa] text-[#5c3882] flex items-center justify-center mx-auto text-2xl">
          ✦
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-[#1f2937] tracking-tight">
            Your money story starts here ✦
          </h2>
          <p className="text-xs sm:text-sm text-[#6b7280] leading-relaxed">
            Upload your transaction CSV or log your first expense to generate your visual spending cards, category pins, and Money Mood.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <button
            onClick={() => onNavigate('add-expense')}
            className="px-5 py-3 rounded-full bg-[#1f2937] hover:bg-[#374151] text-white font-bold text-xs shadow-md transition-all flex items-center gap-2 min-h-[44px]"
          >
            <Upload className="w-4 h-4" /> Upload CSV
          </button>

          <button
            onClick={() => onNavigate('add-expense')}
            className="px-5 py-3 rounded-full bg-[#fbebe6] hover:bg-[#f5d5cc] text-[#993d29] border border-[#f5d5cc] font-bold text-xs transition-all flex items-center gap-2 min-h-[44px]"
          >
            <PlusCircle className="w-4 h-4" /> Add Expense
          </button>

          <button
            onClick={onLoadSample}
            disabled={loadingSample}
            className="px-5 py-3 rounded-full bg-[#edf4ed] hover:bg-[#d4e5d4] text-[#2d5e2e] border border-[#d4e5d4] font-bold text-xs transition-all flex items-center gap-2 min-h-[44px]"
          >
            <Sparkles className="w-4 h-4" /> {loadingSample ? 'Loading...' : 'Try Sample Data'}
          </button>
        </div>
      </div>
    );
  }

  const moneyMood = insights?.money_mood || {
    mood: '🌿 Balanced',
    description: 'Your spending is currently under control.'
  };

  return (
    <div className="space-y-6 pb-20 md:pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-[#ebdcd0]/60 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-[#1f2937] tracking-tight">
            Good evening 👋
          </h1>
          <p className="text-xs sm:text-sm text-[#6b7280] font-medium mt-0.5">
            Your financial picture — September 2026
          </p>
        </div>

        <button
          onClick={onLoadSample}
          disabled={loadingSample}
          className="px-4 py-2 rounded-full bg-[#fdf8e6] hover:bg-[#f5ebbd] text-[#856404] border border-[#f5ebbd] text-xs font-bold transition-all flex items-center gap-1.5 min-h-[44px]"
        >
          <Sparkles className="w-3.5 h-3.5" />
          {loadingSample ? 'Resetting...' : 'Reset Sample Data'}
        </button>
      </div>

      {/* Pinterest Masonry Layout Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        
        {/* Card 1: Balance Card (Pastel Lavender) */}
        <div className="pin-card pastel-lavender rounded-3xl p-6 space-y-3">
          <div className="text-[11px] font-extrabold tracking-wider uppercase opacity-80">
            YOUR BALANCE
          </div>
          <div className="text-3xl sm:text-4xl font-black tracking-tight text-[#1f2937]">
            ₹{summary.remaining_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div className="flex items-center gap-1 text-xs font-bold text-[#5c3882]">
            <ArrowUpRight className="w-4 h-4" />
            <span>Positive net cash balance</span>
          </div>
        </div>

        {/* Card 2: Income & Spent Stacked Card (Sage & Terracotta) */}
        <div className="grid grid-cols-2 gap-4">
          <div className="pin-card pastel-sage rounded-3xl p-5 space-y-2">
            <div className="text-xs font-bold flex items-center gap-1">
              <span>💰</span> Income
            </div>
            <div className="text-xl sm:text-2xl font-black text-[#1f2937]">
              ₹{summary.total_income.toLocaleString('en-IN')}
            </div>
          </div>

          <div className="pin-card pastel-terracotta rounded-3xl p-5 space-y-2">
            <div className="text-xs font-bold flex items-center gap-1">
              <span>💸</span> Spent
            </div>
            <div className="text-xl sm:text-2xl font-black text-[#1f2937]">
              ₹{summary.total_expenses.toLocaleString('en-IN')}
            </div>
          </div>
        </div>

        {/* Card 3: Money Mood Card (Pastel Yellow) */}
        <div className="pin-card pastel-yellow rounded-3xl p-6 space-y-2.5">
          <div className="text-[11px] font-extrabold uppercase tracking-wider opacity-80">
            Your Money Mood
          </div>
          <div className="text-2xl font-black text-[#1f2937] flex items-center gap-2">
            {moneyMood.mood}
          </div>
          <p className="text-xs text-[#856404] leading-relaxed font-medium">
            {moneyMood.description}
          </p>
        </div>

        {/* Card 4: MoneyLens Insight Card (Editorial Terracotta/Cream) */}
        {insights && insights.insights.length > 0 && (
          <div className="pin-card pastel-terracotta rounded-3xl p-6 space-y-3 md:col-span-2">
            <div className="text-xs font-extrabold text-[#993d29] flex items-center gap-1.5">
              <span>✦</span> MoneyLens Insight
            </div>
            <h3 className="text-lg font-black text-[#1f2937] leading-snug">
              {insights.insights[0].title}
            </h3>
            <p className="text-xs text-[#993d29] leading-relaxed font-medium">
              {insights.insights[0].description}
            </p>
          </div>
        )}

        {/* Card 5: Category Visual Pins Grid */}
        <div className="pin-card pastel-cream rounded-3xl p-6 space-y-4 md:col-span-2 lg:col-span-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#1f2937] flex items-center gap-2">
              <span>📌</span> Spending Categories
            </h3>
            <span className="text-xs text-[#6b7280] font-medium">{categories.length} Categories</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {categories.map((cat) => (
              <div key={cat.category} className="p-3.5 rounded-2xl bg-[#faf7f2] border border-[#ebdcd0] space-y-2 hover:border-[#1f2937] transition-all">
                <CategoryBadge category={cat.category} />
                <div className="text-base font-black text-[#1f2937]">
                  ₹{cat.total_amount.toLocaleString('en-IN')}
                </div>
                <div className="text-[11px] text-[#6b7280] font-medium">
                  {cat.percentage}% of spending
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card 6: Recharts Monthly Spending Chart */}
        <div className="pin-card pastel-cream rounded-3xl p-6 space-y-4 md:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#1f2937] flex items-center gap-2">
              <span>📊</span> Monthly Spending
            </h3>
            <span className="text-xs text-[#6b7280] font-medium">Income vs Expenses</span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0eae1" />
                <XAxis dataKey="month" stroke="#9ca3af" fontSize={11} />
                <YAxis stroke="#9ca3af" fontSize={11} />
                <Tooltip
                  formatter={(value: any) => [`₹${Number(value).toLocaleString('en-IN')}`, '']}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#ebdcd0', borderRadius: '16px', fontSize: '12px', color: '#1f2937' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="expenses" fill="#f5d5cc" stroke="#993d29" name="Expenses" radius={[6, 6, 0, 0]} />
                <Bar dataKey="income" fill="#d4e5d4" stroke="#2d5e2e" name="Income" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Card 7: Unusual Transactions Pin List */}
        <div className="pin-card pastel-yellow rounded-3xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-extrabold text-[#856404] flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" /> Unusual Transactions
            </h3>
            <span className="text-[10px] font-bold text-[#856404] uppercase">IsolationForest ML</span>
          </div>

          {anomalies?.message ? (
            <p className="text-xs text-[#856404] leading-relaxed">
              {anomalies.message}
            </p>
          ) : anomalies?.anomalies && anomalies.anomalies.length > 0 ? (
            <div className="space-y-2.5 max-h-52 overflow-y-auto pr-1">
              {anomalies.anomalies.map((anom) => (
                <div key={anom.id} className="p-3 rounded-2xl bg-white/80 border border-[#f5ebbd] space-y-1 text-xs">
                  <div className="flex items-center justify-between font-bold text-[#1f2937]">
                    <span>{anom.description}</span>
                    <span className="text-[#993d29]">₹{anom.amount.toLocaleString('en-IN')}</span>
                  </div>
                  <p className="text-[11px] text-[#856404] leading-normal">{anom.reason}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-[#856404] flex items-center gap-1.5 font-medium">
              <CheckCircle2 className="w-4 h-4 text-[#2d5e2e]" />
              <span>No unusual spending flagged.</span>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
