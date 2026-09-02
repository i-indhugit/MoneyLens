import React from 'react';

interface CategoryBadgeProps {
  category: string;
}

const CATEGORY_MAP: Record<string, { emoji: string; style: string }> = {
  Food: { emoji: '🍜', style: 'bg-[#fbebe6] text-[#993d29] border-[#f5d5cc]' },
  Travel: { emoji: '🚕', style: 'bg-[#edf4ed] text-[#2d5e2e] border-[#d4e5d4]' },
  Shopping: { emoji: '🛍️', style: 'bg-[#f3eefa] text-[#5c3882] border-[#e2d5f5]' },
  Entertainment: { emoji: '🎬', style: 'bg-[#fdf8e6] text-[#856404] border-[#f5ebbd]' },
  Bills: { emoji: '⚡', style: 'bg-[#eef6fc] text-[#1c5075] border-[#d2e6f5]' },
  Healthcare: { emoji: '🏥', style: 'bg-[#fceef0] text-[#942738] border-[#f8d0d6]' },
  Housing: { emoji: '🏠', style: 'bg-[#f0edf7] text-[#4d3a75] border-[#d8d1e8]' },
  Education: { emoji: '📚', style: 'bg-[#eaf4f4] text-[#256161] border-[#c9e4e4]' },
  Income: { emoji: '💰', style: 'bg-[#eaf6ec] text-[#216833] border-[#c6e6cd]' },
  Other: { emoji: '📦', style: 'bg-[#f3f4f6] text-[#4b5563] border-[#e5e7eb]' },
};

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category }) => {
  const item = CATEGORY_MAP[category] || CATEGORY_MAP.Other;

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${item.style}`}>
      <span>{item.emoji}</span>
      <span>{category}</span>
    </span>
  );
};
