import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { TransactionsPage } from './pages/Transactions';
import { AddExpensePage } from './pages/AddExpense';
import { InsightsPage } from './pages/InsightsPage';
import { AskMoneyLensPage } from './pages/AskMoneyLens';
import { SettingsPage } from './pages/Settings';
import { api } from './services/api';
import {
  Transaction,
  SummaryResponse,
  CategorySpending,
  MonthlySpending,
  AnomalyResponse,
  InsightsResponse
} from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [categories, setCategories] = useState<CategorySpending[]>([]);
  const [monthly, setMonthly] = useState<MonthlySpending[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyResponse | null>(null);
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const [loadingSample, setLoadingSample] = useState(false);

  const refreshAllData = async () => {
    try {
      const [sumRes, catRes, monRes, anomRes, insRes, txRes] = await Promise.all([
        api.getSummary().catch(() => null),
        api.getCategories().catch(() => ({ categories: [], total: 0 })),
        api.getMonthly().catch(() => []),
        api.getAnomalies().catch(() => null),
        api.getInsights().catch(() => null),
        api.getTransactions().catch(() => []),
      ]);

      setSummary(sumRes);
      setCategories(catRes.categories || []);
      setMonthly(monRes || []);
      setAnomalies(anomRes);
      setInsights(insRes);
      setTransactions(txRes || []);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  const handleLoadSample = async () => {
    setLoadingSample(true);
    try {
      await api.loadSampleData();
      await refreshAllData();
      setActiveTab('dashboard');
    } catch (err: any) {
      alert(`Failed to load sample dataset: ${err.message}`);
    } finally {
      setLoadingSample(false);
    }
  };

  const handleAddExpenseSuccess = async () => {
    await refreshAllData();
    setActiveTab('dashboard');
  };

  return (
    <div className="min-h-screen bg-[#faf7f2] text-[#1f2937] flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'dashboard' && (
          <Dashboard
            summary={summary}
            categories={categories}
            monthly={monthly}
            anomalies={anomalies}
            insights={insights}
            onNavigate={setActiveTab}
            onLoadSample={handleLoadSample}
            loadingSample={loadingSample}
          />
        )}

        {activeTab === 'transactions' && (
          <TransactionsPage
            transactions={transactions}
            onRefresh={refreshAllData}
            onNavigate={setActiveTab}
          />
        )}

        {activeTab === 'add-expense' && (
          <AddExpensePage
            onSuccess={handleAddExpenseSuccess}
            onLoadSample={handleLoadSample}
            loadingSample={loadingSample}
          />
        )}

        {activeTab === 'insights' && (
          <InsightsPage
            insights={insights}
            onNavigate={setActiveTab}
            onLoadSample={handleLoadSample}
            loadingSample={loadingSample}
          />
        )}

        {activeTab === 'ask' && (
          <AskMoneyLensPage />
        )}

        {activeTab === 'settings' && (
          <SettingsPage
            onRefresh={refreshAllData}
            onResetSample={handleLoadSample}
            loadingSample={loadingSample}
          />
        )}
      </main>

      <footer className="hidden md:block border-t border-[#ebdcd0] bg-[#faf7f2] py-4 text-center text-xs text-[#857567] font-medium">
        moneylens ◉ — 100% Local & API-Free Pinterest-Style Personal Expense Assistant
      </footer>
    </div>
  );
}

export default App;
