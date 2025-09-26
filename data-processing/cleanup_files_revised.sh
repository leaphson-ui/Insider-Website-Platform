#!/bin/bash

echo "🧹 REVISED CLEANUP - KEEPING SEC STRUCTURE ANALYSIS..."
echo "====================================================="

# Test files (safe to delete)
echo "🗑️  Removing test files..."
rm -f test_2025q2.py
rm -f quick_test_2025q2.py
rm -f quick_test_100_transactions.py
rm -f medium_test_1k_transactions.py
rm -f test_small_sample.py

# Temporary directories
echo "🗑️  Removing temporary directories..."
rm -rf temp_2025q2_analysis/
rm -rf temp_2025q2_review/
rm -rf temp_2025q2_test/
rm -rf processed_2025_data/

# Old data directories (individual quarters)
echo "🗑️  Removing individual quarter data..."
rm -rf 2006q1_form345/
rm -rf 2025q2_form345/

# SQL fix files (already applied)
echo "🗑️  Removing applied SQL fixes..."
rm -f update_database_schema.sql
rm -f update_quarter_column.sql
rm -f fix_2025q2_view.sql

# Utility scripts (one-time use)
echo "🗑️  Removing one-time utility scripts..."
rm -f clear_database.py
rm -f MANUAL_CLEANUP_STEPS.md
rm -f NAMING_CONVENTION.md
rm -f processing.log

echo ""
echo "✅ REVISED CLEANUP COMPLETE!"
echo ""
echo "📁 REMAINING FILES (KEPT):"
echo "  ✅ Core processors: processor_post_2023.py, fail_safe_processor.py, process_post_2023_only.py"
echo "  ✅ Database: database_schema.sql, setup_database.py"
echo "  ✅ Monitoring: progress_monitor.py"
echo "  ✅ Documentation: FAIL_SAFE_PROCESSING_PLAN.md, ARCHITECTURE_NOTES.md, README.md"
echo "  ✅ SEC Analysis: sec_structure_analysis_detailed.json, sec_structure_summary.json, analyze_all_structures.py"
echo "  ✅ Data: sec_insider_data/ (raw SEC data)"
echo "  ✅ Config: .env, requirements.txt"
echo ""
echo "🎯 Your core work AND SEC structure analysis are preserved!"
