import React from 'react';
import { Lock, ShieldCheck, FileCheck } from 'lucide-react';

export const PrivacyBanner: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-slate-900 border border-blue-500/20 rounded-2xl p-4 sm:p-5 shadow-lg mb-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 shrink-0">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <span>MoneyLens AI Privacy & Security Guarantee</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400 inline" />
            </h4>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              MoneyLens AI does not require banking credentials, bank passwords, OTPs, or UPI PINs. Users provide transaction statements or expense data themselves. Your financial data stays strictly under your control.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <FileCheck className="w-3.5 h-3.5" /> 100% File & Local Driven
          </span>
        </div>
      </div>
    </div>
  );
};
