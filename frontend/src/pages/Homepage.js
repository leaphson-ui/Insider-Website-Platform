import React from 'react'; 
import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';
import Layout from '../components/Layout';

const Homepage = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="hero-section py-24">
        <div className="container text-center">
          <h1 className="hero-title">
            <span className="gradient-text">A modern insider trading intelligence platform</span>
          </h1>
          <p className="hero-subtitle">
            Uncover unusual insider activity and follow the smart money in real time.
          </p>
          <div className="hero-ctas mb-16">
            <Link to="/dashboard">
              <Button className="btn-primary btn-lg">
                Start free 7 day trial
              </Button>
            </Link>
          </div>
        </div>
        
        {/* Product Imagery - Platform Interface Screenshot */}
        <div className="product-showcase mt-32">
          <div className="browser-frame">
            <div className="browser-header">
              <div className="browser-controls">
                <span className="control-dot bg-red-500"></span>
                <span className="control-dot bg-yellow-500"></span>
                <span className="control-dot bg-green-500"></span>
              </div>
              <div className="browser-url">app.insideralpha.com</div>
            </div>
            <div className="platform-interface">
              {/* Mock platform interface showing insider trading data */}
              <div className="interface-sidebar">
                <div className="sidebar-icon">📊</div>
                <div className="sidebar-icon">📈</div>
                <div className="sidebar-icon">👥</div>
                <div className="sidebar-icon">⚙️</div>
              </div>
              
              <div className="interface-main">
                <div className="data-panels">
                  <div className="panel">
                    <h3>Insider Sentiment</h3>
                    <div className="sentiment-value bullish">Bullish</div>
                    <div className="sentiment-bar">
                      <div className="bar-fill bullish" style={{width: '75%'}}></div>
                    </div>
                  </div>
                  
                  <div className="panel">
                    <h3>Trade Volume</h3>
                    <div className="volume-value">$2.4M</div>
                    <div className="volume-change positive">+12.4%</div>
                  </div>
                </div>
                
                <div className="trades-table">
                  <div className="table-header">
                    <div className="header-cell">TIME</div>
                    <div className="header-cell">INSIDER</div>
                    <div className="header-cell">COMPANY</div>
                    <div className="header-cell">SHARES</div>
                    <div className="header-cell">VALUE</div>
                    <div className="header-cell">TYPE</div>
                  </div>
                  <div className="table-row">
                    <div className="cell">09:33:16</div>
                    <div className="cell">J. Smith</div>
                    <div className="cell">AAPL</div>
                    <div className="cell">50,000</div>
                    <div className="cell positive">$8.2M</div>
                    <div className="cell">BUY</div>
                  </div>
                  <div className="table-row">
                    <div className="cell">09:28:44</div>
                    <div className="cell">M. Johnson</div>
                    <div className="cell">TSLA</div>
                    <div className="cell">25,000</div>
                    <div className="cell positive">$4.1M</div>
                    <div className="cell">BUY</div>
                  </div>
                  <div className="table-row">
                    <div className="cell">09:15:22</div>
                    <div className="cell">S. Davis</div>
                    <div className="cell">NVDA</div>
                    <div className="cell">15,000</div>
                    <div className="cell negative">$2.8M</div>
                    <div className="cell">SELL</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Features Section - CheddarFlow Style */}
      <section className="py-32 bg-primary mb-16">
        <div className="container">
          <div className="grid grid-cols-4 gap-8">
          <div className="cheddarflow-feature-card">
            <div className="feature-content">
              <div className="feature-text">
                <h3 className="cheddarflow-feature-title">Track executive activity</h3>
                <p className="cheddarflow-feature-description">Gain insights into the latest moves corporate executives and board members are making.</p>
              </div>
            </div>
          </div>
            <div className="cheddarflow-feature-card">
              <div className="feature-content">
                <div className="feature-text">
                  <h3 className="cheddarflow-feature-title">Fast, reliable SEC data</h3>
                  <p className="cheddarflow-feature-description">Get the latest Form 4 filings delivered to you quickly and accurately.</p>
                </div>
              </div>
            </div>
            <div className="cheddarflow-feature-card">
              <div className="feature-content">
                <div className="feature-text">
                  <h3 className="cheddarflow-feature-title">Superior user experience</h3>
                  <p className="cheddarflow-feature-description">Enjoy an intuitive interface that makes it easy to find the information you need.</p>
                </div>
              </div>
            </div>
            <div className="cheddarflow-feature-card">
              <div className="feature-content">
                <div className="feature-text">
                  <h3 className="cheddarflow-feature-title">Built to empower the retail investor</h3>
                  <p className="cheddarflow-feature-description">Our platform is designed to give individual investors the edge they need.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Feature Module - CheddarFlow Style */}
      <section className="py-24 bg-primary mt-20">
        <div className="container">
          <div className="cheddarflow-module">
            <div className="cheddarflow-module-content">
              {/* Left Panel - Text Content */}
              <div className="cheddarflow-text-content">
                <h2 className="cheddarflow-title">
                  Profit with <span className="cheddarflow-highlight">insider alerts</span>
                </h2>
                <p className="cheddarflow-description">
                  Our AI-driven system constantly scans the market for unusual insider trading activity, detecting large, influential trades. When a potential trade opportunity emerges, the system triggers an Insider Alert.
                </p>
                <Link to="/dashboard">
                  <Button className="bg-yellow-500 hover:bg-yellow-600 text-black font-semibold px-6 py-3 rounded-lg transition-colors">
                    Learn More
                  </Button>
                </Link>
              </div>

              {/* Right Panel - Data Visualization */}
              <div className="cheddarflow-data-panel">
                <div className="mb-4">
                  <h3 className="text-white font-semibold">Contract Volume/OI: AAPL 125C 12/31/2025</h3>
                </div>
                
                {/* Simple Chart Placeholder */}
                <div className="cheddarflow-chart">
                  <div className="cheddarflow-chart-line"></div>
                  <div className="cheddarflow-alert-marker">
                    <div className="cheddarflow-marker-dot"></div>
                    <div className="cheddarflow-alert-label">Insider Alert: $1.80</div>
                  </div>
                </div>

                {/* Trade Details */}
                <div className="cheddarflow-trade-details">
                  <div className="cheddarflow-detail-header">
                    <span className="cheddarflow-timestamp">3:53:44 PM</span>
                    <span className="cheddarflow-sentiment bullish">BULLISH</span>
                  </div>
                  
                  <div className="cheddarflow-detail-grid">
                    <div className="cheddarflow-detail-item">
                      <div className="cheddarflow-detail-label">TICKER</div>
                      <div className="cheddarflow-detail-value">AAPL</div>
                    </div>
                    <div className="cheddarflow-detail-item">
                      <div className="cheddarflow-detail-label">SHARES</div>
                      <div className="cheddarflow-detail-value">50,000</div>
                    </div>
                    <div className="cheddarflow-detail-item">
                      <div className="cheddarflow-detail-label">VALUE</div>
                      <div className="cheddarflow-detail-value">$8.2M</div>
                    </div>
                    <div className="cheddarflow-detail-item">
                      <div className="cheddarflow-detail-label">CHANGE</div>
                      <div className="cheddarflow-detail-value positive">+76.54%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom Feature Cards */}
      <section className="bottom-feature-cards">
        <div className="container">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Go long or short */}
            <div className="bg-card rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-primary mb-4">Go long or short</h3>
              <p className="text-secondary mb-6">Profit from market upswings or capitalize on downward trends</p>
              <div className="h-32 bg-gradient-to-r from-accent-green to-accent-blue rounded-lg flex items-center justify-center">
                <div className="text-white text-center">
                  <div className="text-4xl font-bold">+126.54%</div>
                  <div className="text-sm opacity-80">Insider Performance</div>
                </div>
              </div>
            </div>

            {/* Capitalize on market movers */}
            <div className="bg-card rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-primary mb-4">Capitalize on market movers</h3>
              <p className="text-secondary mb-6">Maximize your profit potential and enjoy the benefits of a more strategic approach to day or swing trading.</p>
              <div className="h-32 bg-gradient-to-r from-accent-purple to-accent-pink rounded-lg flex items-center justify-center">
                <div className="text-white text-center">
                  <div className="text-4xl font-bold">$2.4M</div>
                  <div className="text-sm opacity-80">Total Insider Value</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Dive deep section */}
      <section className="dive-deep-section">
        <div className="container text-center">
          <h2 className="text-4xl font-bold text-primary mb-8">Dive deep into insider trading data</h2>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="testimonial-section">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-primary mb-12">From our community</h2>
            
            <div className="bg-card rounded-2xl p-10 mb-8">
              <p className="text-xl text-secondary mb-6 italic">
                "Insider Alpha is an incredible tool for tracking insider trading and spotting great trading setups. The filtering functions and ability to customize really sets it apart from the rest."
              </p>
              <div className="flex items-center justify-center gap-4">
                <div className="w-12 h-12 bg-accent-blue rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-lg">TM</span>
                </div>
                <div className="text-left">
                  <p className="text-primary font-semibold">Trader Mentality</p>
                  <p className="text-secondary text-sm">Founder / Trader Mentality</p>
                </div>
              </div>
            </div>

            <Link to="/leaderboard">
              <Button variant="primary" size="lg">
                See what our customers are saying →
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer-section border-t border-border">
        <div className="container">
          <div className="flex justify-between items-start mb-8">
            <div>
              <h3 className="text-xl font-bold text-primary mb-4">Insider Alpha</h3>
              <p className="text-secondary text-sm max-w-md">
                All the analysis information is for reference only and doesn't constitute an investment recommendation.
              </p>
            </div>
            
            <div className="grid grid-cols-3 gap-8">
              <div>
                <h4 className="text-primary font-semibold mb-3">Product</h4>
                <div className="space-y-2">
                  <Link to="/dashboard" className="block text-secondary hover:text-primary transition-colors">Features</Link>
                  <Link to="/leaderboard" className="block text-secondary hover:text-primary transition-colors">Pricing</Link>
                  <Link to="/recent-trades" className="block text-secondary hover:text-primary transition-colors">Blog</Link>
                </div>
              </div>
              
              <div>
                <h4 className="text-primary font-semibold mb-3">Legal</h4>
                <div className="space-y-2">
                  <Link to="/refund" className="block text-secondary hover:text-primary transition-colors">Refund policy</Link>
                  <Link to="/terms" className="block text-secondary hover:text-primary transition-colors">Terms of service</Link>
                  <Link to="/privacy" className="block text-secondary hover:text-primary transition-colors">Privacy Policy</Link>
                </div>
              </div>
              
              <div>
                <h4 className="text-primary font-semibold mb-3">Follow</h4>
                <div className="flex gap-4">
                  <a href="#" className="text-secondary hover:text-primary transition-colors">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                    </svg>
                  </a>
                  <a href="#" className="text-secondary hover:text-primary transition-colors">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.746-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001.012.001z"/>
                    </svg>
                  </a>
                  <a href="#" className="text-secondary hover:text-primary transition-colors">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center text-secondary text-sm">
            <p>&copy; {new Date().getFullYear()} Insider Alpha. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </Layout>
  );
};

export default Homepage;