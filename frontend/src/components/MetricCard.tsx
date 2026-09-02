import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  subtext?: string;
  icon: LucideIcon;
  color?: 'navy' | 'emerald' | 'rose' | 'teal' | 'amber';
}

const COLOR_MAP = {
  navy: { bg: 'bg-slate-50', text: 'text-slate-900', iconBg: 'bg-slate-100 text-slate-700' },
  emerald: { bg: 'bg-emerald-50/50', text: 'text-emerald-700', iconBg: 'bg-emerald-100 text-emerald-700' },
  rose: { bg: 'bg-rose-50/50', text: 'text-rose-700', iconBg: 'bg-rose-100 text-rose-700' },
  teal: { bg: 'bg-teal-50/50', text: 'text-teal-700', iconBg: 'bg-teal-100 text-teal-700' },
  amber: { bg: 'bg-amber-50/50', text: 'text-amber-700', iconBg: 'bg-amber-100 text-amber-700' },
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  color = 'navy'
}) => {
  const styles = COLOR_MAP[color] || COLOR_MAP.navy;

  return (
    <div className={`fintech-card p-5 space-y-3 ${styles.bg}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        <div className={`p-2 rounded-xl ${styles.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div>
        <div className={`text-2xl font-black tracking-tight ${styles.text}`}>
          {value}
        </div>
        {subtext && (
          <p className="text-xs text-slate-500 font-medium mt-1">
            {subtext}
          </p>
        )}
      </div>
    </div>
  );
};
