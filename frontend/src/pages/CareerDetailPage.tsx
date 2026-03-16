import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, GraduationCap, TrendingUp, Users, DollarSign, Calendar } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell,
} from 'recharts';
import RiskGauge from '../components/predictions/RiskGauge';
import RiskBadge from '../components/common/RiskBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { fetchCareer } from '../api/careers';
import { formatSalary, formatNumber } from '../utils/formatters';
import { useLanguage } from '../i18n/LanguageContext';
import type { CareerDetail } from '../types/career';

export default function CareerDetailPage() {
  const { t } = useLanguage();
  const { id } = useParams<{ id: string }>();
  const [career, setCareer] = useState<CareerDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchCareer(parseInt(id))
        .then(setCareer)
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return <LoadingSpinner text={t.detail_loading} />;
  if (!career) return <div className="text-center py-20 text-slate-400">{t.detail_notFound}</div>;

  const ep = career.ensemble_prediction;
  const salaryData = ep ? [
    { year: t.detail_current, salary: career.median_salary || 0 },
    { year: t.detail_5year, salary: ep.salary_5yr_projection || 0 },
    { year: t.detail_10year, salary: ep.salary_10yr_projection || 0 },
  ] : [];

  const modelData = career.predictions.map((p) => ({
    name: p.model_name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    risk: p.automation_risk_score,
    stability: p.job_stability_score || 0,
    year: p.disruption_year || 2035,
  }));

  const skillData = career.skills
    .sort((a, b) => b.importance_score - a.importance_score)
    .slice(0, 8)
    .map(s => ({
      skill: s.skill_name.length > 18 ? s.skill_name.slice(0, 18) + '...' : s.skill_name,
      importance: s.importance_score,
      automation: s.automation_potential * 100,
    }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link to="/dashboard" className="inline-flex items-center gap-1 text-slate-400 hover:text-white mb-6 no-underline text-sm">
        <ArrowLeft className="w-4 h-4" /> {t.detail_backToDashboard}
      </Link>

      {/* Header */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8 mb-6">
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <h1 className="text-3xl font-bold text-white">{career.title}</h1>
              {ep && <RiskBadge level={ep.risk_level} score={ep.automation_risk_score} />}
            </div>
            <p className="text-slate-300 mb-6">{career.description}</p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-green-400" />
                <div>
                  <p className="text-xs text-slate-500">{t.detail_salary}</p>
                  <p className="text-sm font-medium text-white">{formatSalary(career.median_salary)}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-indigo-400" />
                <div>
                  <p className="text-xs text-slate-500">{t.detail_education}</p>
                  <p className="text-sm font-medium text-white">{career.education_level}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-400" />
                <div>
                  <p className="text-xs text-slate-500">{t.detail_employed}</p>
                  <p className="text-sm font-medium text-white">{formatNumber(career.employment_count)}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-amber-400" />
                <div>
                  <p className="text-xs text-slate-500">{t.detail_growth}</p>
                  <p className={`text-sm font-medium ${career.growth_rate_pct && career.growth_rate_pct > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {career.growth_rate_pct ? `${career.growth_rate_pct > 0 ? '+' : ''}${career.growth_rate_pct}%` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {ep && (
            <div className="flex flex-col items-center">
              <RiskGauge score={ep.automation_risk_score} level={ep.risk_level} size={180} />
              {ep.disruption_year && (
                <div className="flex items-center gap-2 mt-2">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  <span className="text-sm text-slate-300">{t.detail_aiDisruption}: ~{ep.disruption_year}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Salary Projection */}
        {salaryData.length > 0 && (
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">{t.detail_salaryProjection}</h2>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={salaryData}>
                <XAxis dataKey="year" tick={{ fill: '#94a3b8' }} />
                <YAxis tick={{ fill: '#94a3b8' }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  formatter={(value) => [formatSalary(Number(value)), 'Projected Salary']}
                />
                <Line type="monotone" dataKey="salary" stroke="#6366f1" strokeWidth={3} dot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Model Comparison */}
        {modelData.length > 0 && (
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">{t.detail_modelPredictions}</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={modelData}>
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  formatter={(value, name) => [
                    `${Number(value).toFixed(1)}%`,
                    name === 'risk' ? 'Risk Score' : 'Stability',
                  ]}
                />
                <Bar dataKey="risk" name="Risk" radius={[4, 4, 0, 0]}>
                  {modelData.map((_, i) => (
                    <Cell key={i} fill={i % 2 === 0 ? '#ef4444' : '#f97316'} />
                  ))}
                </Bar>
                <Bar dataKey="stability" name="Stability" radius={[4, 4, 0, 0]} fill="#22c55e" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Skills Analysis */}
        {skillData.length > 0 && (
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6 lg:col-span-2">
            <h2 className="text-lg font-semibold text-white mb-4">{t.detail_skillsAutomation}</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={skillData} layout="vertical" margin={{ left: 120 }}>
                <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
                <YAxis type="category" dataKey="skill" tick={{ fill: '#e2e8f0', fontSize: 12 }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                />
                <Bar dataKey="importance" name="Importance" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={12} />
                <Bar dataKey="automation" name="Automation %" fill="#ef444480" radius={[0, 4, 4, 0]} barSize={12} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
