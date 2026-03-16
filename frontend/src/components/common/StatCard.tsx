import { useEffect, useState, useRef, type ReactNode } from 'react';

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  color?: string;
}

function useAnimatedCounter(target: number, duration = 1500) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          const start = performance.now();
          const animate = (now: number) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setCount(Math.round(eased * target));
            if (progress < 1) requestAnimationFrame(animate);
          };
          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.3 },
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target, duration]);

  return { count, ref };
}

export default function StatCard({ title, value, subtitle, icon, color = 'indigo' }: Props) {
  const colorMap: Record<string, string> = {
    indigo: 'from-indigo-500/20 to-indigo-600/5 border-indigo-500/30',
    green: 'from-green-500/20 to-green-600/5 border-green-500/30',
    red: 'from-red-500/20 to-red-600/5 border-red-500/30',
    amber: 'from-amber-500/20 to-amber-600/5 border-amber-500/30',
  };

  const isNumeric = typeof value === 'number';
  const hasPercent = typeof value === 'string' && value.endsWith('%');
  const numericValue = isNumeric ? value : hasPercent ? parseFloat(value) : 0;
  const shouldAnimate = isNumeric || hasPercent;
  const { count, ref } = useAnimatedCounter(numericValue);

  return (
    <div ref={ref} className={`bg-gradient-to-br ${colorMap[color] || colorMap.indigo} border rounded-xl p-6`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400 mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">
            {shouldAnimate ? (hasPercent ? `${count}%` : count) : value}
          </p>
          {subtitle && <p className="text-sm text-slate-400 mt-1">{subtitle}</p>}
        </div>
        <div className="text-slate-400">{icon}</div>
      </div>
    </div>
  );
}
