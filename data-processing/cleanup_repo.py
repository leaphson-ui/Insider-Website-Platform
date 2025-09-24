#!/usr/bin/env python3
"""
Clean up the data-processing directory by removing temporary files
"""

import os
import shutil

def cleanup_repo():
    print("🧹 Cleaning up data-processing directory...")
    
    # Files to keep (important)
    keep_files = [
        'ARCHITECTURE_NOTES.md',
        'NAMING_CONVENTION.md', 
        'process_2025_sec_data.py',
        'fix_2025q2_view.sql',
        'robust_import.py',
        'requirements.txt',
        '.env',
        'README.md'
    ]
    
    # Directories to keep
    keep_dirs = [
        'processed_2025_data',
        '2025q2_form345',
        '2006q1_form345'
    ]
    
    # Files to delete (temporary/debug)
    delete_files = [
        'check_2025_data.py',
        'check_actual_structure.py', 
        'check_historical_data.py',
        'check_schemas.py',
        'check_table_structure.py',
        'debug_frontend_query.py',
        'debug_missing_transactions.py',
        'debug_view_issue.py',
        'simple_data_check.py',
        'test_connection.py',
        'test_data_cleaning.py',
        'test_fixed_query.py',
        'test_multi_file_pipeline.py',
        'test_search.py',
        'test_small_import.py',
        'simple_test.py',
        'quick_test.py',
        'clean_duplicates.py',
        'download_sample_data.py',
        'env_example.txt'
    ]
    
    # SQL files to delete (temporary)
    delete_sql_files = [
        'create_2025_tables.sql',
        'create_organized_schemas.sql', 
        'rename_schemas_and_tables_consistent.sql',
        'rename_tables_descriptive.sql'
    ]
    
    # Import scripts to delete (old versions)
    delete_import_files = [
        'import_2025_data.py',
        'import_2025_to_schema.py',
        'import_to_supabase.py',
        'import_to_supabase_final.py',
        'setup_2025_database.py',
        'fix_2025_import.py',
        'setup_full_text_search.py',
        'update_platform_for_descriptive_tables.py'
    ]
    
    # Pipeline files to delete (old versions)
    delete_pipeline_files = [
        'analyze_sec_structure.py',
        'corrected_cleaning_pipeline.py',
        'final_working_pipeline.py',
        'multi_file_cleaning_pipeline.py',
        'fix_data_joining.py',
        'fix_foreign_keys.py'
    ]
    
    # Directories to delete
    delete_dirs = [
        'final_processed_data',
        'fixed_processed_data', 
        'processed_data',
        'sample_data',
        'test_output'
    ]
    
    # Files to delete
    all_delete_files = delete_files + delete_sql_files + delete_import_files + delete_pipeline_files
    
    print(f"📁 Files to keep: {len(keep_files)}")
    print(f"🗑️ Files to delete: {len(all_delete_files)}")
    print(f"📁 Directories to keep: {len(keep_dirs)}")
    print(f"🗑️ Directories to delete: {len(delete_dirs)}")
    
    # Delete files
    deleted_files = 0
    for file in all_delete_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Deleted: {file}")
                deleted_files += 1
            except Exception as e:
                print(f"❌ Error deleting {file}: {e}")
        else:
            print(f"⚠️  File not found: {file}")
    
    # Delete directories
    deleted_dirs = 0
    for dir_name in delete_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✅ Deleted directory: {dir_name}")
                deleted_dirs += 1
            except Exception as e:
                print(f"❌ Error deleting directory {dir_name}: {e}")
        else:
            print(f"⚠️  Directory not found: {dir_name}")
    
    print(f"\n🎉 Cleanup complete!")
    print(f"   Deleted {deleted_files} files")
    print(f"   Deleted {deleted_dirs} directories")
    print(f"   Kept {len(keep_files)} important files")
    print(f"   Kept {len(keep_dirs)} important directories")

if __name__ == "__main__":
    cleanup_repo()
