import { Shield } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';

export default function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="bg-slate-900 border-t border-slate-800 py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-indigo-500" />
            <span className="text-sm text-slate-400">
              {t.footer_tagline}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <img
              src="/fabrice.jpg"
              alt="Fabrice Andre"
              className="w-8 h-8 rounded-full object-cover border-2 border-indigo-500/50"
            />
            <span className="text-sm text-slate-400 font-medium">
              {t.footer_owner}
            </span>
          </div>
          <div className="text-sm text-slate-500">
            {t.footer_data}
          </div>
        </div>
      </div>
    </footer>
  );
}
