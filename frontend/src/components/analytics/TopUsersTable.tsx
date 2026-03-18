/* TopUsersTable component */
import type { TopUser } from '../../services/analyticsService';

interface TopUsersTableProps {
  users: TopUser[];
}

function UserInitials({ name }: { name: string }) {
  const parts = name.split(' ');
  const initials = parts.map((p) => p[0]).join('').toUpperCase();
  return (
    <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
      <span className="text-xs font-bold text-slate-600">{initials}</span>
    </div>
  );
}

export function TopUsersTable({ users }: TopUsersTableProps) {
  return (
    <div className="bg-white p-8 rounded-[24px] border border-slate-100 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.05),0_2px_4px_-1px_rgba(0,0,0,0.03)]">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-bold text-slate-800 text-xl">Top Users by Activity</h3>
        <a href="#" className="text-xs font-bold text-[#5F2CFF] hover:underline">View All</a>
      </div>
      <div className="overflow-hidden rounded-lg border border-slate-200">
        <table className="w-full text-left">
          <thead className="bg-[#1E2345] text-white">
            <tr className="text-sm font-semibold tracking-wide">
              <th className="py-3 px-4 font-semibold">User</th>
              <th className="py-3 px-4 text-right">Eval.</th>
              <th className="py-3 px-4 text-right">Last Active</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, idx) => (
              <tr key={user.name} className={`group ${idx % 2 === 0 ? 'bg-white' : 'bg-[#F3F4F4]'}`}>
                <td className={`py-4 px-4 ${idx < users.length - 1 ? 'border-b border-slate-100' : ''}`}>
                  <div className="flex items-center gap-2">
                    <UserInitials name={user.name} />
                    <span className="text-sm font-semibold text-slate-700">{user.name}</span>
                  </div>
                </td>
                <td className={`py-4 px-4 text-right text-sm font-medium text-slate-600 ${idx < users.length - 1 ? 'border-b border-slate-100' : ''}`}>
                  {user.evaluations}
                </td>
                <td className={`py-4 px-4 text-right text-xs text-slate-400 ${idx < users.length - 1 ? 'border-b border-slate-100' : ''}`}>
                  {user.last_active}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
