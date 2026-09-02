import {
  Transaction,
  SummaryResponse,
  CategorySpendingResponse,
  MonthlySpending,
  AnomalyResponse,
  InsightsResponse,
  AskResponse
} from '../types';

// Use relative /api endpoint path so it works seamlessly on both web server and Android Capacitor PWA
const API_BASE = '/api';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Network response error' }));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Upload CSV
  uploadCSV: async (file: File): Promise<Transaction[]> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/transactions/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<Transaction[]>(res);
  },

  // Add Manual Transaction
  addTransaction: async (data: {
    description: string;
    amount: number;
    date?: string;
    transaction_type?: string;
    category?: string;
  }): Promise<Transaction> => {
    const res = await fetch(`${API_BASE}/transactions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<Transaction>(res);
  },

  // List Transactions
  getTransactions: async (params?: { search?: string; category?: string }): Promise<Transaction[]> => {
    const query = new URLSearchParams();
    if (params?.search) query.append('search', params.search);
    if (params?.category) query.append('category', params.category);

    const res = await fetch(`${API_BASE}/transactions?${query.toString()}`);
    return handleResponse<Transaction[]>(res);
  },

  // Delete Single Transaction
  deleteTransaction: async (id: string): Promise<{ message: string; success: boolean }> => {
    const res = await fetch(`${API_BASE}/transactions/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<{ message: string; success: boolean }>(res);
  },

  // Delete All Transactions
  deleteAllData: async (): Promise<{ message: string; success: boolean }> => {
    const res = await fetch(`${API_BASE}/transactions`, {
      method: 'DELETE',
    });
    return handleResponse<{ message: string; success: boolean }>(res);
  },

  // Load Sample Data
  loadSampleData: async (): Promise<Transaction[]> => {
    const res = await fetch(`${API_BASE}/transactions/sample-data`, {
      method: 'POST',
    });
    return handleResponse<Transaction[]>(res);
  },

  // Financial Analytics
  getSummary: async (): Promise<SummaryResponse> => {
    const res = await fetch(`${API_BASE}/analytics/summary`);
    return handleResponse<SummaryResponse>(res);
  },

  getCategories: async (): Promise<CategorySpendingResponse> => {
    const res = await fetch(`${API_BASE}/analytics/categories`);
    return handleResponse<CategorySpendingResponse>(res);
  },

  getMonthly: async (): Promise<MonthlySpending[]> => {
    const res = await fetch(`${API_BASE}/analytics/monthly`);
    return handleResponse<MonthlySpending[]>(res);
  },

  getAnomalies: async (): Promise<AnomalyResponse> => {
    const res = await fetch(`${API_BASE}/analytics/anomalies`);
    return handleResponse<AnomalyResponse>(res);
  },

  getInsights: async (): Promise<InsightsResponse> => {
    const res = await fetch(`${API_BASE}/insights`);
    return handleResponse<InsightsResponse>(res);
  },

  // Ask Question
  askQuestion: async (question: string): Promise<AskResponse> => {
    const res = await fetch(`${API_BASE}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    return handleResponse<AskResponse>(res);
  },
};
