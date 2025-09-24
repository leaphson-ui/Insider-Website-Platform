#!/usr/bin/env python3
"""
Test script for the multi-file SEC data cleaning pipeline
"""

import os
import sys
from multi_file_cleaning_pipeline import MultiFileSECCleaner

def test_pipeline():
    """Test the multi-file cleaning pipeline"""
    print("SEC Multi-File Data Cleaning Pipeline Test")
    print("=" * 50)
    
    # Check if we have quarter directories
    quarter_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and 'q' in d.lower()]
    
    if not quarter_dirs:
        print("❌ No quarter directories found!")
        print("\nExpected directories like:")
        print("  - 2006q1_form345")
        print("  - 2024q3_form345")
        print("  - etc.")
        print("\nPlease download some quarterly SEC datasets first.")
        return False
    
    print(f"✅ Found {len(quarter_dirs)} quarter directories:")
    for dir in quarter_dirs:
        print(f"  - {dir}")
    
    # Test with first available quarter
    test_quarter = quarter_dirs[0]
    print(f"\n🧪 Testing with: {test_quarter}")
    
    # Check what files are in the test quarter
    files = os.listdir(test_quarter)
    print(f"Files in {test_quarter}:")
    for file in sorted(files):
        file_path = os.path.join(test_quarter, file)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"  - {file} ({size_mb:.1f} MB)")
    
    # Initialize cleaner
    cleaner = MultiFileSECCleaner()
    
    try:
        # Process the test quarter
        print(f"\n🔄 Processing {test_quarter}...")
        quarter_data = cleaner.process_quarter_directory(test_quarter)
        
        # Check for errors
        if 'error' in quarter_data:
            print(f"❌ Error processing {test_quarter}: {quarter_data['error']}")
            return False
        
        # Consolidate data
        consolidated = cleaner.consolidate_quarter_data(quarter_data)
        
        # Print results
        print(f"\n✅ Successfully processed {test_quarter}!")
        
        stats = consolidated['stats']
        print(f"\n📊 Results:")
        print(f"  Transactions: {stats['total_transactions']:,}")
        print(f"  Companies: {stats['unique_companies']:,}")
        print(f"  Insiders: {stats['unique_insiders']:,}")
        
        if stats['date_range']:
            print(f"  Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        if stats['transaction_types']:
            print(f"  Transaction types:")
            for code, count in list(stats['transaction_types'].items())[:5]:  # Show top 5
                print(f"    {code}: {count:,}")
        
        # Save test results
        os.makedirs("test_output", exist_ok=True)
        cleaner.save_processed_data({test_quarter: consolidated}, "test_output")
        
        print(f"\n💾 Test results saved to: test_output/{test_quarter}/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_next_steps():
    """Show next steps after successful test"""
    print("\n" + "=" * 50)
    print("🎉 PIPELINE TEST SUCCESSFUL!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. 📥 Download more quarterly datasets (2006-2024)")
    print("2. 🗄️  Set up Supabase project and database schema")
    print("3. 🔄 Process all quarters: python multi_file_cleaning_pipeline.py")
    print("4. 📊 Import to Supabase: python import_to_supabase.py")
    print("5. 🎨 Build frontend dashboard")
    
    print("\n💡 Tips:")
    print("- Start with 2-3 quarters to test the full pipeline")
    print("- Monitor memory usage with large datasets")
    print("- Check the processed_data/ directory for cleaned files")

if __name__ == "__main__":
    success = test_pipeline()
    
    if success:
        show_next_steps()
    else:
        print("\n❌ Test failed. Please check the errors above and try again.")
        sys.exit(1)
