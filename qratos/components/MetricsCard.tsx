import type { ReactNode } from 'react';

interface MetricsCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
  icon?: ReactNode;
}

export const MetricsCard = ({ 
  label, 
  value, 
  unit = '', 
  trend, 
  color = 'text-white',
  icon
}: MetricsCardProps) => {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 backdrop-blur-sm hover:border-slate-700 transition-colors">
      <div className="flex justify-between items-start mb-2">
        <span className="text-slate-400 text-xs uppercase tracking-wider font-semibold">{label}</span>
        {icon && <div className="text-slate-500">{icon}</div>}
      </div>
      <div className="flex items-baseline gap-2">
        <span className={`text-2xl font-mono font-bold ${color}`}>
          {value}
        </span>
        {unit && <span className="text-slate-500 text-sm font-mono">{unit}</span>}
      </div>
      {trend && (
        <div className="mt-2 text-xs">
          {trend === 'up' && <span className="text-emerald-400">↑ Increasing</span>}
          {trend === 'down' && <span className="text-rose-400">↓ Decreasing</span>}
          {trend === 'neutral' && <span className="text-slate-500">→ Stable</span>}
        </div>
      )}
    </div>
  );
};
