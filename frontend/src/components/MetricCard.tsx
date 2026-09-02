import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  subtext?: string;
  changePct?: number;
  icon: LucideIcon;
  color?: 'blue' | 'emerald' | 'rose' | 'amber' | 'indigo';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtext,
  changePct,
  icon: Icon,
  color = 'blue'
}) => {
  const colorMap = {
    blue: 'from-blue-500/10 to-blue-600/5 text-blue-400 border-blue-500/20',
    emerald: 'from-emerald-500/10 to-emerald-600/5 text-emerald-400 border-emerald-500/20',
    rose: 'from-rose-500/10 to-rose-600/5 text-rose-400 border-rose-500/20',
    amber: 'from-amber-500/10 to-amber-600/5 text-amber-400 border-amber-500/20',
    indigo: 'from-indigo-500/10 to-indigo-600/5 text-indigo-400 border-indigo-500/20',
  };

  const iconBgMap = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  };

  return (
    <div className={`glass-card glass-card-hover rounded-2xl p-5 bg-gradient-to-br ${colorMap[color]}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl border ${iconBgMap[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3">
        <div className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          {value}
        </div>
        
        <div className="mt-2 flex items-center justify-between">
          {subtext && (
            <p className="text-xs text-slate-400 font-medium">
              {subtext}
            </p>
          )}

          {changePct !== undefined && (
            <div className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
              changePct >= 0
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }`}>
              {changePct >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(changePct)}%</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
