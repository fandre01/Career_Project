import { useState, useEffect } from 'react';
import { MessageCircle, Send, Clock } from 'lucide-react';
import { fetchComments, postComment } from '../../api/engagement';
import { useLanguage } from '../../i18n/LanguageContext';
import type { Comment } from '../../types/engagement';

function timeAgo(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

export default function CommentsSection() {
  const { t } = useLanguage();
  const [comments, setComments] = useState<Comment[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const loadComments = (p: number, append = false) => {
    fetchComments(p, 10).then((data) => {
      setComments((prev) => append ? [...prev, ...data.items] : data.items);
      setTotal(data.total);
      setPage(p);
    }).catch(() => {});
  };

  useEffect(() => {
    loadComments(1);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !message.trim()) return;
    setSubmitting(true);
    setError('');
    try {
      await postComment(name.trim(), message.trim());
      setName('');
      setMessage('');
      loadComments(1);
    } catch (err) {
      if (err instanceof Error && err.message === 'RATE_LIMITED') {
        setError(t.comments_rateLimited);
      } else {
        setError('Something went wrong. Please try again.');
      }
    }
    setSubmitting(false);
  };

  const hasMore = comments.length < total;

  return (
    <section id="comments" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="flex items-center gap-3 mb-8">
        <MessageCircle className="w-8 h-8 text-indigo-400" />
        <h2 className="text-2xl font-bold text-white">{t.comments_title}</h2>
      </div>

      {/* Comment Form */}
      <form onSubmit={handleSubmit} className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6 mb-8">
        <p className="text-slate-400 text-sm mb-4">{t.comments_subtitle}</p>
        <div className="flex flex-col sm:flex-row gap-3 mb-3">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t.comments_name}
            maxLength={100}
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 text-sm"
          />
        </div>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={t.comments_message}
          maxLength={1000}
          rows={3}
          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 text-sm resize-none mb-2"
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-500">
            {1000 - message.length} {t.comments_charLimit}
          </span>
          <button
            type="submit"
            disabled={submitting || !name.trim() || !message.trim()}
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white font-medium px-6 py-2.5 rounded-xl text-sm"
          >
            <Send className="w-4 h-4" />
            {submitting ? t.comments_submitting : t.comments_submit}
          </button>
        </div>
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
      </form>

      {/* Comments List */}
      {comments.length === 0 ? (
        <p className="text-center text-slate-500 py-8">{t.comments_empty}</p>
      ) : (
        <div className="space-y-4">
          {comments.map((c) => (
            <div key={c.id} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-white text-sm">{c.name}</span>
                <span className="flex items-center gap-1 text-xs text-slate-500">
                  <Clock className="w-3 h-3" />
                  {timeAgo(c.created_at)}
                </span>
              </div>
              <p className="text-slate-300 text-sm whitespace-pre-wrap">{c.message}</p>
            </div>
          ))}

          {hasMore && (
            <button
              onClick={() => loadComments(page + 1, true)}
              className="w-full py-3 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 text-sm"
            >
              {t.comments_loadMore}
            </button>
          )}
        </div>
      )}
    </section>
  );
}
