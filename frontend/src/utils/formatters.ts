export function formatSalary(amount: number | null): string {
  if (!amount) return 'N/A';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(num: number | null): string {
  if (!num) return 'N/A';
  return new Intl.NumberFormat('en-US').format(num);
}

export function getRiskColor(level: string): string {
  switch (level) {
    case 'low': return '#22c55e';
    case 'medium': return '#f59e0b';
    case 'high': return '#f97316';
    case 'critical': return '#ef4444';
    default: return '#94a3b8';
  }
}

export function getRiskBgColor(level: string): string {
  switch (level) {
    case 'low': return 'bg-green-500/20 text-green-400 border-green-500/30';
    case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
    default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  }
}

export function getRiskLabel(score: number): string {
  if (score >= 70) return 'Critical Risk';
  if (score >= 50) return 'High Risk';
  if (score >= 30) return 'Medium Risk';
  return 'Low Risk';
}
