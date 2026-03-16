interface Props {
  className?: string;
}

export default function Skeleton({ className = '' }: Props) {
  return (
    <div className={`animate-pulse bg-slate-700/50 rounded ${className}`} />
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-3">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-3 w-32" />
    </div>
  );
}

export function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 p-4">
      <Skeleton className="h-5 w-48" />
      <Skeleton className="h-4 w-24 hidden md:block" />
      <Skeleton className="h-4 w-20 ml-auto" />
      <Skeleton className="h-6 w-16 rounded-full" />
    </div>
  );
}

export function SkeletonCareerList({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl overflow-hidden">
      <div className="border-b border-slate-700/50 px-6 py-4 flex gap-4">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-24 hidden md:block" />
        <Skeleton className="h-4 w-20 ml-auto" />
        <Skeleton className="h-4 w-16" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="border-b border-slate-700/30 px-6 py-4 flex items-center gap-4">
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-3 w-24" />
          </div>
          <Skeleton className="h-4 w-20 hidden md:block" />
          <Skeleton className="h-4 w-16 hidden sm:block" />
          <Skeleton className="h-6 w-20 rounded-full" />
        </div>
      ))}
    </div>
  );
}
