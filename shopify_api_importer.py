#!/usr/bin/env python3
"""
Shopify API Integration Script for ENGWE Products
Direct import to Shopify store using Admin API
"""

import json
import requests
import time
import logging
from typing import List, Dict, Optional
import os
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ShopifyConfig:
    """Shopify API configuration"""
    shop_name: str  # your-shop-name (without .myshopify.com)
    access_token: str  # Private app access token
    api_version: str = "2024-01"  # API version
    
    @property
    def base_url(self) -> str:
        return f"https://{self.shop_name}.myshopify.com/admin/api/{self.api_version}"

class ShopifyImporter:
    """Import products directly to Shopify using Admin API"""
    
    def __init__(self, config: ShopifyConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-Shopify-Access-Token': config.access_token,
            'Content-Type': 'application/json'
        })
        
        # Rate limiting
        self.max_requests_per_second = 2
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Ensure we don't exceed Shopify rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.max_requests_per_second
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            self._rate_limit()
            response = self.session.get(f"{self.config.base_url}/shop.json")
            response.raise_for_status()
            
            shop_data = response.json()
            logger.info(f"Connected to shop: {shop_data['shop']['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Shopify: {e}")
            return False
    
    def get_existing_products(self) -> List[Dict]:
        """Get all existing products from the store"""
        products = []
        page_info = None
        
        while True:
            try:
                self._rate_limit()
                
                url = f"{self.config.base_url}/products.json?limit=250"
                if page_info:
                    url += f"&page_info={page_info}"
                
                response = self.session.get(url)
                response.raise_for_status()
                
                data = response.json()
                products.extend(data['products'])
                
                # Check for pagination
                link_header = response.headers.get('Link', '')
                if 'rel="next"' in link_header:
                    # Extract page_info from Link header
                    import re
                    next_match = re.search(r'<[^>]*[?&]page_info=([^&>]*)>; rel="next"', link_header)
                    if next_match:
                        page_info = next_match.group(1)
                    else:
                        break
                else:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching existing products: {e}")
                break
        
        logger.info(f"Found {len(products)} existing products")
        return products
    
    def create_product(self, product_data: Dict) -> Optional[Dict]:
        """Create a single product in Shopify"""
        try:
            self._rate_limit()
            
            # Prepare product data for Shopify API
            shopify_product = {
                "product": {
                    "title": product_data.get('name', product_data.get('title', '')),
                    "body_html": product_data.get('description', ''),
                    "vendor": product_data.get('vendor', 'ENGWE'),
                    "product_type": product_data.get('product_type', 'Electric Bike'),
                    "handle": product_data.get('handle', ''),
                    "published": product_data.get('published', True),
                    "tags": ', '.join(product_data.get('tags', [])),
                    "variants": [{
                        "title": "Default Title",
                        "price": str(product_data.get('price', 0)),
                        "sku": product_data.get('sku', ''),
                        "inventory_quantity": product_data.get('inventory_quantity', 100),
                        "inventory_management": "shopify",
                        "inventory_policy": "deny",
                        "fulfillment_service": "manual",
                        "requires_shipping": product_data.get('requires_shipping', True),
                        "taxable": product_data.get('taxable', True),
                        "weight": 0,
                        "weight_unit": "kg"
                    }],
                    "images": [],
                    "metafields": []
                }
            }
            
            # Add images
            images = product_data.get('images', [])
            if images:
                shopify_product["product"]["images"] = [
                    {
                        "src": img_url,
                        "alt": product_data.get('name', ''),
                        "position": idx + 1
                    } for idx, img_url in enumerate(images[:10])  # Limit to 10 images
                ]
            
            # Add metafields for specifications
            if product_data.get('specifications'):
                shopify_product["product"]["metafields"].append({
                    "namespace": "specifications",
                    "key": "details",
                    "value": json.dumps(product_data['specifications']),
                    "type": "json"
                })
            
            if product_data.get('features'):
                shopify_product["product"]["metafields"].append({
                    "namespace": "product",
                    "key": "features",
                    "value": json.dumps(product_data['features']),
                    "type": "json"
                })
            
            # Create the product
            response = self.session.post(
                f"{self.config.base_url}/products.json",
                json=shopify_product
            )
            response.raise_for_status()
            
            created_product = response.json()['product']
            logger.info(f"Created product: {created_product['title']} (ID: {created_product['id']})")
            return created_product
            
        except Exception as e:
            logger.error(f"Failed to create product {product_data.get('name', 'Unknown')}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def bulk_import(self, products_file: str, start_index: int = 0, max_products: int = None) -> Dict:
        """Import products in bulk from JSON file"""
        logger.info(f"Starting bulk import from {products_file}")
        
        # Load products
        with open(products_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('products', data) if isinstance(data, dict) else data
        
        if max_products:
            products = products[start_index:start_index + max_products]
        else:
            products = products[start_index:]
        
        logger.info(f"Importing {len(products)} products...")
        
        # Import results
        results = {
            'successful': [],
            'failed': [],
            'skipped': []
        }
        
        # Get existing products for duplicate checking
        existing_products = self.get_existing_products()
        existing_handles = {p['handle'] for p in existing_products}
        
        for idx, product in enumerate(products, start=start_index + 1):
            try:
                product_name = product.get('name', product.get('title', f'Product {idx}'))
                product_handle = product.get('handle', '')
                
                # Skip if product already exists
                if product_handle in existing_handles:
                    logger.info(f"Skipping existing product: {product_name}")
                    results['skipped'].append({
                        'product': product,
                        'reason': 'already_exists'
                    })
                    continue
                
                logger.info(f"Creating product {idx}: {product_name}")
                
                created_product = self.create_product(product)
                
                if created_product:
                    results['successful'].append(created_product)
                else:
                    results['failed'].append({
                        'product': product,
                        'reason': 'creation_failed'
                    })
                
                # Progress update
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(products)} products processed")
                
            except Exception as e:
                logger.error(f"Error processing product {idx}: {e}")
                results['failed'].append({
                    'product': product,
                    'reason': str(e)
                })
        
        # Final summary
        logger.info(f"Import completed:")
        logger.info(f"  Successful: {len(results['successful'])}")
        logger.info(f"  Failed: {len(results['failed'])}")
        logger.info(f"  Skipped: {len(results['skipped'])}")
        
        return results
    
    def save_import_report(self, results: Dict, output_file: str = None) -> str:
        """Save import results to a report file"""
        if output_file is None:
            output_file = f"shopify_import_report_{int(time.time())}.json"
        
        report_data = {
            'import_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_processed': len(results['successful']) + len(results['failed']) + len(results['skipped']),
                'successful': len(results['successful']),
                'failed': len(results['failed']),
                'skipped': len(results['skipped'])
            },
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Import report saved to: {output_file}")
        return output_file

def main():
    """Main function for Shopify API import"""
    print("ENGWE Shopify API Importer")
    print("=" * 50)
    
    # Get configuration
    shop_name = input("Enter your Shopify shop name (without .myshopify.com): ").strip()
    access_token = input("Enter your private app access token: ").strip()
    
    if not shop_name or not access_token:
        print("Error: Shop name and access token are required")
        return
    
    # Get import file
    import_file = input("Enter path to products JSON file: ").strip()
    if not os.path.exists(import_file):
        print(f"Error: File {import_file} not found")
        return
    
    # Optional parameters
    start_index = int(input("Start from product index (default 0): ") or "0")
    max_products_input = input("Max products to import (default all): ").strip()
    max_products = int(max_products_input) if max_products_input else None
    
    print("\nStarting import...")
    
    # Create importer and test connection
    config = ShopifyConfig(shop_name=shop_name, access_token=access_token)
    importer = ShopifyImporter(config)
    
    if not importer.test_connection():
        print("Failed to connect to Shopify. Check your credentials.")
        return
    
    # Run import
    results = importer.bulk_import(import_file, start_index, max_products)
    
    # Save report
    report_file = importer.save_import_report(results)
    
    print(f"\nImport completed!")
    print(f"Report saved to: {report_file}")
    
    if results['failed']:
        print("\nSome products failed to import. Check the report for details.")

if __name__ == "__main__":
    main()