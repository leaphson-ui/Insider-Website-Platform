import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import DemoVisualization from '../components/DemoVisualization';
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  UsersIcon,
  ClockIcon,
  ShareIcon,
  EyeIcon,
  ArrowRightIcon,
  PlayIcon,
  SparklesIcon,
  TrophyIcon,
  BoltIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

const Homepage = () => {
  const { isDarkMode } = useTheme();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const features = [
    {
      icon: ChartBarIcon,
      title: "Real-Time Analytics",
      description: "Track insider trades as they happen with advanced performance metrics and conviction scoring.",
      gradient: "from-blue-500 to-purple-600",
      link: "/dashboard"
    },
    {
      icon: TrophyIcon,
      title: "Performance Leaderboard",
      description: "Discover top-performing insiders ranked by returns, win rates, and trading consistency.",
      gradient: "from-green-500 to-emerald-600",
      link: "/leaderboard"
    },
    {
      icon: CurrencyDollarIcon,
      title: "Portfolio Tracking",
      description: "Monitor insider holdings and portfolio values with real-time position tracking.",
      gradient: "from-yellow-500 to-orange-600",
      link: "/portfolio"
    },
    {
      icon: ShareIcon,
      title: "Network Intelligence",
      description: "Uncover insider connections and coordinated trading patterns across companies.",
      gradient: "from-purple-500 to-pink-600",
      link: "/networks"
    },
    {
      icon: ClockIcon,
      title: "Timing Analysis",
      description: "Analyze trading patterns, market timing, and behavioral insights of top insiders.",
      gradient: "from-indigo-500 to-blue-600",
      link: "/timing"
    },
    {
      icon: BoltIcon,
      title: "Live Trade Feed",
      description: "Access the latest insider transactions with comprehensive filtering and analysis tools.",
      gradient: "from-red-500 to-rose-600",
      link: "/trades"
    }
  ];

  const stats = [
    { label: "Active Insiders", value: "10K+", icon: UsersIcon },
    { label: "Tracked Trades", value: "419K+", icon: ChartBarIcon },
    { label: "Companies", value: "5K+", icon: GlobeAltIcon },
    { label: "Success Rate", value: "94%", icon: SparklesIcon }
  ];

  return (
    <div className="min-h-screen bg-primary">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-pink-600/20" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <div className={`text-center transform transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            <h1 className="text-6xl md:text-8xl font-bold text-primary mb-6 leading-tight">
              Insider
              <span className="block hero-gradient">
                Intelligence
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-secondary max-w-3xl mx-auto mb-8 leading-relaxed">
              The most advanced platform for tracking, analyzing, and profiting from corporate insider trading patterns.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Link
                to="/dashboard"
                className="group inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-full hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                <span>Start Analyzing</span>
                <ArrowRightIcon className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button className="group inline-flex items-center px-8 py-4 border-2 border-default text-primary font-semibold rounded-full hover:bg-secondary transition-all duration-300">
                <PlayIcon className="mr-2 h-5 w-5" />
                <span>Watch Demo</span>
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              {stats.map((stat, index) => (
                <div key={stat.label} className={`transform transition-all duration-700 delay-${index * 100} ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
                  <div className="text-center">
                    <stat.icon className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                    <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
                    <div className="text-sm text-secondary">{stat.label}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-full blur-xl float-animation" />
        <div className="absolute bottom-20 right-10 w-32 h-32 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-full blur-xl float-animation" style={{animationDelay: '2s'}} />
        <div className="absolute top-40 right-20 w-16 h-16 bg-gradient-to-r from-green-500/30 to-blue-500/30 rounded-full blur-xl float-animation" style={{animationDelay: '1s'}} />
      </section>

      {/* Features Section */}
      <section className="py-24 bg-secondary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-primary mb-4">
              Everything you need to
              <span className="block text-blue-500">dominate the market</span>
            </h2>
            <p className="text-xl text-secondary max-w-3xl mx-auto">
              Comprehensive insider trading intelligence with institutional-grade analytics and real-time insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Link
                key={feature.title}
                to={feature.link}
                className={`group block transform transition-all duration-500 delay-${index * 100} hover:scale-105 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}
              >
                <div className="relative h-full p-8 bg-primary rounded-3xl border border-default hover:border-blue-500/50 transition-all duration-300 overflow-hidden">
                  {/* Gradient Background */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                  
                  {/* Icon */}
                  <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${feature.gradient} mb-6`}>
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-bold text-primary mb-3 group-hover:text-blue-500 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-secondary leading-relaxed mb-4">
                    {feature.description}
                  </p>

                  {/* Arrow */}
                  <div className="flex items-center text-blue-500 font-semibold">
                    <span className="mr-2">Explore</span>
                    <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-24 bg-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold text-primary mb-6">
                Built with
                <span className="block text-purple-500">cutting-edge technology</span>
              </h2>
              <p className="text-xl text-secondary mb-8 leading-relaxed">
                Our platform processes millions of SEC filings in real-time, delivering institutional-grade analytics with consumer-friendly interfaces.
              </p>
              
              <div className="space-y-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mr-4">
                    <BoltIcon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-primary">Real-time Processing</h3>
                    <p className="text-secondary">SEC Form 4 filings processed within minutes of submission</p>
                  </div>
                </div>
                
                <div className="flex items-center">
                  <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mr-4">
                    <SparklesIcon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-primary">AI-Powered Insights</h3>
                    <p className="text-secondary">Machine learning algorithms identify patterns and anomalies</p>
                  </div>
                </div>
                
                <div className="flex items-center">
                  <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center mr-4">
                    <EyeIcon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-primary">Comprehensive Coverage</h3>
                    <p className="text-secondary">Track 10,000+ insiders across 5,000+ public companies</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Visualization */}
            <div className="relative">
              <DemoVisualization />
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 gradient-shift">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to unlock insider intelligence?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of investors already using our platform to make smarter trading decisions.
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-bold rounded-full hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl pulse-glow"
          >
            <span>Get Started Now</span>
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Homepage;
