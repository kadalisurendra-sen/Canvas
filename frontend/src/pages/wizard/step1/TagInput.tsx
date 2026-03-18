import React, { useState } from 'react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
}

export function TagInput({ tags, onChange }: TagInputProps) {
  const [input, setInput] = useState('');

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const trimmed = input.trim().toLowerCase();
      if (trimmed && !tags.includes(trimmed)) {
        onChange([...tags, trimmed]);
      }
      setInput('');
    }
  };

  const removeTag = (tag: string) => {
    onChange(tags.filter((t) => t !== tag));
  };

  return (
    <div className="flex flex-col gap-3">
      <label className="text-[14px] font-medium text-[#3D4353]">Search Tags</label>
      <div className="w-full flex flex-wrap gap-2 p-1.5 rounded-[8px] border border-[#CFD0D6] bg-white min-h-[44px]">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-primary/10 text-primary text-xs font-semibold"
          >
            {tag}
            <span
              className="material-symbols-outlined text-sm cursor-pointer hover:text-slate-900 transition-colors"
              onClick={() => removeTag(tag)}
            >
              close
            </span>
          </span>
        ))}
        <input
          className="border-none bg-transparent h-6 text-xs focus:ring-0 flex-1 min-w-[60px]"
          placeholder="Add tag..."
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      </div>
    </div>
  );
}
