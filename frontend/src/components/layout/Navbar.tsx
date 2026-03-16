import { Link, useLocation } from 'react-router-dom';
import { Shield, Search, Globe, ChevronDown, Menu, X } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../i18n/LanguageContext';
import { LANGUAGES } from '../../i18n/translations';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { lang, setLang, t } = useLanguage();
  const [search, setSearch] = useState('');
  const [langOpen, setLangOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const langRef = useRef<HTMLDivElement>(null);

  const currentLang = LANGUAGES.find((l) => l.code === lang)!;

  const links = [
    { to: '/', label: t.nav_home },
    { to: '/dashboard', label: t.nav_dashboard },
    { to: '/career-dna', label: t.nav_careerDna },
    { to: '/compare', label: 'Compare' },
    { to: '/chat', label: t.nav_fabriceAi },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) {
      navigate(`/dashboard?search=${encodeURIComponent(search.trim())}`);
      setSearch('');
      setMobileOpen(false);
    }
  };

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (langRef.current && !langRef.current.contains(e.target as Node)) {
        setLangOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  return (
    <nav className="bg-slate-900/80 backdrop-blur-md border-b border-slate-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 no-underline">
            <Shield className="w-8 h-8 text-indigo-500" />
            <span className="text-xl font-bold text-white">
              Career<span className="text-indigo-400">Shield</span> AI
            </span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-6">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`text-sm font-medium transition-colors no-underline ${
                  location.pathname === link.to
                    ? 'text-indigo-400'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            {/* Language Selector */}
            <div className="relative" ref={langRef}>
              <button
                onClick={() => setLangOpen(!langOpen)}
                className="flex items-center gap-1.5 bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white hover:bg-slate-700 transition-colors"
              >
                <Globe className="w-4 h-4 text-indigo-400" />
                <span className="hidden sm:inline">{currentLang.flag}</span>
                <span className="hidden lg:inline text-xs">{currentLang.name}</span>
                <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform ${langOpen ? 'rotate-180' : ''}`} />
              </button>

              {langOpen && (
                <div className="absolute right-0 top-full mt-2 bg-slate-800 border border-slate-600 rounded-xl shadow-xl overflow-hidden z-50 min-w-[180px] max-h-[400px] overflow-y-auto">
                  {LANGUAGES.map((l) => (
                    <button
                      key={l.code}
                      onClick={() => {
                        setLang(l.code);
                        setLangOpen(false);
                      }}
                      className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                        lang === l.code
                          ? 'bg-indigo-600/20 text-indigo-300'
                          : 'text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      <span className="text-lg">{l.flag}</span>
                      <span>{l.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Search (desktop) */}
            <form onSubmit={handleSearch} className="hidden sm:flex items-center">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={t.nav_searchPlaceholder}
                  className="bg-slate-800 border border-slate-600 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 w-48 focus:w-64 transition-all"
                />
              </div>
            </form>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
            >
              {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-slate-700/50 bg-slate-900/95 backdrop-blur-md">
          <div className="px-4 py-4 space-y-2">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`block px-4 py-3 rounded-lg text-sm font-medium no-underline transition-colors ${
                  location.pathname === link.to
                    ? 'bg-indigo-600/20 text-indigo-400'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
            {/* Mobile search */}
            <form onSubmit={handleSearch} className="pt-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={t.nav_searchPlaceholder}
                  className="w-full bg-slate-800 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </form>
          </div>
        </div>
      )}
    </nav>
  );
}
