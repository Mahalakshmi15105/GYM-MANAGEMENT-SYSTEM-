import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Footer from '../components/Footer';
import api from '../services/api';
import { 
  HeartIcon, 
  LockClosedIcon, 
  KeyIcon, 
  BoltIcon 
} from '@heroicons/react/24/outline';

export default function LandingPage() {
  const { isAuthenticated, logout } = useAuth();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const response = await api.get('/api/admin/subscription-plans/active');
        setPlans(response.data.plans);
      } catch (err) {
        console.error('Failed to fetch plans:', err);
        setError('Failed to load plans');
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  return (
    <div className="bg-white text-gray-800 min-h-screen flex flex-col w-full overflow-x-hidden">
      {/* Header - Stretches up to 1800px for high-res screens */}
      <header className="w-full border-b border-gray-200 bg-white/95 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 h-16 sm:h-20 flex items-center justify-between w-full">
          {/* Logo brand */}
          <div className="flex items-center gap-2">
            <HeartIcon className="w-8 h-8 sm:w-10 sm:h-10 text-orange-600" />
            <span className="text-xl sm:text-2xl font-bold text-orange-500">
              FlexiGym
            </span>
          </div>
          {/* Navigation links */}
          <nav className="flex items-center gap-4 sm:gap-6">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="text-sm sm:text-base font-medium text-gray-600 hover:text-orange-500 transition-colors">
                  Dashboard
                </Link>
                <button
                  onClick={logout}
                  className="text-xs sm:text-sm lg:text-base font-semibold bg-red-500 hover:bg-red-600 text-white px-3.5 py-2 sm:px-5 sm:py-2.5 rounded-xl transition-all duration-200 shadow-md"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm sm:text-base font-medium text-gray-600 hover:text-orange-500 transition-colors">
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="text-xs sm:text-sm lg:text-base font-semibold bg-orange-500 hover:bg-orange-600 text-white px-3.5 py-2 sm:px-5 sm:py-2.5 rounded-xl transition-all duration-200 shadow-md"
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
        <section className="relative overflow-hidden py-16 sm:py-24 md:py-32 xl:py-48 w-full flex items-center justify-center bg-gradient-to-br from-orange-50 to-white">
          {/* Glowing background highlights scaled for high-res screens */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] sm:w-[600px] lg:w-[800px] xl:w-[1000px] h-[350px] sm:h-[600px] lg:h-[800px] xl:h-[1000px] bg-orange-200/30 rounded-full blur-[100px] sm:blur-[140px] pointer-events-none"></div>
          <div className="absolute top-1/3 left-1/3 w-[200px] sm:w-[400px] lg:w-[600px] xl:w-[800px] h-[200px] sm:h-[400px] lg:h-[600px] xl:h-[800px] bg-orange-100/40 rounded-full blur-[80px] sm:blur-[120px] pointer-events-none"></div>

          <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 relative z-10 flex flex-col items-center text-center w-full">
            <span className="text-xs sm:text-sm uppercase font-extrabold tracking-widest bg-orange-100 text-orange-600 px-4 py-2 rounded-full border border-orange-200 inline-block mb-6 sm:mb-8">
              Multi-Tenant Gym SaaS
            </span>
            <h1 className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl 2xl:text-9xl font-black tracking-tight text-gray-900 mb-6 sm:mb-8 leading-tight max-w-6xl">
              Scale Your Gym Operations with{' '}
              <span className="text-orange-500">
                FlexiGym
              </span>
            </h1>
            <p className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl 2xl:text-3xl text-gray-600 mb-10 sm:mb-12 max-w-2xl lg:max-w-4xl 2xl:max-w-6xl leading-relaxed">
              The ultimate multi-tenant platform for gym owners to manage members, payments, trainers, schedules, and attendance under one dashboard with complete data isolation.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center w-full sm:w-auto px-4 sm:px-0">
              <Link
                to="/register"
                className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-6 py-3.5 sm:px-8 sm:py-4 xl:px-10 xl:py-5 rounded-xl transition-all duration-200 shadow-lg shadow-orange-500/25 transform hover:-translate-y-0.5 text-center text-sm sm:text-base xl:text-lg"
              >
                Start Gym Owner Registration
              </Link>
              <Link
                to="/login"
                className="bg-white hover:bg-gray-50 border-2 border-gray-200 text-gray-800 font-bold px-6 py-3.5 sm:px-8 sm:py-4 xl:px-10 xl:py-5 rounded-xl transition-all duration-200 transform hover:-translate-y-0.5 text-center text-sm sm:text-base xl:text-lg shadow-lg"
              >
                Log In to Workspace
              </Link>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 sm:py-28 xl:py-36 border-t border-gray-200 bg-gray-50 w-full">
          <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 w-full">
            <div className="text-center mb-16 sm:mb-24">
              <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-gray-900">
                Engineered for Fitness Businesses
              </h2>
              <p className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-gray-600 max-w-xl lg:max-w-2xl mx-auto">
                Everything you need to handle memberships, process billing, and record athlete check-ins.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 lg:gap-12 xl:gap-16 w-full">
              {/* Card 1 */}
              <div className="bg-white border border-gray-200 p-6 sm:p-8 xl:p-12 rounded-2xl hover:border-orange-300 hover:shadow-lg transition-all duration-300 w-full flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-orange-100 border border-orange-200 rounded-xl flex items-center justify-center mb-6 text-orange-500">
                    <LockClosedIcon className="w-6 h-6 sm:w-7 sm:h-7" />
                  </div>
                  <h3 className="text-lg sm:text-xl xl:text-2xl font-bold mb-2 text-gray-900">Isolated Multi-Tenant Security</h3>
                  <p className="text-xs sm:text-sm xl:text-base text-gray-600 leading-relaxed">
                    Strict database division ensures your gym statistics, revenue numbers, and customer profiles remain strictly invisible to other tenants.
                  </p>
                </div>
              </div>
              {/* Card 2 */}
              <div className="bg-white border border-gray-200 p-6 sm:p-8 xl:p-12 rounded-2xl hover:border-orange-300 hover:shadow-lg transition-all duration-300 w-full flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-orange-100 border border-orange-200 rounded-xl flex items-center justify-center mb-6 text-orange-500">
                    <KeyIcon className="w-6 h-6 sm:w-7 sm:h-7" />
                  </div>
                  <h3 className="text-lg sm:text-xl xl:text-2xl font-bold mb-2 text-gray-900">JWT Authentication & RBAC</h3>
                  <p className="text-xs sm:text-sm xl:text-base text-gray-600 leading-relaxed">
                    Secure login flow with JSON Web Tokens and granular permissions tailored to Super Admins, Gym Owners, and member-level accounts.
                  </p>
                </div>
              </div>
              {/* Card 3 */}
              <div className="bg-white border border-gray-200 p-6 sm:p-8 xl:p-12 rounded-2xl hover:border-orange-300 hover:shadow-lg transition-all duration-300 w-full flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-orange-100 border border-orange-200 rounded-xl flex items-center justify-center mb-6 text-orange-500">
                    <BoltIcon className="w-6 h-6 sm:w-7 sm:h-7" />
                  </div>
                  <h3 className="text-lg sm:text-xl xl:text-2xl font-bold mb-2 text-gray-900">Real-Time Core Performance</h3>
                  <p className="text-xs sm:text-sm xl:text-base text-gray-600 leading-relaxed">
                    Vite-powered Single Page Application paired with a Python Flask REST backend for instant screen transitions and real-time dashboard analytics.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Subscription Plans Section */}
        <section className="py-20 sm:py-28 xl:py-36 border-t border-gray-200 bg-white w-full">
          <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-12 xl:px-16 w-full">
            <div className="text-center mb-16 sm:mb-24">
              <h2 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-gray-900">
                Choose Your Perfect Plan
              </h2>
              <p className="text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-gray-600 max-w-xl lg:max-w-2xl mx-auto">
                Flexible pricing designed to grow with your fitness business, from single locations to enterprise chains.
              </p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8 lg:gap-12 xl:gap-16 w-full">
              {loading ? (
                // Loading skeletons
                [...Array(3)].map((_, i) => (
                  <div key={i} className="bg-gray-100 border-2 border-gray-200 p-6 sm:p-8 xl:p-12 rounded-2xl w-full flex flex-col animate-pulse">
                    <div className="text-center mb-8">
                      <div className="h-8 bg-gray-200 rounded mb-4 w-3/4 mx-auto"></div>
                      <div className="h-12 bg-gray-200 rounded mb-4 w-1/2 mx-auto"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
                    </div>
                    <div className="space-y-3 mb-8 flex-1">
                      {[...Array(4)].map((_, j) => (
                        <div key={j} className="h-4 bg-gray-200 rounded"></div>
                      ))}
                    </div>
                    <div className="h-12 bg-gray-200 rounded"></div>
                  </div>
                ))
              ) : error ? (
                <div className="col-span-1 lg:col-span-3 text-center py-12">
                  <p className="text-gray-600">{error}</p>
                </div>
              ) : plans.length === 0 ? (
                <div className="col-span-1 lg:col-span-3 text-center py-12">
                  <p className="text-gray-600">No plans available</p>
                </div>
              ) : (
                plans.map((plan) => (
                  <div 
                    key={plan.id} 
                    className={`bg-white border-2 p-6 sm:p-8 xl:p-12 rounded-2xl hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 w-full flex flex-col ${plan.recommended ? 'border-orange-500 relative overflow-hidden' : 'border-gray-200 hover:border-orange-300'}`}
                  >
                    {plan.recommended && (
                      <div className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs font-bold px-4 py-1 rounded-bl-xl">
                        RECOMMENDED
                      </div>
                    )}
                    
                    <div className="text-center mb-8">
                      <h3 className="text-xl sm:text-2xl xl:text-3xl font-bold mb-2 text-gray-900">
                        {plan.plan_name}
                      </h3>
                      <div className="mb-4">
                        <span className="text-3xl sm:text-4xl xl:text-5xl font-bold text-orange-500">
                          ₹{plan.price}
                        </span>
                        <span className="text-gray-600 text-sm sm:text-base xl:text-lg">
                          /{plan.billing_cycle}
                        </span>
                      </div>
                      <p className="text-xs sm:text-sm xl:text-base text-gray-600">
                        {plan.description}
                      </p>
                    </div>
                    
                    {plan.features && Array.isArray(plan.features) && plan.features.length > 0 ? (
                      <ul className="space-y-3 mb-8 flex-1">
                        {plan.features.map((feature, idx) => (
                          <li key={idx} className="flex items-center text-xs sm:text-sm xl:text-base text-gray-700">
                            <span className="w-5 h-5 rounded-full bg-orange-100 flex items-center justify-center mr-3 flex-shrink-0">
                              <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                            </span>
                            {feature}
                          </li>
                        ))}
                      </ul>
                    ) : null}
                    
                    <button className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold px-6 py-3.5 sm:px-8 sm:py-4 xl:px-10 xl:py-5 rounded-xl transition-all duration-200 shadow-lg shadow-orange-500/25 transform hover:-translate-y-0.5 text-sm sm:text-base xl:text-lg">
                      Choose Plan
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
