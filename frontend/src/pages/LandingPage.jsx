import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="bg-slate-950 text-slate-100 min-h-screen flex flex-col w-full overflow-x-hidden">
      {/* Header - Stretches up to 1800px for high-res screens */}
      <header className="w-full border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 h-16 sm:h-20 flex items-center justify-between w-full">
          {/* Logo brand */}
          <div className="flex items-center gap-2">
            <span className="text-2xl sm:text-3xl">🏋️‍♂️</span>
            <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              FlexiGym
            </span>
          </div>
          {/* Navigation links */}
          <nav className="flex items-center gap-4 sm:gap-6">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="text-sm sm:text-base font-medium text-slate-300 hover:text-white transition-colors">
                  Dashboard
                </Link>
                <button
                  onClick={logout}
                  className="text-xs sm:text-sm lg:text-base font-semibold bg-red-500 hover:bg-red-600 text-white px-3.5 py-2 sm:px-5 sm:py-2.5 rounded-xl transition-all duration-200 shadow-md shadow-red-500/10"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm sm:text-base font-medium text-slate-300 hover:text-white transition-colors">
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="text-xs sm:text-sm lg:text-base font-semibold bg-emerald-500 hover:bg-emerald-600 text-slate-950 px-3.5 py-2 sm:px-5 sm:py-2.5 rounded-xl transition-all duration-200 shadow-md shadow-emerald-500/10"
                >
                  Register Gym
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Hero & Features Main Content */}
      <main className="flex-1 w-full">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-16 sm:py-24 md:py-32 xl:py-48 w-full flex items-center justify-center">
          {/* Glowing background highlights scaled for high-res screens */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] sm:w-[600px] lg:w-[800px] xl:w-[1000px] h-[350px] sm:h-[600px] lg:h-[800px] xl:h-[1000px] bg-emerald-500/10 rounded-full blur-[100px] sm:blur-[140px] pointer-events-none"></div>
          <div className="absolute top-1/3 left-1/3 w-[200px] sm:w-[400px] lg:w-[600px] xl:w-[800px] h-[200px] sm:h-[400px] lg:h-[600px] xl:h-[800px] bg-teal-500/10 rounded-full blur-[80px] sm:blur-[120px] pointer-events-none"></div>

          <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 relative z-10 flex flex-col items-center text-center w-full">
            <span className="text-xs sm:text-sm uppercase font-extrabold tracking-widest bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-full border border-emerald-500/20 inline-block mb-6 sm:mb-8">
              Multi-Tenant Gym SaaS
            </span>
            <h1 className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl 2xl:text-9xl font-black tracking-tight text-white mb-6 sm:mb-8 leading-tight max-w-6xl">
              Scale Your Gym Operations with{' '}
              <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
                FlexiGym
              </span>
            </h1>
            <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl 2xl:text-3xl text-slate-400 mb-10 sm:mb-12 max-w-2xl lg:max-w-4xl 2xl:max-w-6xl leading-relaxed">
              The ultimate multi-tenant platform for gym owners to manage members, payments, trainers, schedules, and attendance under one dashboard with complete data isolation.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center w-full sm:w-auto px-4 sm:px-0">
              <Link
                to="/register"
                className="bg-gradient-to-r from-emerald-400 to-teal-500 hover:from-emerald-500 hover:to-teal-600 text-slate-950 font-bold px-6 py-3.5 sm:px-8 sm:py-4 xl:px-10 xl:py-5 rounded-xl transition-all duration-200 shadow-lg shadow-emerald-500/20 transform hover:-translate-y-0.5 text-center text-sm sm:text-base xl:text-lg"
              >
                Start Gym Owner Registration
              </Link>
              <Link
                to="/login"
                className="bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 font-bold px-6 py-3.5 sm:px-8 sm:py-4 xl:px-10 xl:py-5 rounded-xl transition-all duration-200 transform hover:-translate-y-0.5 text-center text-sm sm:text-base xl:text-lg"
              >
                Log In to Workspace
              </Link>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 sm:py-28 xl:py-36 border-t border-slate-900 bg-slate-900/20 w-full">
          <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 w-full">
            <div className="text-center mb-16 sm:mb-24">
              <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
                Engineered for Fitness Businesses
              </h2>
              <p className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-slate-400 max-w-xl lg:max-w-2xl mx-auto">
                Everything you need to handle memberships, process billing, and record athlete check-ins.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 lg:gap-12 xl:gap-16 w-full">
              {/* Card 1 */}
              <div className="bg-slate-900/50 border border-slate-855 p-6 sm:p-8 xl:p-12 rounded-2xl hover:border-emerald-500/20 transition-all duration-300 w-full flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center text-xl sm:text-2xl mb-6 text-emerald-400">
                    🔒
                  </div>
                  <h3 className="text-lg sm:text-xl xl:text-2xl font-bold mb-2 text-white">Isolated Multi-Tenant Security</h3>
                  <p className="text-xs sm:text-sm xl:text-base text-slate-400 leading-relaxed">
                    Strict database division ensures your gym statistics, revenue numbers, and customer profiles remain strictly invisible to other tenants.
                  </p>
                </div>
              </div>
              {/* Card 2 */}
              <div className="bg-slate-900/50 border border-slate-855 p-6 sm:p-8 xl:p-12 rounded-2xl hover:border-emerald-500/20 transition-all duration-300 w-full flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center text-xl sm:text-2xl mb-6 text-emerald-400">
                    🔑
                  </div>
                  <h3 className="text-lg sm:text-xl xl:text-2xl font-bold mb-2 text-white">JWT Authentication & RBAC</h3>
                  <p className="text-xs sm:text-sm xl:text-base text-slate-400 leading-relaxed">
                    Secure login flow with JSON Web Tokens and granular permissions tailored to Super Admins, Gym Owners, and member-level accounts.
                  </p>
                </div>
              </div>
              {/* Card 3 */}
              <div className="bg-slate-900/50 border border-slate-855 p-6 sm:p-8 xl:p-12 rounded-2xl hover:border-emerald-500/20 transition-all duration-300 w-full flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-center text-xl sm:text-2xl mb-6 text-emerald-400">
                    ⚡
                  </div>
                  <h3 className="text-lg sm:text-xl xl:text-2xl font-bold mb-2 text-white">Real-Time Core Performance</h3>
                  <p className="text-xs sm:text-sm xl:text-base text-slate-400 leading-relaxed">
                    Vite-powered Single Page Application paired with a Python Flask REST backend for instant screen transitions and real-time dashboard analytics.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-12 bg-slate-950 text-slate-500 text-sm text-center w-full">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 flex flex-col md:flex-row items-center justify-between gap-4 w-full">
          <div className="flex items-center gap-2">
            <span>🏋️‍♂️</span>
            <span className="font-semibold text-slate-400 text-sm sm:text-base">FlexiGym SaaS</span>
          </div>
          <p className="text-xs sm:text-sm">© {new Date().getFullYear()} FlexiGym. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
