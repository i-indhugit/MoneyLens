import React, { useState } from 'react';
import {
  Send,
  Zap,
  User,
  Bot,
  Calculator
} from 'lucide-react';
import { api } from '../services/api';
import { AskResponse } from '../types';

interface MessageItem {
  id: string;
  sender: 'user' | 'system';
  text: string;
  intent?: string;
  timestamp: string;
}

const QUICK_QUESTIONS = [
  "How much did I spend?",
  "How much did I spend on food?",
  "How much did I spend on shopping?",
  "What did I spend the most on?",
  "What is my biggest expense?",
  "How much did I earn?",
  "What is my balance?",
  "How much did I spend this month?",
  "Show unusual transactions."
];

export const AskMoneyLensPage: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'welcome-1',
      sender: 'system',
      text: "Hello! I am **Ask MoneyLens**. Ask questions about your spending, income, categories, monthly totals, or balance. I process queries 100% locally with Python — zero external AI APIs required.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const handleSend = async (textToAsk?: string) => {
    const qText = (textToAsk || question).trim();
    if (!qText) return;

    const userMsg: MessageItem = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: qText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToAsk) setQuestion('');
    setLoading(true);

    try {
      const res: AskResponse = await api.askQuestion(qText);

      const botMsg: MessageItem = {
        id: `system-${Date.now()}`,
        sender: 'system',
        text: res.answer,
        intent: res.intent,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errMsg: MessageItem = {
        id: `system-err-${Date.now()}`,
        sender: 'system',
        text: `Error processing question: ${err.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5 max-w-3xl mx-auto pb-20 md:pb-8">
      {/* Header */}
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <Bot className="w-6 h-6 text-teal-600" />
          <span>Ask MoneyLens</span>
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-0.5">
          Local financial question assistant powered by Python intent matching.
        </p>
      </div>

      {/* Suggested Questions */}
      <div className="space-y-2">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
          <Zap className="w-3.5 h-3.5 text-amber-600" /> Suggested Questions:
        </span>
        <div className="flex flex-wrap gap-2">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => handleSend(q)}
              disabled={loading}
              className="px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-slate-900 border border-slate-200 text-xs font-semibold transition-all text-left min-h-[36px]"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Box */}
      <div className="fintech-card p-5 min-h-[400px] max-h-[520px] overflow-y-auto space-y-4 flex flex-col justify-between">
        <div className="space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${
                m.sender === 'user' ? 'flex-row-reverse' : ''
              }`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                  m.sender === 'user'
                    ? 'bg-slate-900 text-white'
                    : 'bg-teal-100 text-teal-800'
                }`}
              >
                {m.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`max-w-[85%] sm:max-w-xl rounded-2xl p-4 space-y-1.5 text-xs leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-slate-900 text-white rounded-tr-none font-medium'
                    : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-none font-medium'
                }`}
              >
                {m.sender === 'system' && m.intent && (
                  <div className="flex items-center gap-2 pb-1.5 border-b border-slate-200">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700 uppercase">
                      Intent: {m.intent}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-100 text-teal-800 flex items-center gap-1">
                      <Calculator className="w-3 h-3" /> Python Math
                    </span>
                  </div>
                )}

                <div className="whitespace-pre-wrap">
                  {m.text}
                </div>

                <div className="text-[10px] text-slate-400 text-right">
                  {m.timestamp}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-slate-500 text-xs font-medium italic">
              <div className="w-6 h-6 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center animate-pulse">
                <Bot className="w-4 h-4" />
              </div>
              <span>Processing local Pandas calculation...</span>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 pt-3 border-t border-slate-200"
        >
          <input
            type="text"
            placeholder="Ask a question (e.g. How much did I spend on food?)"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading}
            className="flex-1 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 text-xs font-medium focus:outline-none focus:border-slate-900 min-h-[44px]"
          />

          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 min-h-[44px]"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
