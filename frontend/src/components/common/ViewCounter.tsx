import { useEffect, useState } from 'react';
import { Eye, Users } from 'lucide-react';
import StatCard from './StatCard';
import { fetchViewStats, trackPageView } from '../../api/engagement';
import { useLanguage } from '../../i18n/LanguageContext';
import type { ViewStats } from '../../types/engagement';

export default function ViewCounter() {
  const { t } = useLanguage();
  const [stats, setStats] = useState<ViewStats | null>(null);

  useEffect(() => {
    trackPageView('/').catch(() => {});
    fetchViewStats().then(setStats).catch(() => {});
  }, []);

  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <StatCard
        title={t.views_totalVisitors}
        value={stats.total_views}
        icon={<Eye className="w-6 h-6" />}
        color="indigo"
      />
      <StatCard
        title={t.views_todayVisitors}
        value={stats.today_views}
        icon={<Users className="w-6 h-6" />}
        color="green"
      />
    </div>
  );
}
