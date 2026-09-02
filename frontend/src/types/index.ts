export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  transaction_type: 'expense' | 'income';
  category: string;
  created_at?: string;
}

export interface SummaryResponse {
  total_income: number;
  total_expenses: number;
  remaining_balance: number;
  average_expense: number;
  highest_expense?: {
    id: string;
    date: string;
    description: string;
    amount: number;
    category: string;
  };
  transaction_count: number;
}

export interface CategorySpending {
  category: string;
  total_amount: number;
  percentage: number;
  count: number;
}

export interface CategorySpendingResponse {
  categories: CategorySpending[];
  total: number;
}

export interface MonthlySpending {
  month: string;
  expenses: number;
  income: number;
  net: number;
}

export interface AnomalyItem {
  id: string;
  date: string;
  description: string;
  amount: number;
  category: string;
  reason: string;
}

export interface AnomalyResponse {
  total_anomalies: number;
  anomalies: AnomalyItem[];
  message?: string;
}

export interface MoneyMood {
  mood: string;
  description: string;
}

export interface InsightItem {
  type: string;
  title: string;
  description: string;
}

export interface InsightsResponse {
  money_mood: MoneyMood;
  insights: InsightItem[];
}

export interface AskResponse {
  question: string;
  answer: string;
  intent: string;
  result_data?: Record<string, any>;
}
