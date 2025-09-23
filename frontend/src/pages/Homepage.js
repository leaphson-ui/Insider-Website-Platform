import React from 'react'; 
import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';
import Layout from '../components/Layout';

const Homepage = () => {
  return (
    <Layout>
      {/* SVG Gradient Definitions */}
      <svg width="0" height="0" style={{ position: 'absolute' }}>
        <defs>
          <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFB366" />
            <stop offset="50%" stopColor="#FF8A80" />
            <stop offset="100%" stopColor="#B39DDB" />
          </linearGradient>
          <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFB366" />
            <stop offset="50%" stopColor="#FF8A80" />
            <stop offset="100%" stopColor="#B39DDB" />
          </linearGradient>
          <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFB366" />
            <stop offset="50%" stopColor="#FF8A80" />
            <stop offset="100%" stopColor="#B39DDB" />
          </linearGradient>
          <linearGradient id="gradient4" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFB366" />
            <stop offset="50%" stopColor="#FF8A80" />
            <stop offset="100%" stopColor="#B39DDB" />
          </linearGradient>
        </defs>
      </svg>
      {/* Hero Section */}
      <section className="hero-section py-24">
        <div className="container text-center">
          <h1 className="hero-title">
            <span className="gradient-text">A modern insider trading intelligence platform.</span>
          </h1>
          <p className="hero-subtitle">
            Uncover unusual insider activity and follow the smart money in real time.
          </p>
          
          {/* Search Bar */}
          <div className="hero-search mb-8">
            <div className="search-container">
              <div className="search-input-wrapper">
                <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <input 
                  type="text" 
                  placeholder="Search for insider trades, executives, or companies..." 
                  className="search-input"
                />
                <button className="search-button">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M5 12H19M12 5L19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
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
              <div className="feature-icon">
                <div className="gradient-icon">
                  <svg width="96" height="96" viewBox="0 0 96 96" fill="none">
                    <circle cx="48" cy="48" r="40" fill="url(#gradient1)" stroke="url(#gradient1)" strokeWidth="4"/>
                    <circle cx="40" cy="40" r="12" stroke="white" strokeWidth="3"/>
                    <path d="M52 52L64 64" stroke="white" strokeWidth="3" strokeLinecap="round"/>
                  </svg>
                </div>
              </div>
              <div className="feature-text">
                <h3 className="cheddarflow-feature-title">Track executive activity</h3>
                <p className="cheddarflow-feature-description">Gain insights into the latest moves corporate executives and board members are making.</p>
              </div>
            </div>
          </div>
            <div className="cheddarflow-feature-card">
              <div className="feature-content">
                <div className="feature-icon">
                  <div className="gradient-icon">
                    <svg width="96" height="96" viewBox="0 0 96 96" fill="none">
                      <circle cx="48" cy="48" r="40" fill="url(#gradient2)" stroke="url(#gradient2)" strokeWidth="4"/>
                      <path d="M32 40C40 40 40 48 48 48C56 48 56 40 64 40" stroke="white" strokeWidth="4" strokeLinecap="round"/>
                      <path d="M32 48C40 48 40 56 48 56C56 56 56 48 64 48" stroke="white" strokeWidth="4" strokeLinecap="round"/>
                      <path d="M32 56C40 56 40 64 48 64C56 64 56 56 64 56" stroke="white" strokeWidth="4" strokeLinecap="round"/>
                    </svg>
                  </div>
                </div>
                <div className="feature-text">
                  <h3 className="cheddarflow-feature-title">Fast, reliable SEC data</h3>
                  <p className="cheddarflow-feature-description">Get the latest Form 4 filings delivered to you quickly and accurately.</p>
                </div>
              </div>
            </div>
            <div className="cheddarflow-feature-card">
              <div className="feature-content">
                <div className="feature-icon">
                  <div className="gradient-icon">
                    <svg width="96" height="96" viewBox="0 0 96 96" fill="none">
                      <circle cx="48" cy="48" r="40" fill="url(#gradient3)" stroke="url(#gradient3)" strokeWidth="4"/>
                      <rect x="36" y="24" width="24" height="48" rx="4" stroke="white" strokeWidth="4"/>
                      <circle cx="48" cy="36" r="2" fill="white"/>
                      <rect x="42" y="44" width="12" height="2" fill="white"/>
                    </svg>
                  </div>
                </div>
                <div className="feature-text">
                  <h3 className="cheddarflow-feature-title">Superior user experience</h3>
                  <p className="cheddarflow-feature-description">Enjoy an intuitive interface that makes it easy to find the information you need.</p>
                </div>
              </div>
            </div>
            <div className="cheddarflow-feature-card">
              <div className="feature-content">
                <div className="feature-icon">
                  <div className="gradient-icon">
                    <svg width="96" height="96" viewBox="0 0 96 96" fill="none">
                      <circle cx="48" cy="48" r="40" fill="url(#gradient4)" stroke="url(#gradient4)" strokeWidth="4"/>
                      <path d="M48 24L52 40L68 40L56 48L60 64L48 56L36 64L40 48L28 40L44 40L48 24Z" fill="white"/>
                    </svg>
                  </div>
                </div>
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


      {/* Community Section - 21st.dev Testimonials */}
      <section className="py-16 md:py-32 bg-primary" style={{paddingTop: '100px'}}>
        <div className="mx-auto max-w-6xl space-y-8 px-6 md:space-y-16">
          <div className="relative z-10 mx-auto max-w-xl space-y-6 text-center md:space-y-12">
            <h2 className="cheddarflow-title">From our community</h2>
            <p className="text-lg text-secondary">See what our customers are saying about Insider Alpha</p>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="testimonial-card-small">
              <div className="testimonial-content">
                <blockquote className="grid h-full grid-rows-[1fr_auto] gap-6">
                  <p className="text-primary">Insider Alpha has transformed the way I track insider activity. Their real-time alerts and comprehensive data have significantly accelerated my trading workflow.</p>

                  <div className="grid grid-cols-[auto_1fr] gap-3">
                    <div className="testimonial-avatar">
                      <img
                        src="https://images.unsplash.com/photo-1599566150163-29194dcaad36?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=3387&q=80"
                        alt="John Doe"
                        height="48"
                        width="48"
                        loading="lazy"
                      />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-primary">John Doe</p>
                      <span className="text-secondary block text-sm">Software Engineer</span>
                    </div>
                  </div>
                </blockquote>
              </div>
            </div>
            
            <div className="testimonial-card-small">
              <div className="testimonial-content">
                <blockquote className="grid h-full grid-rows-[1fr_auto] gap-6">
                  <p className="text-primary">Insider Alpha is really extraordinary and very practical, no need to break your head. A real gold mine.</p>

                  <div className="grid grid-cols-[auto_1fr] gap-3">
                    <div className="testimonial-avatar">
                      <img
                        src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YXZhdGFyfGVufDB8fDB8fHww&auto=format&fit=crop&w=800&q=60"
                        alt="Robert Johnson"
                        height="48"
                        width="48"
                        loading="lazy"
                      />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-primary">Robert Johnson</p>
                      <span className="text-secondary block text-sm">Product Manager</span>
                    </div>
                  </div>
                </blockquote>
              </div>
            </div>
            
            <div className="testimonial-card-small">
              <div className="testimonial-content">
                <blockquote className="grid h-full grid-rows-[1fr_auto] gap-6">
                  <p className="text-primary">Great work on Insider Alpha. This is one of the best trading platforms that I have seen so far!</p>

                  <div className="grid grid-cols-[auto_1fr] gap-3">
                    <div className="testimonial-avatar">
                      <img
                        src="https://images.unsplash.com/photo-1580489944761-15a19d654956?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8YXZhdGFyfGVufDB8fDB8fHww&auto=format&fit=crop&w=800&q=60"
                        alt="Jane Smith"
                        height="48"
                        width="48"
                        loading="lazy"
                      />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-primary">Jane Smith</p>
                      <span className="text-secondary block text-sm">Data Scientist</span>
                    </div>
                  </div>
                </blockquote>
              </div>
            </div>
            
            <div className="testimonial-card-small variant-mixed">
              <div className="testimonial-content">
                <blockquote className="grid h-full grid-rows-[1fr_auto] gap-6">
                  <p className="text-primary">Great work on Insider Alpha. This is one of the best trading platforms that I have seen so far!</p>

                  <div className="grid grid-cols-[auto_1fr] gap-3">
                    <div className="testimonial-avatar">
                      <img
                        src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fGF2YXRhcnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60"
                        alt="Emily Davis"
                        height="48"
                        width="48"
                        loading="lazy"
                      />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-primary">Emily Davis</p>
                      <span className="text-secondary block text-sm">UX Designer</span>
                    </div>
                  </div>
                </blockquote>
              </div>
            </div>
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