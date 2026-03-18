import React from 'react';

interface DeleteTemplateModalProps {
  templateName: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function DeleteTemplateModal({
  templateName, onConfirm, onCancel,
}: DeleteTemplateModalProps) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-rose-50 flex items-center justify-center">
            <span className="material-symbols-outlined text-rose-500">warning</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900">Delete Template</h2>
        </div>

        <p className="text-sm text-slate-600 mb-6">
          Are you sure you want to delete <strong>'{templateName}'</strong>?
          This action cannot be undone.
        </p>

        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-6 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-2 text-sm font-semibold text-white bg-rose-500 hover:bg-rose-600 rounded-lg transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
