import { getRiskColor } from '../../utils/formatters';

interface Props {
  score: number;
  level: string;
  size?: number;
}

export default function RiskGauge({ score, level, size = 160 }: Props) {
  const color = getRiskColor(level);
  const radius = (size - 20) / 2;
  const circumference = Math.PI * radius;
  const progress = (score / 100) * circumference;
  const center = size / 2;

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        {/* Background arc */}
        <path
          d={`M 10 ${center} A ${radius} ${radius} 0 0 1 ${size - 10} ${center}`}
          fill="none"
          stroke="#334155"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {/* Progress arc */}
        <path
          d={`M 10 ${center} A ${radius} ${radius} 0 0 1 ${size - 10} ${center}`}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${progress} ${circumference}`}
          style={{ filter: `drop-shadow(0 0 6px ${color}40)` }}
        />
        {/* Score text */}
        <text x={center} y={center - 5} textAnchor="middle" fill="white" fontSize="28" fontWeight="bold">
          {score.toFixed(0)}%
        </text>
        <text x={center} y={center + 15} textAnchor="middle" fill={color} fontSize="12" fontWeight="500" style={{ textTransform: 'uppercase' }}>
          {level} risk
        </text>
      </svg>
    </div>
  );
}
