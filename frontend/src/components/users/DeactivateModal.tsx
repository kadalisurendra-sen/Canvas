import React from 'react';

interface DeactivateModalProps {
  userName: string;
  onClose: () => void;
  onConfirm: () => void;
}

export function DeactivateModal({ userName, onClose, onConfirm }: DeactivateModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
            <span className="material-symbols-outlined text-red-600">warning</span>
          </div>
          <h3 className="text-lg font-bold text-slate-900">Deactivate User</h3>
        </div>

        <p className="text-sm text-slate-600 mb-6">
          Are you sure you want to deactivate <strong>{userName}</strong>?
          They will lose access immediately.
        </p>

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-5 py-2 bg-red-600 text-white text-sm font-bold rounded-lg hover:bg-red-700 transition-all"
          >
            Deactivate
          </button>
        </div>
      </div>
    </div>
  );
}
