import { getRiskBgColor } from '../../utils/formatters';

interface Props {
  level: string;
  score?: number;
  size?: 'sm' | 'md' | 'lg';
}

export default function RiskBadge({ level, score, size = 'md' }: Props) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium capitalize ${getRiskBgColor(level)} ${sizeClasses[size]}`}
    >
      <span
        className="w-2 h-2 rounded-full"
        style={{
          backgroundColor:
            level === 'low' ? '#22c55e' :
            level === 'medium' ? '#f59e0b' :
            level === 'high' ? '#f97316' :
            '#ef4444',
        }}
      />
      {level} {score !== undefined && `(${score.toFixed(0)}%)`}
    </span>
  );
}
