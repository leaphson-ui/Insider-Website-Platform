#!/usr/bin/env python3
"""
Database Setup Script
Creates the transactions table with proper schema and constraints
"""

import os
import logging
from pathlib import Path
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Setup database table with schema"""
    # Load environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    try:
        # Connect to Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Connected to Supabase")
        
        # Read schema file
        schema_file = Path(__file__).parent / "database_schema.sql"
        if not schema_file.exists():
            logger.error(f"❌ Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        logger.info("📄 Schema file loaded")
        
        # Execute schema (Supabase doesn't support direct SQL execution via Python client)
        # We'll need to run this manually in the Supabase dashboard
        logger.warning("⚠️  Database schema must be created manually in Supabase dashboard")
        logger.info("📋 Please run the following SQL in your Supabase SQL editor:")
        logger.info("=" * 60)
        print(schema_sql)
        logger.info("=" * 60)
        
        # Test if table exists
        try:
            result = supabase.table('insider_transactions').select('id').limit(1).execute()
            logger.info("✅ Table 'insider_transactions' exists and is accessible")
            return True
        except Exception as e:
            logger.error(f"❌ Table 'insider_transactions' not found or not accessible: {e}")
            logger.info("Please create the table using the SQL above")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_database()
