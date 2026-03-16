import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, X, Search, GitCompareArrows, DollarSign, TrendingUp, Calendar, Shield } from 'lucide-react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, Legend,
} from 'recharts';
import RiskBadge from '../components/common/RiskBadge';
import RiskGauge from '../components/predictions/RiskGauge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { searchCareers, compareCareers } from '../api/careers';
import { formatSalary } from '../utils/formatters';
import { useLanguage } from '../i18n/LanguageContext';
import type { CareerDetail, CareerListItem } from '../types/career';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'];

export default function ComparePage() {
  const { t } = useLanguage();
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [results, setResults] = useState<CareerDetail[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CareerListItem[]>([]);
  const [searching, setSearching] = useState(false);
  const [activeSlot, setActiveSlot] = useState<number | null>(null);

  const handleSearch = async (q: string) => {
    setSearchQuery(q);
    if (q.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const res = await searchCareers(q.trim());
      setSearchResults(res.filter((r) => !selectedIds.includes(r.id)));
    } catch {
      setSearchResults([]);
    }
    setSearching(false);
  };

  const addCareer = (career: CareerListItem) => {
    if (selectedIds.length >= 4) return;
    setSelectedIds((prev) => [...prev, career.id]);
    setSearchQuery('');
    setSearchResults([]);
    setActiveSlot(null);
  };

  const removeCareer = (id: number) => {
    setSelectedIds((prev) => prev.filter((x) => x !== id));
    if (results) setResults(results.filter((r) => r.id !== id));
  };

  const handleCompare = async () => {
    if (selectedIds.length < 2) return;
    setLoading(true);
    try {
      const data = await compareCareers(selectedIds);
      setResults(data.careers);
    } catch {
      alert('Error comparing careers. Make sure the backend is running.');
    }
    setLoading(false);
  };

  const radarData = results
    ? (() => {
        const metrics = [
          { key: 'risk', label: 'AI Risk' },
          { key: 'stability', label: 'Stability' },
          { key: 'salary', label: 'Salary' },
          { key: 'growth', label: 'Growth' },
        ];
        return metrics.map((m) => {
          const row: Record<string, string | number> = { metric: m.label };
          results.forEach((c) => {
            const ep = c.ensemble_prediction;
            let val = 0;
            if (m.key === 'risk') val = ep ? ep.automation_risk_score : 0;
            else if (m.key === 'stability') val = ep?.job_stability_score || 0;
            else if (m.key === 'salary') val = Math.min(((c.median_salary || 0) / 200000) * 100, 100);
            else if (m.key === 'growth') val = Math.max(0, Math.min(100, (c.growth_rate_pct || 0) + 50));
            row[c.title] = Math.round(val);
          });
          return row;
        });
      })()
    : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <GitCompareArrows className="w-8 h-8 text-indigo-400" />
        <h1 className="text-3xl font-bold text-white">{t.compare_title || 'Compare Careers'}</h1>
      </div>

      {/* Selection Slots */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[0, 1, 2, 3].map((slot) => {
          const careerId = selectedIds[slot];
          const career = results?.find((c) => c.id === careerId);
          return (
            <div key={slot} className="relative">
              {careerId ? (
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 h-24 flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[slot] }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">
                      {career?.title || `Career #${careerId}`}
                    </p>
                    {career?.ensemble_prediction && (
                      <RiskBadge level={career.ensemble_prediction.risk_level} size="sm" />
                    )}
                  </div>
                  <button
                    onClick={() => removeCareer(careerId)}
                    className="p-1 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setActiveSlot(slot)}
                  disabled={slot > selectedIds.length}
                  className="w-full h-24 border-2 border-dashed border-slate-700 rounded-xl flex flex-col items-center justify-center gap-1 text-slate-500 hover:border-indigo-500/50 hover:text-indigo-400 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <Plus className="w-5 h-5" />
                  <span className="text-xs">{t.compare_addCareer || 'Add Career'}</span>
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Search Dropdown */}
      {activeSlot !== null && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder={t.compare_searchPlaceholder || 'Search for a career to add...'}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
              autoFocus
            />
          </div>
          {searching && <p className="text-sm text-slate-400 mt-3">Searching...</p>}
          {searchResults.length > 0 && (
            <div className="mt-3 max-h-60 overflow-y-auto space-y-1">
              {searchResults.map((career) => (
                <button
                  key={career.id}
                  onClick={() => addCareer(career)}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-lg text-left hover:bg-slate-700 transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium text-white">{career.title}</p>
                    <p className="text-xs text-slate-400">{career.category} | {formatSalary(career.median_salary)}</p>
                  </div>
                  {career.ensemble_prediction && (
                    <RiskBadge level={career.ensemble_prediction.risk_level} size="sm" />
                  )}
                </button>
              ))}
            </div>
          )}
          <button
            onClick={() => setActiveSlot(null)}
            className="mt-3 text-sm text-slate-400 hover:text-white"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Compare Button */}
      {selectedIds.length >= 2 && !results && (
        <button
          onClick={handleCompare}
          disabled={loading}
          className="w-full sm:w-auto flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white font-medium px-8 py-3 rounded-xl mb-8"
        >
          <GitCompareArrows className="w-5 h-5" />
          {loading ? 'Comparing...' : t.compare_button || `Compare ${selectedIds.length} Careers`}
        </button>
      )}

      {loading && <LoadingSpinner />}

      {/* Results */}
      {results && results.length >= 2 && (
        <div className="space-y-6">
          {/* Radar Chart */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">{t.compare_overview || 'Overview Comparison'}</h2>
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#e2e8f0', fontSize: 13 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                {results.map((c, i) => (
                  <Radar
                    key={c.id}
                    name={c.title}
                    dataKey={c.title}
                    stroke={COLORS[i]}
                    fill={COLORS[i]}
                    fillOpacity={0.15}
                    strokeWidth={2}
                  />
                ))}
                <Legend wrapperStyle={{ color: '#e2e8f0', fontSize: 12 }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Side-by-side Cards */}
          <div className={`grid gap-6 ${results.length === 2 ? 'grid-cols-1 md:grid-cols-2' : results.length === 3 ? 'grid-cols-1 md:grid-cols-3' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'}`}>
            {results.map((career, i) => {
              const ep = career.ensemble_prediction;
              return (
                <div key={career.id} className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6" style={{ borderTopColor: COLORS[i], borderTopWidth: 3 }}>
                  <Link to={`/career/${career.id}`} className="no-underline">
                    <h3 className="text-lg font-semibold text-white mb-3 hover:text-indigo-400 transition-colors">{career.title}</h3>
                  </Link>

                  {ep && (
                    <div className="flex justify-center mb-4">
                      <RiskGauge score={ep.automation_risk_score} level={ep.risk_level} size={130} />
                    </div>
                  )}

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-slate-400">
                        <DollarSign className="w-4 h-4" />
                        <span className="text-sm">{t.detail_salary || 'Salary'}</span>
                      </div>
                      <span className="text-sm font-medium text-white">{formatSalary(career.median_salary)}</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-slate-400">
                        <TrendingUp className="w-4 h-4" />
                        <span className="text-sm">{t.detail_growth || 'Growth'}</span>
                      </div>
                      <span className={`text-sm font-medium ${career.growth_rate_pct && career.growth_rate_pct > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {career.growth_rate_pct ? `${career.growth_rate_pct > 0 ? '+' : ''}${career.growth_rate_pct}%` : 'N/A'}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-slate-400">
                        <Shield className="w-4 h-4" />
                        <span className="text-sm">Stability</span>
                      </div>
                      <span className="text-sm font-medium text-white">{ep?.job_stability_score?.toFixed(0) || 'N/A'}/100</span>
                    </div>

                    {ep?.disruption_year && (
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-slate-400">
                          <Calendar className="w-4 h-4" />
                          <span className="text-sm">Disruption</span>
                        </div>
                        <span className="text-sm font-medium text-amber-400">~{ep.disruption_year}</span>
                      </div>
                    )}

                    {ep?.salary_5yr_projection && (
                      <div className="pt-3 border-t border-slate-700/50">
                        <p className="text-xs text-slate-500 mb-1">5yr Salary Projection</p>
                        <p className="text-sm font-medium text-green-400">{formatSalary(ep.salary_5yr_projection)}</p>
                      </div>
                    )}
                  </div>

                  {/* Top Skills */}
                  {career.skills.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-700/50">
                      <p className="text-xs text-slate-500 mb-2">Top Skills</p>
                      <div className="flex flex-wrap gap-1">
                        {career.skills.slice(0, 5).map((s) => (
                          <span key={s.id} className="px-2 py-0.5 rounded bg-slate-700/50 text-xs text-slate-300">{s.skill_name}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* New Comparison */}
          <button
            onClick={() => { setResults(null); setSelectedIds([]); }}
            className="px-6 py-3 rounded-xl bg-slate-700 text-white hover:bg-slate-600"
          >
            {t.compare_newComparison || 'New Comparison'}
          </button>
        </div>
      )}

      {/* Empty State */}
      {!results && selectedIds.length === 0 && activeSlot === null && (
        <div className="text-center py-16">
          <GitCompareArrows className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">{t.compare_emptyTitle || 'Compare Careers Side by Side'}</h2>
          <p className="text-slate-400 max-w-md mx-auto">
            {t.compare_emptyDesc || 'Select 2-4 careers to compare their AI automation risk, salary projections, and key metrics.'}
          </p>
          <button
            onClick={() => setActiveSlot(0)}
            className="mt-6 inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-3 rounded-xl"
          >
            <Plus className="w-5 h-5" /> {t.compare_startComparing || 'Start Comparing'}
          </button>
        </div>
      )}
    </div>
  );
}
