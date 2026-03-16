import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, TrendingUp, AlertTriangle, Sparkles, ArrowRight, Brain, Target, BarChart3 } from 'lucide-react';
import StatCard from '../components/common/StatCard';
import RiskBadge from '../components/common/RiskBadge';
import { SkeletonCard } from '../components/common/Skeleton';
import { fetchStats, fetchTopRisk, fetchTopSafe } from '../api/careers';
import { formatSalary } from '../utils/formatters';
import { useLanguage } from '../i18n/LanguageContext';
import type { PlatformStats, CareerRiskItem } from '../types/career';

export default function HomePage() {
  const { t } = useLanguage();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [topRisk, setTopRisk] = useState<CareerRiskItem[]>([]);
  const [topSafe, setTopSafe] = useState<CareerRiskItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchStats(),
      fetchTopRisk(5),
      fetchTopSafe(5),
    ]).then(([s, r, safe]) => {
      setStats(s);
      setTopRisk(r);
      setTopSafe(safe);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const heroSection = (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/20 via-slate-900 to-purple-600/10" />
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 rounded-full px-4 py-1.5 mb-6">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span className="text-sm text-indigo-300">{t.home_badge}</span>
          </div>

          <h1 className="text-5xl lg:text-7xl font-bold text-white mb-6 leading-tight">
            {t.home_title1}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">{t.home_title2}</span>
          </h1>

          <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
            {t.home_subtitle.replace('{count}', String(stats?.total_careers || '500+'))}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-8 py-3.5 rounded-xl transition-all shadow-lg shadow-indigo-500/25 no-underline"
            >
              <BarChart3 className="w-5 h-5" />
              {t.home_exploreDashboard}
            </Link>
            <Link
              to="/career-dna"
              className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white font-medium px-8 py-3.5 rounded-xl border border-slate-600 transition-all no-underline"
            >
              <Target className="w-5 h-5" />
              {t.home_findDna}
            </Link>
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-medium px-8 py-3.5 rounded-xl transition-all shadow-lg shadow-purple-500/25 no-underline"
            >
              <Brain className="w-5 h-5" />
              {t.home_askFabrice}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );

  if (loading) {
    return (
      <div className="min-h-screen">
        {heroSection}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[0, 1, 2, 3].map((i) => <SkeletonCard key={i} />)}
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {heroSection}

      {/* Stats */}
      {stats && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-10">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title={t.home_careersAnalyzed}
              value={stats.total_careers}
              icon={<BarChart3 className="w-6 h-6" />}
              color="indigo"
            />
            <StatCard
              title={t.home_avgRiskScore}
              value={`${stats.avg_risk_score}%`}
              icon={<AlertTriangle className="w-6 h-6" />}
              color="amber"
            />
            <StatCard
              title={t.home_highRiskCareers}
              value={stats.careers_at_high_risk}
              subtitle={t.home_criticalOrHigh}
              icon={<AlertTriangle className="w-6 h-6" />}
              color="red"
            />
            <StatCard
              title={t.home_aiSafeCareers}
              value={stats.careers_at_low_risk}
              subtitle={t.home_lowAutomation}
              icon={<Shield className="w-6 h-6" />}
              color="green"
            />
          </div>
        </section>
      )}

      {/* Top Risk & Safe */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Most at risk */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <AlertTriangle className="w-6 h-6 text-red-400" />
              <h2 className="text-xl font-bold text-white">{t.home_mostAtRisk}</h2>
            </div>
            <div className="space-y-3">
              {topRisk.map((career) => (
                <Link
                  key={career.career_id}
                  to={`/career/${career.career_id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50 hover:bg-slate-900 transition-colors no-underline"
                >
                  <div>
                    <p className="font-medium text-white">{career.title}</p>
                    <p className="text-sm text-slate-400">{formatSalary(career.median_salary)}</p>
                  </div>
                  <RiskBadge level={career.risk_level} score={career.automation_risk_score} size="sm" />
                </Link>
              ))}
            </div>
            <Link to="/dashboard?sort_by=risk_score&sort_order=desc" className="flex items-center gap-1 text-indigo-400 text-sm mt-4 hover:text-indigo-300 no-underline">
              {t.home_viewAll} <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Most safe */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Shield className="w-6 h-6 text-green-400" />
              <h2 className="text-xl font-bold text-white">{t.home_mostSafe}</h2>
            </div>
            <div className="space-y-3">
              {topSafe.map((career) => (
                <Link
                  key={career.career_id}
                  to={`/career/${career.career_id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50 hover:bg-slate-900 transition-colors no-underline"
                >
                  <div>
                    <p className="font-medium text-white">{career.title}</p>
                    <p className="text-sm text-slate-400">{formatSalary(career.median_salary)}</p>
                  </div>
                  <RiskBadge level={career.risk_level} score={career.automation_risk_score} size="sm" />
                </Link>
              ))}
            </div>
            <Link to="/dashboard?sort_by=risk_score&sort_order=asc" className="flex items-center gap-1 text-indigo-400 text-sm mt-4 hover:text-indigo-300 no-underline">
              {t.home_viewAll} <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-2xl p-8 lg:p-12 text-center">
          <Brain className="w-12 h-12 text-indigo-400 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-4">{t.home_meetFabrice}</h2>
          <p className="text-lg text-slate-300 max-w-xl mx-auto mb-6">
            {t.home_meetFabriceDesc}
          </p>
          <Link
            to="/chat"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-8 py-3 rounded-xl transition-all no-underline"
          >
            <Sparkles className="w-5 h-5" />
            {t.home_startConversation}
          </Link>
        </div>
      </section>
    </div>
  );
}
