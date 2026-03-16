import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { BarChart3, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { SkeletonCareerList } from '../components/common/Skeleton';
import RiskBadge from '../components/common/RiskBadge';
import { fetchCareers, fetchIndustryBreakdown, fetchCategories } from '../api/careers';
import { formatSalary } from '../utils/formatters';
import { useLanguage } from '../i18n/LanguageContext';
import type { PaginatedCareers, IndustryBreakdown } from '../types/career';

export default function DashboardPage() {
  const { t } = useLanguage();
  const [searchParams, setSearchParams] = useSearchParams();
  const [careers, setCareers] = useState<PaginatedCareers | null>(null);
  const [industries, setIndustries] = useState<IndustryBreakdown[]>([]);
  const [categories, setCategories] = useState<{ name: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  const page = parseInt(searchParams.get('page') || '1');
  const search = searchParams.get('search') || '';
  const category = searchParams.get('category') || '';
  const riskLevel = searchParams.get('risk_level') || '';
  const sortBy = searchParams.get('sort_by') || 'title';
  const sortOrder = searchParams.get('sort_order') || 'asc';

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => {});
    fetchIndustryBreakdown().then(setIndustries).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchCareers({
      page,
      page_size: 20,
      search: search || undefined,
      category: category || undefined,
      risk_level: riskLevel || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    })
      .then(setCareers)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, search, category, riskLevel, sortBy, sortOrder]);

  const updateParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    if (key !== 'page') params.set('page', '1');
    setSearchParams(params);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <BarChart3 className="w-8 h-8 text-indigo-400" />
        <h1 className="text-3xl font-bold text-white">{t.dash_title}</h1>
      </div>

      {/* Industry Breakdown Chart */}
      {industries.length > 0 && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">{t.dash_riskByIndustry}</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={industries} layout="vertical" margin={{ left: 120 }}>
              <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis type="category" dataKey="category" tick={{ fill: '#e2e8f0', fontSize: 12 }} width={120} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f8fafc' }}
                formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Avg Risk']}
              />
              <Bar dataKey="avg_risk_score" radius={[0, 4, 4, 0]}>
                {industries.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={
                      entry.avg_risk_score >= 70 ? '#ef4444' :
                      entry.avg_risk_score >= 50 ? '#f97316' :
                      entry.avg_risk_score >= 30 ? '#f59e0b' :
                      '#22c55e'
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-sm text-slate-400">{t.dash_filters}</span>
        </div>
        <input
          type="text"
          placeholder={t.dash_searchCareers}
          value={search}
          onChange={(e) => updateParam('search', e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
        />
        <select
          value={category}
          onChange={(e) => updateParam('category', e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-indigo-500"
        >
          <option value="">{t.dash_allCategories}</option>
          {categories.map((c) => (
            <option key={c.name} value={c.name}>{c.name} ({c.count})</option>
          ))}
        </select>
        <select
          value={riskLevel}
          onChange={(e) => updateParam('risk_level', e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-indigo-500"
        >
          <option value="">{t.dash_allRiskLevels}</option>
          <option value="low">{t.dash_lowRisk}</option>
          <option value="medium">{t.dash_mediumRisk}</option>
          <option value="high">{t.dash_highRisk}</option>
          <option value="critical">{t.dash_criticalRisk}</option>
        </select>
        <select
          value={`${sortBy}-${sortOrder}`}
          onChange={(e) => {
            const [sb, so] = e.target.value.split('-');
            updateParam('sort_by', sb);
            setTimeout(() => updateParam('sort_order', so), 0);
          }}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-indigo-500"
        >
          <option value="title-asc">{t.dash_nameAZ}</option>
          <option value="title-desc">{t.dash_nameZA}</option>
          <option value="risk_score-desc">{t.dash_highestRisk}</option>
          <option value="risk_score-asc">{t.dash_lowestRisk}</option>
          <option value="median_salary-desc">{t.dash_highestSalary}</option>
          <option value="median_salary-asc">{t.dash_lowestSalary}</option>
        </select>
      </div>

      {/* Career Table */}
      {loading ? (
        <SkeletonCareerList rows={10} />
      ) : careers && careers.items.length > 0 ? (
        <>
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700/50">
                  <th className="text-left text-sm font-medium text-slate-400 px-6 py-4">{t.dash_career}</th>
                  <th className="text-left text-sm font-medium text-slate-400 px-4 py-4 hidden md:table-cell">{t.dash_category}</th>
                  <th className="text-right text-sm font-medium text-slate-400 px-4 py-4 hidden sm:table-cell">{t.dash_salary}</th>
                  <th className="text-right text-sm font-medium text-slate-400 px-4 py-4">{t.dash_aiRisk}</th>
                  <th className="text-right text-sm font-medium text-slate-400 px-6 py-4 hidden lg:table-cell">{t.dash_growth}</th>
                </tr>
              </thead>
              <tbody>
                {careers.items.map((career) => (
                  <tr key={career.id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="px-6 py-4">
                      <Link to={`/career/${career.id}`} className="text-white hover:text-indigo-400 font-medium no-underline">
                        {career.title}
                      </Link>
                      <p className="text-xs text-slate-500 mt-0.5">{career.education_level}</p>
                    </td>
                    <td className="px-4 py-4 text-sm text-slate-400 hidden md:table-cell">{career.category}</td>
                    <td className="px-4 py-4 text-sm text-white text-right hidden sm:table-cell">{formatSalary(career.median_salary)}</td>
                    <td className="px-4 py-4 text-right">
                      {career.ensemble_prediction && (
                        <RiskBadge
                          level={career.ensemble_prediction.risk_level}
                          score={career.ensemble_prediction.automation_risk_score}
                          size="sm"
                        />
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-right hidden lg:table-cell">
                      <span className={career.growth_rate_pct && career.growth_rate_pct > 0 ? 'text-green-400' : 'text-red-400'}>
                        {career.growth_rate_pct ? `${career.growth_rate_pct > 0 ? '+' : ''}${career.growth_rate_pct}%` : 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6">
            <p className="text-sm text-slate-400">
              {t.dash_showing} {(careers.page - 1) * careers.page_size + 1}-
              {Math.min(careers.page * careers.page_size, careers.total)} {t.dash_of} {careers.total}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => updateParam('page', String(page - 1))}
                disabled={page <= 1}
                className="p-2 rounded-lg bg-slate-800 border border-slate-600 text-white disabled:opacity-30 hover:bg-slate-700"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="flex items-center px-4 text-sm text-slate-300">
                {t.dash_page} {careers.page} {t.dash_of} {careers.total_pages}
              </span>
              <button
                onClick={() => updateParam('page', String(page + 1))}
                disabled={page >= careers.total_pages}
                className="p-2 rounded-lg bg-slate-800 border border-slate-600 text-white disabled:opacity-30 hover:bg-slate-700"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-20 text-slate-400">
          {t.dash_noResults}
        </div>
      )}
    </div>
  );
}
