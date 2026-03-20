import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Dna, Sparkles } from 'lucide-react';
import RiskBadge from '../components/common/RiskBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { fetchCareerDNA } from '../api/careers';
import { formatSalary } from '../utils/formatters';
import { useLanguage } from '../i18n/LanguageContext';
import type { CareerMatch } from '../types/career';

const SKILL_OPTIONS = [
  'Programming', 'Data Analysis', 'Writing', 'Public Speaking', 'Mathematics',
  'Design', 'Leadership', 'Research', 'Problem Solving', 'Communication',
  'Teaching', 'Sales', 'Marketing', 'Engineering', 'Science',
  'Healthcare', 'Counseling', 'Finance', 'Law', 'Art',
  'Music', 'Physical Fitness', 'Cooking', 'Mechanical Skills', 'Electronics',
];

const INTEREST_OPTIONS = [
  'Technology', 'Healthcare', 'Education', 'Business', 'Science',
  'Creative Arts', 'Social Services', 'Engineering', 'Law', 'Finance',
  'Sports', 'Environment', 'Agriculture', 'Manufacturing', 'Transportation',
];

export default function CareerDNAPage() {
  const { t } = useLanguage();
  const [step, setStep] = useState(1);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [education, setEducation] = useState('bachelors');
  const [maxRisk, setMaxRisk] = useState(60);
  const [results, setResults] = useState<CareerMatch[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [totalAnalyzed, setTotalAnalyzed] = useState(0);

  const toggleItem = (item: string, list: string[], setter: (v: string[]) => void) => {
    setter(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const data = await fetchCareerDNA({
        skills: selectedSkills,
        interests: selectedInterests,
        education,
        max_risk: maxRisk,
      });
      setResults(data.matches);
      setTotalAnalyzed(data.total_analyzed);
      setStep(4);
    } catch {
      alert('Error fetching results. Make sure the backend is running.');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <Dna className="w-8 h-8 text-purple-400" />
        <h1 className="text-3xl font-bold text-white">{t.dna_title}</h1>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= s ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-400'
              }`}
            >
              {s}
            </div>
            {s < 3 && <div className={`w-12 h-0.5 ${step > s ? 'bg-indigo-500' : 'bg-slate-700'}`} />}
          </div>
        ))}
        <span className="text-sm text-slate-400 ml-2">
          {step === 1 ? t.dna_skills : step === 2 ? t.dna_interests : step === 3 ? t.dna_preferences : t.dna_results}
        </span>
      </div>

      {/* Step 1: Skills */}
      {step === 1 && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-2">{t.dna_whatSkills}</h2>
          <p className="text-slate-400 mb-6">{t.dna_selectSkills}</p>
          <div className="flex flex-wrap gap-2 mb-8">
            {SKILL_OPTIONS.map((skill) => (
              <button
                key={skill}
                onClick={() => toggleItem(skill, selectedSkills, setSelectedSkills)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedSkills.includes(skill)
                    ? 'bg-indigo-600 text-white border-indigo-500'
                    : 'bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600'
                } border`}
              >
                {skill}
              </button>
            ))}
          </div>
          <button
            onClick={() => setStep(2)}
            disabled={selectedSkills.length === 0}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white font-medium px-6 py-3 rounded-xl"
          >
            {t.dna_next} <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Step 2: Interests */}
      {step === 2 && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-2">{t.dna_whatInterests}</h2>
          <p className="text-slate-400 mb-6">{t.dna_selectInterests}</p>
          <div className="flex flex-wrap gap-2 mb-8">
            {INTEREST_OPTIONS.map((interest) => (
              <button
                key={interest}
                onClick={() => toggleItem(interest, selectedInterests, setSelectedInterests)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedInterests.includes(interest)
                    ? 'bg-purple-600 text-white border-purple-500'
                    : 'bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600'
                } border`}
              >
                {interest}
              </button>
            ))}
          </div>
          <div className="flex gap-3">
            <button onClick={() => setStep(1)} className="px-6 py-3 rounded-xl bg-slate-700 text-white">{t.dna_back}</button>
            <button
              onClick={() => setStep(3)}
              disabled={selectedInterests.length === 0}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white font-medium px-6 py-3 rounded-xl"
            >
              {t.dna_next} <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Preferences */}
      {step === 3 && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-6">{t.dna_yourPreferences}</h2>

          <div className="space-y-6 mb-8">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">{t.dna_educationLevel}</label>
              <select
                value={education}
                onChange={(e) => setEducation(e.target.value)}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white"
              >
                <option value="high_school">{t.dna_highSchool}</option>
                <option value="bachelors">{t.dna_bachelors}</option>
                <option value="masters">{t.dna_masters}</option>
                <option value="doctorate">{t.dna_doctorate}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                {t.dna_maxRisk}: {maxRisk}%
              </label>
              <p className="text-xs text-slate-500 mb-3">{t.dna_riskExplain}</p>
              <input
                type="range"
                min={10}
                max={100}
                value={maxRisk}
                onChange={(e) => setMaxRisk(parseInt(e.target.value))}
                className="w-full accent-indigo-500"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-1">
                <span>{t.dna_verySafe}</span>
                <span>{t.dna_anyRisk}</span>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={() => setStep(2)} className="px-6 py-3 rounded-xl bg-slate-700 text-white">{t.dna_back}</button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium px-8 py-3 rounded-xl"
            >
              <Sparkles className="w-5 h-5" />
              {loading ? t.dna_analyzing : t.dna_findDna}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Results */}
      {step === 4 && results && (
        <div>
          <div className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-2xl p-6 mb-6">
            <p className="text-slate-300">
              {t.dna_analyzed} <span className="text-white font-semibold">{totalAnalyzed}</span> {t.dna_careers} {t.dna_matchingProfile} <span className="text-white font-semibold">{results.length}</span> {t.dna_matches}
            </p>
          </div>

          <div className="space-y-4">
            {results.map((match, i) => (
              <Link
                key={match.career_id}
                to={`/career/${match.career_id}`}
                className="block bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 hover:bg-slate-800 hover:border-indigo-500/30 transition-all no-underline"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl font-bold text-indigo-400">#{i + 1}</span>
                      <h3 className="text-lg font-semibold text-white">{match.title}</h3>
                      <RiskBadge level={match.risk_level} size="sm" />
                    </div>
                    <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                      <span>{match.category}</span>
                      <span>{formatSalary(match.median_salary)}</span>
                      {match.disruption_year && <span>{t.dna_disruption}: ~{match.disruption_year}</span>}
                    </div>
                    {match.matching_skills.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {match.matching_skills.map((s) => (
                          <span key={s} className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-xs">{s}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-3xl font-bold text-white">{match.match_score.toFixed(0)}%</div>
                    <div className="text-xs text-slate-500">{t.dna_match}</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          <button
            onClick={() => { setStep(1); setResults(null); }}
            className="mt-6 px-6 py-3 rounded-xl bg-slate-700 text-white hover:bg-slate-600"
          >
            {t.dna_startOver}
          </button>
        </div>
      )}

      {loading && <LoadingSpinner text={t.dna_analyzingDna} />}
    </div>
  );
}
