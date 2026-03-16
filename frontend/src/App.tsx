import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LanguageProvider } from './i18n/LanguageContext';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import CareerDetailPage from './pages/CareerDetailPage';
import ChatPage from './pages/ChatPage';
import CareerDNAPage from './pages/CareerDNAPage';
import ComparePage from './pages/ComparePage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <LanguageProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <div className="min-h-screen flex flex-col bg-slate-950">
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/career/:id" element={<CareerDetailPage />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/career-dna" element={<CareerDNAPage />} />
                <Route path="/compare" element={<ComparePage />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </QueryClientProvider>
    </LanguageProvider>
  );
}
