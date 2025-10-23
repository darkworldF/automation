#!/usr/bin/env python3
"""
Engwe Product API Importer
Main runner for API-based product import to Shopify
"""

import os
import sys
import configparser
from datetime import datetime

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    
    if not os.path.exists('config.ini'):
        print("ERROR: config.ini not found!")
        print("Please make sure you have configured your API credentials.")
        return None
    
    config.read('config.ini')
    return config

def validate_api_config(config):
    """Validate API configuration"""
    required_keys = [
        ('SHOPIFY_API', 'store_url'),
        ('SHOPIFY_API', 'access_token'),
        ('SHOPIFY_API', 'api_key'),
        ('SHOPIFY_API', 'api_secret')
    ]
    
    for section, key in required_keys:
        if not config.has_option(section, key) or not config.get(section, key).strip():
            print(f"ERROR: Missing or empty {section}.{key} in config.ini")
            return False
    
    return True

def main():
    """Main function to run API import"""
    print("Loading configuration...")
    config = load_config()
    if not config:
        return 1
    
    print("Validating API credentials...")
    if not validate_api_config(config):
        print("\nPlease update config.ini with your Shopify API credentials:")
        print("1. store_url = your-store.myshopify.com")
        print("2. access_token = shpat_your_access_token")
        print("3. api_key = your_api_key")
        print("4. api_secret = your_api_secret")
        return 1
    
    try:
        print("\nStarting product import process...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Source: engwe.com")
        print(f"Destination: {config.get('SHOPIFY_API', 'store_url')}")
        print("-" * 50)
        
        # Import the shopify API importer
        from shopify_api_importer import ShopifyAPIImporter
        
        # Create importer instance
        importer = ShopifyAPIImporter(config)
        
        # Run the import
        success = importer.run_full_import()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 IMPORT COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print("\nNext steps:")
            print("1. Log into your Shopify admin")
            print("2. Go to Products section")
            print("3. Review imported products (they're saved as drafts)")
            print("4. Publish products when ready")
            print("\nImport log saved to: import_log.txt")
        else:
            print("\n❌ Import failed. Check import_log.txt for details.")
            return 1
            
    except ImportError:
        print("ERROR: shopify_api_importer module not found!")
        print("Please make sure all required files are present.")
        return 1
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("Check import_log.txt for detailed error information.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("\nPress Enter to exit...")
    sys.exit(exit_code)