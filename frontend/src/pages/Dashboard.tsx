import React from 'react';
import {
  Wallet,
  CreditCard,
  DollarSign,
  TrendingUp,
  BarChart3,
  PieChart as PieIcon,
  AlertTriangle,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Upload,
  PlusCircle,
  Layers
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  SummaryResponse,
  CategorySpending,
  MonthlySpending,
  AnomalyResponse,
  InsightsResponse,
  Transaction
} from '../types';
import { MetricCard } from '../components/MetricCard';
import { CategoryBadge } from '../components/CategoryBadge';

interface DashboardProps {
  summary: SummaryResponse | null;
  categories: CategorySpending[];
  monthly: MonthlySpending[];
  anomalies: AnomalyResponse | null;
  insights: InsightsResponse | null;
  recentTransactions: Transaction[];
  onNavigate: (tab: string) => void;
  onLoadSample: () => void;
  loadingSample: boolean;
}

const COLORS = [
  '#0f172a', '#0d9488', '#2563eb', '#d97706', '#dc2626',
  '#7c3aed', '#059669', '#db2777', '#4b5563', '#475569'
];

export const Dashboard: React.FC<DashboardProps> = ({
  summary,
  categories,
  monthly,
  anomalies,
  insights,
  recentTransactions,
  onNavigate,
  onLoadSample,
  loadingSample
}) => {

  // Empty State View
  if (!summary || summary.transaction_count === 0) {
    return (
      <div className="fintech-card p-8 sm:p-14 text-center space-y-6 my-6 max-w-2xl mx-auto">
        <div className="w-16 h-16 rounded-2xl bg-slate-100 text-slate-700 flex items-center justify-center mx-auto shadow-sm">
          <PieIcon className="w-8 h-8 text-teal-600" />
        </div>

        <div className="space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Financial Dashboard
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-md mx-auto">
            Upload your CSV expense file, log transactions manually, or populate sample data to generate instant financial analytics and insights.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <button
            onClick={() => onNavigate('add-expense')}
            className="px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm transition-all flex items-center gap-2 min-h-[44px]"
          >
            <Upload className="w-4 h-4" /> Upload CSV Statement
          </button>

          <button
            onClick={() => onNavigate('add-expense')}
            className="px-5 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs border border-slate-200 transition-all flex items-center gap-2 min-h-[44px]"
          >
            <PlusCircle className="w-4 h-4" /> Add Expense
          </button>

          <button
            onClick={onLoadSample}
            disabled={loadingSample}
            className="px-5 py-3 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-800 font-bold text-xs border border-teal-200 transition-all flex items-center gap-2 min-h-[44px]"
          >
            <Sparkles className="w-4 h-4 text-teal-600" /> {loadingSample ? 'Loading...' : 'Load Sample Data'}
          </button>
        </div>
      </div>
    );
  }

  const moneyHealth = insights?.money_health || {
    status: 'Stable',
    summary: 'Your overall personal expenses are tracked and balanced.'
  };

  const topCategory = summary.top_spending_category || (categories[0]?.category || 'N/A');

  return (
    <div className="space-y-6 pb-20 md:pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Financial Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 font-medium mt-0.5">
            Overview of income, expenses, category breakdowns, and automated insights.
          </p>
        </div>

        <button
          onClick={onLoadSample}
          disabled={loadingSample}
          className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs border border-slate-200 transition-all flex items-center gap-2 min-h-[44px]"
        >
          <Sparkles className="w-4 h-4 text-teal-600" />
          {loadingSample ? 'Loading...' : 'Load Sample Data'}
        </button>
      </div>

      {/* Financial Overview 3 Key KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Current Balance"
          value={`₹${summary.remaining_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
          subtext={summary.remaining_balance >= 0 ? 'Net positive savings balance' : 'Net deficit balance'}
          icon={Wallet}
          color={summary.remaining_balance >= 0 ? 'teal' : 'rose'}
        />

        <MetricCard
          title="Total Income"
          value={`₹${summary.total_income.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
          subtext="Total earnings recorded"
          icon={DollarSign}
          color="emerald"
        />

        <MetricCard
          title="Total Expenses"
          value={`₹${summary.total_expenses.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
          subtext={`${summary.transaction_count} transaction records`}
          icon={CreditCard}
          color="navy"
        />
      </div>

      {/* Money Health & Primary MoneyLens Insight Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Money Health Summary Card */}
        <div className="fintech-card p-5 space-y-2 bg-slate-900 text-white">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span>Money Health Summary</span>
            <ShieldCheck className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-xl font-extrabold text-white">
            {moneyHealth.status}
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-medium">
            {moneyHealth.summary}
          </p>
        </div>

        {/* Primary MoneyLens Insight */}
        {insights && insights.insights.length > 0 && (
          <div className="fintech-card p-5 space-y-2 md:col-span-2 bg-teal-50/60 border-teal-200">
            <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-teal-800">
              <Sparkles className="w-4 h-4 text-teal-600" />
              <span>MoneyLens Insight</span>
            </div>
            <h3 className="text-base font-extrabold text-slate-900">
              {insights.insights[0].title}
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              {insights.insights[0].description}
            </p>
          </div>
        )}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Monthly Spending Trend Bar Chart */}
        <div className="fintech-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-teal-600" />
              <span>Monthly Spending Trend</span>
            </h3>
            <span className="text-xs text-slate-500 font-medium">Income vs Expenses</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  formatter={(value: any) => [`₹${Number(value).toLocaleString('en-IN')}`, '']}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '12px', fontSize: '12px', color: '#0f172a' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="expenses" fill="#f43f5e" name="Expenses" radius={[4, 4, 0, 0]} />
                <Bar dataKey="income" fill="#10b981" name="Income" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Donut Chart */}
        <div className="fintech-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-blue-600" />
              <span>Category Breakdown</span>
            </h3>
            <span className="text-xs text-slate-500 font-medium">Top Category: {topCategory}</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categories}
                  dataKey="total_amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: any) => [`₹${Number(value).toLocaleString('en-IN')}`, 'Amount']}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '12px', fontSize: '12px' }}
                />
                <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Category Breakdown Table / Grid & Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Category Breakdown Table */}
        <div className="fintech-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-slate-700" />
              <span>Category Spending Distribution</span>
            </h3>
            <span className="text-xs text-slate-500 font-medium">{categories.length} Categories</span>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {categories.map((cat) => (
              <div key={cat.category} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200/60 text-xs">
                <CategoryBadge category={cat.category} />
                <div className="text-right">
                  <div className="font-extrabold text-slate-900">
                    ₹{cat.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-[10px] text-slate-500 font-medium">
                    {cat.percentage}% of spending ({cat.count} txs)
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Unusual Transactions */}
        <div className="fintech-card p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Unusual Spending Anomalies</span>
            </h3>
            <span className="text-[10px] font-bold text-slate-500 uppercase">IsolationForest ML</span>
          </div>

          {anomalies?.message ? (
            <p className="text-xs text-slate-600 bg-amber-50 p-4 rounded-xl border border-amber-200 leading-relaxed font-medium">
              {anomalies.message}
            </p>
          ) : anomalies?.anomalies && anomalies.anomalies.length > 0 ? (
            <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
              {anomalies.anomalies.map((anom) => (
                <div key={anom.id} className="p-3 rounded-xl bg-amber-50/50 border border-amber-200/80 space-y-1 text-xs">
                  <div className="flex items-center justify-between font-bold text-slate-900">
                    <span>{anom.description}</span>
                    <span className="text-rose-600 font-extrabold">₹{anom.amount.toLocaleString('en-IN')}</span>
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug font-medium">{anom.reason}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-teal-700 bg-teal-50 p-4 rounded-xl border border-teal-200 flex items-center gap-2 font-medium">
              <CheckCircle2 className="w-4 h-4 text-teal-600" />
              <span>No unusual spending anomalies detected.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
