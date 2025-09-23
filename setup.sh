#!/bin/bash

# Insider Alpha Platform Setup Script

echo "🚀 Setting up Insider Alpha Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed. Please install PostgreSQL first.${NC}"
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Setup database
echo -e "${YELLOW}📊 Setting up database...${NC}"
createdb insider_alpha 2>/dev/null || echo "Database may already exist"

# Load database schema
if [ -f "database/schema.sql" ]; then
    psql insider_alpha < database/schema.sql
    echo -e "${GREEN}✅ Database schema loaded${NC}"
else
    echo -e "${RED}❌ Database schema file not found${NC}"
fi

# Setup backend
echo -e "${YELLOW}🔧 Setting up backend...${NC}"
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Create .env file from example
if [ ! -f ".env" ]; then
    cp env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env file with your API keys${NC}"
fi

cd ..

# Setup frontend
echo -e "${YELLOW}🎨 Setting up frontend...${NC}"
cd frontend

# Install Node.js dependencies
npm install
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

cd ..

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit backend/.env file with your Polygon.io API key"
echo "2. Start the backend: cd backend && source venv/bin/activate && python -m app.main"
echo "3. Start the frontend: cd frontend && npm start"
echo "4. Run data ingestion: cd backend && source venv/bin/activate && python scripts/data_ingestion.py"
echo "5. Run performance calculation: cd backend && source venv/bin/activate && python scripts/performance_calc.py"


