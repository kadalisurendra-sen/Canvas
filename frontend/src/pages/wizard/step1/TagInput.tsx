import React, { useState } from 'react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
}

export function TagInput({ tags, onChange }: TagInputProps) {
  const [input, setInput] = useState('');

  const addTag = () => {
    const trimmed = input.trim().toLowerCase();
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed]);
    }
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      e.stopPropagation();
      addTag();
    }
    // Remove last tag on backspace if input is empty
    if (e.key === 'Backspace' && input === '' && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text');
    const newTags = pasted
      .split(/[,\n]+/)
      .map((t) => t.trim().toLowerCase())
      .filter((t) => t && !tags.includes(t));
    if (newTags.length > 0) {
      onChange([...tags, ...newTags]);
    }
  };

  const removeTag = (tag: string) => {
    onChange(tags.filter((t) => t !== tag));
  };

  return (
    <div className="flex flex-col gap-3">
      <label className="text-[14px] font-medium text-[#3D4353]">Search Tags</label>
      <div
        className="w-full flex flex-wrap gap-2 p-2 rounded-[8px] border border-[#CFD0D6] bg-white min-h-[44px] focus-within:ring-2 focus-within:ring-primary/30 focus-within:border-primary transition-all"
      >
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-primary/10 text-primary text-xs font-semibold"
          >
            {tag}
            <span
              className="material-symbols-outlined text-sm cursor-pointer hover:text-red-500 transition-colors"
              onClick={() => removeTag(tag)}
            >
              close
            </span>
          </span>
        ))}
        <div className="flex items-center gap-1 flex-1 min-w-[100px]">
          <input
            className="border-none bg-transparent h-7 text-xs focus:ring-0 flex-1 min-w-[60px] outline-none"
            placeholder={tags.length === 0 ? 'Type a tag and press Enter...' : 'Add more...'}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value.replace(',', ''))}
            onKeyDown={handleKeyDown}
            onBlur={() => { if (input.trim()) addTag(); }}
            onPaste={handlePaste}
          />
          {input.trim() && (
            <button
              type="button"
              onClick={(e) => { e.preventDefault(); addTag(); }}
              className="px-2 py-0.5 text-[10px] font-bold text-primary bg-primary/10 rounded hover:bg-primary/20 transition-colors flex-shrink-0"
            >
              Add
            </button>
          )}
        </div>
      </div>
      <p className="text-[10px] text-slate-400">
        Press Enter or comma to add. Backspace to remove last tag. You can also paste comma-separated values.
      </p>
    </div>
  );
}
