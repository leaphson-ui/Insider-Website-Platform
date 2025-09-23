#!/usr/bin/env python3
"""
pSEO Page Generator for Insider Alpha Platform
Generates static pages for individual traders, companies, and leaderboards
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import requests
from typing import List, Dict, Any

class PSEOGenerator:
    def __init__(self, db_path: str, output_dir: str, api_base_url: str = "http://localhost:8000"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.api_base_url = api_base_url
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all_pages(self):
        """Generate all pSEO pages"""
        print("🚀 Starting pSEO page generation...")
        
        # Generate individual trader pages
        self.generate_trader_pages()
        
        # Generate company pages
        self.generate_company_pages()
        
        # Generate leaderboard pages
        self.generate_leaderboard_pages()
        
        # Generate sitemap
        self.generate_sitemap()
        
        print("✅ pSEO page generation complete!")
    
    def generate_trader_pages(self):
        """Generate individual trader pages"""
        print("📊 Generating trader pages...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get top traders by performance score
        cursor.execute("""
            SELECT trader_id, name, title, company_ticker, company_name, sector,
                   total_trades, win_rate, performance_score, total_profit_loss
            FROM traders 
            WHERE total_trades >= 10 
            ORDER BY performance_score DESC 
            LIMIT 1000
        """)
        
        traders = cursor.fetchall()
        
        for trader in traders:
            trader_id, name, title, ticker, company_name, sector, total_trades, win_rate, performance_score, profit_loss = trader
            
            # Generate SEO-friendly slug
            slug = self.create_slug(f"{name}-{ticker}")
            
            # Create page content
            page_content = self.create_trader_page_content(
                trader_id, name, title, ticker, company_name, sector,
                total_trades, win_rate, performance_score, profit_loss
            )
            
            # Write to file
            page_path = self.output_dir / f"trader-{slug}.html"
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
        
        conn.close()
        print(f"✅ Generated {len(traders)} trader pages")
    
    def generate_company_pages(self):
        """Generate company pages"""
        print("🏢 Generating company pages...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get companies with most insider activity
        cursor.execute("""
            SELECT company_ticker, company_name, sector, 
                   COUNT(DISTINCT trader_id) as active_insiders,
                   COUNT(*) as total_transactions
            FROM traders 
            GROUP BY company_ticker, company_name, sector
            HAVING total_transactions >= 50
            ORDER BY total_transactions DESC
            LIMIT 500
        """)
        
        companies = cursor.fetchall()
        
        for company in companies:
            ticker, company_name, sector, active_insiders, total_transactions = company
            
            # Generate SEO-friendly slug
            slug = self.create_slug(f"{company_name}-{ticker}")
            
            # Create page content
            page_content = self.create_company_page_content(
                ticker, company_name, sector, active_insiders, total_transactions
            )
            
            # Write to file
            page_path = self.output_dir / f"company-{slug}.html"
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
        
        conn.close()
        print(f"✅ Generated {len(companies)} company pages")
    
    def generate_leaderboard_pages(self):
        """Generate leaderboard pages"""
        print("🏆 Generating leaderboard pages...")
        
        # Generate main leaderboard
        leaderboard_content = self.create_leaderboard_page_content()
        with open(self.output_dir / "leaderboard.html", 'w', encoding='utf-8') as f:
            f.write(leaderboard_content)
        
        # Generate sector-specific leaderboards
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT sector FROM traders WHERE sector IS NOT NULL")
        sectors = [row[0] for row in cursor.fetchall()]
        
        for sector in sectors:
            sector_content = self.create_sector_leaderboard_content(sector)
            sector_slug = self.create_slug(sector)
            with open(self.output_dir / f"leaderboard-{sector_slug}.html", 'w', encoding='utf-8') as f:
                f.write(sector_content)
        
        conn.close()
        print(f"✅ Generated {len(sectors) + 1} leaderboard pages")
    
    def create_trader_page_content(self, trader_id, name, title, ticker, company_name, sector, total_trades, win_rate, performance_score, profit_loss):
        """Create HTML content for trader page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Insider Trading Performance | {ticker} | Insider Alpha</title>
    <meta name="description" content="Track {name}'s insider trading performance at {company_name} ({ticker}). {win_rate:.1f}% win rate, {total_trades} trades, ${profit_loss:,.0f} total value. Follow the smart money.">
    <meta name="keywords" content="{name}, {ticker}, insider trading, {company_name}, stock performance, executive trading">
    <link rel="canonical" href="https://insideralpha.com/trader/{trader_id}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{name} - Insider Trading Performance">
    <meta property="og:description" content="Track {name}'s insider trading performance at {company_name}">
    <meta property="og:type" content="profile">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{name} - Insider Trading Performance">
    <meta name="twitter:description" content="Track {name}'s insider trading performance at {company_name}">
    
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2rem; font-weight: bold; color: #1f2937; }}
        .metric-label {{ color: #6b7280; font-size: 0.875rem; }}
        .positive {{ color: #059669; }}
        .negative {{ color: #dc2626; }}
        .cta {{ background: #3b82f6; color: white; padding: 15px 30px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{name} - Insider Trading Performance</h1>
            <p><strong>{title}</strong> at {company_name} ({ticker})</p>
            {f'<p>Sector: {sector}</p>' if sector else ''}
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value {'positive' if win_rate > 50 else 'negative'}">{win_rate:.1f}%</div>
                <div class="metric-label">Win Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_trades:,}</div>
                <div class="metric-label">Total Trades</div>
            </div>
            <div class="metric">
                <div class="metric-value {'positive' if profit_loss > 0 else 'negative'}">${profit_loss:,.0f}</div>
                <div class="metric-label">Total P&L</div>
            </div>
            <div class="metric">
                <div class="metric-value">{performance_score:.0f}</div>
                <div class="metric-label">Performance Score</div>
            </div>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2>About {name}</h2>
            <p>{name} is {title} at {company_name} ({ticker}) and has made {total_trades} insider trades with a {win_rate:.1f}% win rate. {'Their trades have generated' if profit_loss > 0 else 'Their trades have resulted in a loss of'} ${abs(profit_loss):,.0f} in total value.</p>
            
            <h3>Why Track {name}'s Trades?</h3>
            <ul>
                <li><strong>Proven Track Record:</strong> {win_rate:.1f}% win rate across {total_trades} trades</li>
                <li><strong>Significant Activity:</strong> {total_trades} insider transactions</li>
                <li><strong>Performance Score:</strong> {performance_score:.0f} (higher is better)</li>
                <li><strong>Company Insight:</strong> {title} at {company_name} has unique market knowledge</li>
            </ul>
            
            <a href="https://insideralpha.com" class="cta">Track All Insider Activity →</a>
        </div>
    </div>
</body>
</html>"""
    
    def create_company_page_content(self, ticker, company_name, sector, active_insiders, total_transactions):
        """Create HTML content for company page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} ({ticker}) Insider Trading Activity | Insider Alpha</title>
    <meta name="description" content="Track insider trading activity at {company_name} ({ticker}). {active_insiders} active insiders, {total_transactions} transactions. Follow the smart money at {ticker}.">
    <meta name="keywords" content="{ticker}, {company_name}, insider trading, stock activity, executive trading, {sector}">
    <link rel="canonical" href="https://insideralpha.com/company/{ticker}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{company_name} Insider Trading Activity">
    <meta property="og:description" content="Track insider trading activity at {company_name} ({ticker})">
    <meta property="og:type" content="website">
    
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2rem; font-weight: bold; color: #1f2937; }}
        .metric-label {{ color: #6b7280; font-size: 0.875rem; }}
        .cta {{ background: #3b82f6; color: white; padding: 15px 30px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{company_name} ({ticker}) Insider Trading Activity</h1>
            {f'<p>Sector: {sector}</p>' if sector else ''}
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{active_insiders}</div>
                <div class="metric-label">Active Insiders</div>
            </div>
            <div class="metric">
                <div class="metric-value">{total_transactions:,}</div>
                <div class="metric-label">Total Transactions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{ticker}</div>
                <div class="metric-label">Stock Symbol</div>
            </div>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2>About {company_name} Insider Activity</h2>
            <p>{company_name} ({ticker}) has {active_insiders} active insiders who have made {total_transactions} total transactions. {'This high level of insider activity' if total_transactions > 100 else 'This insider activity'} provides valuable insights into the company's direction and management confidence.</p>
            
            <h3>Why Track {ticker} Insider Activity?</h3>
            <ul>
                <li><strong>Management Insight:</strong> {active_insiders} insiders provide unique company perspective</li>
                <li><strong>Activity Level:</strong> {total_transactions} transactions show significant insider engagement</li>
                <li><strong>Market Signals:</strong> Insider buying/selling patterns indicate management confidence</li>
                <li><strong>Timing Intelligence:</strong> Track when insiders buy or sell {ticker} stock</li>
            </ul>
            
            <a href="https://insideralpha.com" class="cta">Track All Insider Activity →</a>
        </div>
    </div>
</body>
</html>"""
    
    def create_leaderboard_page_content(self):
        """Create HTML content for main leaderboard page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top Performing Insiders - Insider Trading Leaderboard | Insider Alpha</title>
    <meta name="description" content="Discover the top performing corporate insiders ranked by their trading performance. Follow the smart money and track the best insider trading strategies.">
    <meta name="keywords" content="insider trading leaderboard, top performing insiders, best insider traders, executive performance, smart money">
    <link rel="canonical" href="https://insideralpha.com/leaderboard">
    
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; }
        .cta { background: #3b82f6; color: white; padding: 15px 30px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Top Performing Insiders</h1>
            <p>Discover the best performing corporate insiders ranked by their trading performance</p>
            <a href="https://insideralpha.com" class="cta">View Live Leaderboard →</a>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2>Why Track Top Performing Insiders?</h2>
            <ul>
                <li><strong>Proven Track Records:</strong> These insiders have demonstrated consistent trading success</li>
                <li><strong>Market Intelligence:</strong> Top performers often have unique insights into their companies</li>
                <li><strong>Timing Expertise:</strong> Learn from the best timing strategies</li>
                <li><strong>Risk Management:</strong> See how successful insiders manage their positions</li>
            </ul>
            
            <h3>How We Rank Insiders</h3>
            <p>Our leaderboard ranks insiders based on multiple factors including win rate, total profit/loss, number of trades, and performance consistency. This comprehensive scoring system identifies the most successful insider traders.</p>
        </div>
    </div>
</body>
</html>"""
    
    def create_sector_leaderboard_content(self, sector):
        """Create HTML content for sector-specific leaderboard"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Top {sector} Insiders - Insider Trading Leaderboard | Insider Alpha</title>
    <meta name="description" content="Discover the top performing insiders in the {sector} sector. Track the best {sector} insider trading strategies and performance.">
    <meta name="keywords" content="{sector} insider trading, {sector} executives, {sector} insider performance, sector leaderboard">
    <link rel="canonical" href="https://insideralpha.com/leaderboard/{self.create_slug(sector)}">
    
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f9fafb; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; text-align: center; }}
        .cta {{ background: #3b82f6; color: white; padding: 15px 30px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Top {sector} Insiders</h1>
            <p>Discover the best performing insiders in the {sector} sector</p>
            <a href="https://insideralpha.com" class="cta">View Live Leaderboard →</a>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2>Why Track {sector} Insiders?</h2>
            <ul>
                <li><strong>Sector Expertise:</strong> {sector} insiders have deep industry knowledge</li>
                <li><strong>Market Trends:</strong> Track sector-specific buying and selling patterns</li>
                <li><strong>Competitive Intelligence:</strong> See how {sector} executives position their holdings</li>
                <li><strong>Timing Insights:</strong> Learn from the best {sector} timing strategies</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
    
    def create_slug(self, text):
        """Create SEO-friendly slug from text"""
        import re
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def generate_sitemap(self):
        """Generate XML sitemap"""
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://insideralpha.com/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://insideralpha.com/leaderboard</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>"""
        
        # Add all generated pages
        for file_path in self.output_dir.glob("*.html"):
            if file_path.name != "sitemap.xml":
                sitemap_content += f"""
    <url>
        <loc>https://insideralpha.com/{file_path.name}</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>"""
        
        sitemap_content += """
</urlset>"""
        
        with open(self.output_dir / "sitemap.xml", 'w', encoding='utf-8') as f:
            f.write(sitemap_content)

if __name__ == "__main__":
    # Configuration
    DB_PATH = "/Users/ronniederman/insider_alpha_platform/backend/trading.db"
    OUTPUT_DIR = "/Users/ronniederman/insider_alpha_platform/pseo_pages"
    API_BASE_URL = "http://localhost:8000"
    
    # Generate pages
    generator = PSEOGenerator(DB_PATH, OUTPUT_DIR, API_BASE_URL)
    generator.generate_all_pages()
