#!/usr/bin/env python3
"""
Simple script to run the ENGWE product import
"""

from engwe_product_importer import EngweProductImporter
from datetime import datetime
import os

def main():
    print("🚲 ENGWE to NLEbike Product Importer")
    print("=" * 50)
    print("This tool will extract all products from Engwe.com and prepare them for import to NLEbike.com")
    print()
    
    # Get user preferences
    print("Configuration Options:")
    download_images = input("📸 Download product images? (y/N): ").strip().lower() == 'y'
    
    if download_images:
        print("⚠️  Warning: Downloading images will take longer but provides complete product data")
    
    max_workers = input("🔧 Max concurrent workers (default 3, max 10): ").strip()
    try:
        max_workers = min(int(max_workers) if max_workers else 3, 10)
    except ValueError:
        max_workers = 3
    
    print(f"\n🔄 Starting import with {max_workers} workers...")
    print("This may take 10-30 minutes depending on settings.")
    print()
    
    # Create output directory
    output_dir = f"engwe_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Run import
    importer = EngweProductImporter(output_dir=output_dir)
    export_files = importer.run_full_import(
        download_images=download_images,
        max_workers=max_workers
    )
    
    if export_files:
        print("\n✅ Import completed successfully!")
        print("\n📁 Generated files:")
        for file_type, filepath in export_files.items():
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"   {file_type.upper()}: {filepath} ({file_size:.1f} KB)")
        
        print(f"\n📂 All files saved in: {output_dir}/")
        print("\n🛒 Next steps for importing to NLEbike.com:")
        print("   1. Review the generated CSV file")
        print("   2. Upload to Shopify Admin → Products → Import")
        print("   3. Or use the JSON file for API integration")
        print("   4. Check the summary report for any issues")
        
        if download_images:
            print("   5. Upload images from the images/ folder to your store")
    else:
        print("\n❌ Import failed. Check the log file for details.")

if __name__ == "__main__":
    main()
