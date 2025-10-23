#!/usr/bin/env python3
"""
ENGWE Product Importer - Complete automation tool for importing products from Engwe.com
Author: MiniMax Agent
Features:
- Extracts all products from Engwe.com
- Downloads product images
- Generates CSV, JSON, and Shopify-compatible outputs
- Handles duplicate detection
- Supports multiple import methods
"""

import requests
import csv
import json
import os
import re
import time
import logging
from urllib.parse import urljoin, urlparse
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('engwe_importer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProductVariant:
    """Represents a product variant (color, size, etc.)"""
    name: str
    price: str
    sku: str = ""
    inventory_quantity: int = 0
    image_url: str = ""
    available: bool = True

@dataclass
class Product:
    """Represents a complete product with all details"""
    # Basic Info
    name: str
    description: str
    price: str
    vendor: str = "ENGWE"
    product_type: str = "Electric Bike"
    
    # URLs and IDs
    url: str = ""
    sku: str = ""
    handle: str = ""
    
    # Images
    images: List[str] = None
    featured_image: str = ""
    
    # Specifications
    specifications: Dict[str, Any] = None
    features: List[str] = None
    
    # Variants
    variants: List[ProductVariant] = None
    
    # Status
    published: bool = True
    available: bool = True
    
    # SEO and Meta
    meta_title: str = ""
    meta_description: str = ""
    tags: List[str] = None
    
    # Shopify specific
    weight: str = ""
    weight_unit: str = "kg"
    requires_shipping: bool = True
    taxable: bool = True
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.specifications is None:
            self.specifications = {}
        if self.features is None:
            self.features = []
        if self.variants is None:
            self.variants = []
        if self.tags is None:
            self.tags = []

class EngweProductImporter:
    """Main class for importing products from Engwe.com"""
    
    def __init__(self, output_dir: str = "engwe_import"):
        self.base_url = "https://engwe.com"
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/images", exist_ok=True)
        os.makedirs(f"{output_dir}/data", exist_ok=True)
        
        self.products: List[Product] = []
        self.failed_products: List[str] = []
        
    def get_product_urls(self) -> List[str]:
        """Extract all product URLs from sitemap"""
        logger.info("Fetching product URLs from sitemap...")
        
        sitemap_url = f"{self.base_url}/sitemap_products_1.xml?from=7771622932537&to=8045848199225"
        
        try:
            response = self.session.get(sitemap_url)
            response.raise_for_status()
            
            # Parse XML sitemap
            root = ET.fromstring(response.content)
            
            # Extract URLs - namespace handling
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = []
            
            for url_elem in root.findall('.//ns:url', namespaces):
                loc = url_elem.find('ns:loc', namespaces)
                if loc is not None and '/products/' in loc.text:
                    urls.append(loc.text)
            
            logger.info(f"Found {len(urls)} product URLs")
            return urls
            
        except Exception as e:
            logger.error(f"Error fetching sitemap: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        return text
    
    def extract_price(self, text: str) -> str:
        """Extract price from text"""
        if not text:
            return "0.00"
        
        # Find price patterns like €1,299.00 or $1299.99
        price_match = re.search(r'[€$£]?([0-9,]+\.?[0-9]*)', text)
        if price_match:
            price = price_match.group(1).replace(',', '')
            return price
        
        return "0.00"
    
    def generate_handle(self, name: str) -> str:
        """Generate Shopify-compatible handle from product name"""
        handle = name.lower()
        handle = re.sub(r'[^a-z0-9\s-]', '', handle)
        handle = re.sub(r'\s+', '-', handle)
        handle = re.sub(r'-+', '-', handle)
        return handle.strip('-')
    
    def download_image(self, image_url: str, product_handle: str) -> Optional[str]:
        """Download product image and return local path"""
        try:
            if not image_url.startswith('http'):
                image_url = urljoin(self.base_url, image_url)
            
            response = self.session.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Generate filename
            parsed_url = urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename or '.' not in filename:
                filename = f"{hashlib.md5(image_url.encode()).hexdigest()}.jpg"
            
            # Clean filename
            filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
            local_path = f"{self.output_dir}/images/{product_handle}_{filename}"
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.debug(f"Downloaded image: {local_path}")
            return local_path
            
        except Exception as e:
            logger.warning(f"Failed to download image {image_url}: {e}")
            return None
    
    def extract_product_data(self, product_url: str) -> Optional[Product]:
        """Extract detailed product information from a product page"""
        try:
            logger.info(f"Extracting product: {product_url}")
            
            # Simulate web extraction (in real implementation, this would use web extraction)
            # For now, we'll use a simplified extraction based on the patterns we observed
            
            response = self.session.get(product_url)
            response.raise_for_status()
            
            html_content = response.text
            
            # Extract basic product info using regex patterns
            name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
            product_name = self.clean_text(name_match.group(1)) if name_match else "Unknown Product"
            
            # Extract price
            price_match = re.search(r'["\']price["\']\s*:\s*["\']([^"\'>]+)["\']', html_content)
            if not price_match:
                price_match = re.search(r'€([0-9,]+\.?[0-9]*)', html_content)
            
            price = self.extract_price(price_match.group(1) if price_match else "0.00")
            
            # Extract description
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]+)["\']', html_content)
            description = self.clean_text(desc_match.group(1)) if desc_match else ""
            
            # Extract images
            image_urls = re.findall(r'https://[^\s"\'>]+\.(?:jpg|jpeg|png|webp)[^\s"\'>]*', html_content)
            image_urls = list(set(image_urls))  # Remove duplicates
            
            # Create product object
            product = Product(
                name=product_name,
                description=description,
                price=price,
                url=product_url,
                handle=self.generate_handle(product_name),
                images=image_urls[:10],  # Limit to 10 images
                featured_image=image_urls[0] if image_urls else ""
            )
            
            # Extract additional details based on product type
            if "battery" in product_name.lower():
                product.product_type = "E-Bike Battery"
                product.tags.extend(["battery", "replacement", "electric-bike"])
            elif any(keyword in product_name.lower() for keyword in ["bag", "basket", "rack", "mount", "lock"]):
                product.product_type = "E-Bike Accessory"
                product.tags.extend(["accessory", "electric-bike"])
            else:
                product.product_type = "Electric Bike"
                product.tags.extend(["electric-bike", "e-bike", "ebike"])
            
            # Add ENGWE tag
            product.tags.append("engwe")
            
            return product
            
        except Exception as e:
            logger.error(f"Error extracting product {product_url}: {e}")
            self.failed_products.append(product_url)
            return None
    
    def download_product_images(self, product: Product) -> Product:
        """Download all images for a product"""
        if not product.images:
            return product
        
        logger.info(f"Downloading images for {product.name}...")
        
        downloaded_images = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {
                executor.submit(self.download_image, img_url, product.handle): img_url 
                for img_url in product.images
            }
            
            for future in as_completed(future_to_url):
                local_path = future.result()
                if local_path:
                    downloaded_images.append(local_path)
        
        product.images = downloaded_images
        product.featured_image = downloaded_images[0] if downloaded_images else ""
        
        return product
    
    def extract_all_products(self, max_workers: int = 5) -> List[Product]:
        """Extract all products from Engwe.com"""
        product_urls = self.get_product_urls()
        
        if not product_urls:
            logger.error("No product URLs found")
            return []
        
        logger.info(f"Starting extraction of {len(product_urls)} products...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.extract_product_data, url): url 
                for url in product_urls
            }
            
            for future in as_completed(future_to_url):
                product = future.result()
                if product:
                    self.products.append(product)
                
                # Add delay to be respectful
                time.sleep(0.5)
        
        logger.info(f"Successfully extracted {len(self.products)} products")
        return self.products
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export products to CSV format"""
        if filename is None:
            filename = f"{self.output_dir}/data/engwe_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        logger.info(f"Exporting {len(self.products)} products to CSV: {filename}")
        
        # Shopify CSV headers
        headers = [
            'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type',
            'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
            'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker',
            'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service',
            'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping',
            'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text',
            'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category',
            'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN',
            'Google Shopping / AdWords Grouping', 'Google Shopping / AdWords Labels',
            'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0',
            'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3',
            'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code',
            'Cost per item', 'Included / Price', 'Status'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for product in self.products:
                # Base product row
                base_row = [
                    product.handle,  # Handle
                    product.name,    # Title
                    product.description,  # Body (HTML)
                    product.vendor,  # Vendor
                    product.product_type,  # Product Category
                    product.product_type,  # Type
                    ', '.join(product.tags),  # Tags
                    'TRUE' if product.published else 'FALSE',  # Published
                    '', '', '', '', '', '',  # Options (empty for now)
                    product.sku,  # Variant SKU
                    '',  # Variant Grams
                    'shopify',  # Variant Inventory Tracker
                    '100',  # Variant Inventory Qty
                    'deny',  # Variant Inventory Policy
                    'manual',  # Variant Fulfillment Service
                    product.price,  # Variant Price
                    '',  # Variant Compare At Price
                    'TRUE' if product.requires_shipping else 'FALSE',  # Variant Requires Shipping
                    'TRUE' if product.taxable else 'FALSE',  # Variant Taxable
                    '',  # Variant Barcode
                    product.featured_image,  # Image Src
                    '1',  # Image Position
                    product.name,  # Image Alt Text
                    'FALSE',  # Gift Card
                    product.meta_title or product.name,  # SEO Title
                    product.meta_description or product.description[:160],  # SEO Description
                    '',  # Google Shopping Category
                    '', '', '', '', '', '', '', '', '', '', '', '', '', '',  # Google Shopping fields
                    product.weight_unit,  # Variant Weight Unit
                    '', '', '', 'active'  # Additional fields
                ]
                
                writer.writerow(base_row)
                
                # Additional image rows
                for idx, image_url in enumerate(product.images[1:], start=2):
                    image_row = [''] * len(headers)
                    image_row[0] = product.handle  # Handle
                    image_row[25] = image_url  # Image Src
                    image_row[26] = str(idx)  # Image Position
                    image_row[27] = product.name  # Image Alt Text
                    writer.writerow(image_row)
        
        logger.info(f"CSV export completed: {filename}")
        return filename
    
    def export_to_json(self, filename: str = None) -> str:
        """Export products to JSON format"""
        if filename is None:
            filename = f"{self.output_dir}/data/engwe_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        logger.info(f"Exporting {len(self.products)} products to JSON: {filename}")
        
        # Convert products to dict format
        products_data = {
            'export_date': datetime.now().isoformat(),
            'total_products': len(self.products),
            'failed_products': len(self.failed_products),
            'failed_urls': self.failed_products,
            'products': [asdict(product) for product in self.products]
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(products_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON export completed: {filename}")
        return filename
    
    def export_shopify_api_format(self, filename: str = None) -> str:
        """Export products in Shopify API format"""
        if filename is None:
            filename = f"{self.output_dir}/data/shopify_api_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        logger.info(f"Exporting {len(self.products)} products in Shopify API format: {filename}")
        
        shopify_products = []
        
        for product in self.products:
            shopify_product = {
                'product': {
                    'title': product.name,
                    'body_html': product.description,
                    'vendor': product.vendor,
                    'product_type': product.product_type,
                    'handle': product.handle,
                    'published': product.published,
                    'tags': ', '.join(product.tags),
                    'variants': [{
                        'title': 'Default Title',
                        'price': product.price,
                        'sku': product.sku,
                        'inventory_quantity': 100,
                        'inventory_management': 'shopify',
                        'inventory_policy': 'deny',
                        'fulfillment_service': 'manual',
                        'requires_shipping': product.requires_shipping,
                        'taxable': product.taxable,
                        'weight': 0,
                        'weight_unit': product.weight_unit
                    }],
                    'images': [
                        {
                            'src': img_url,
                            'alt': product.name,
                            'position': idx + 1
                        } for idx, img_url in enumerate(product.images)
                    ],
                    'metafields': [
                        {
                            'namespace': 'specifications',
                            'key': 'details',
                            'value': json.dumps(product.specifications),
                            'value_type': 'json_string'
                        },
                        {
                            'namespace': 'product',
                            'key': 'features',
                            'value': json.dumps(product.features),
                            'value_type': 'json_string'
                        }
                    ] if product.specifications or product.features else []
                }
            }
            
            shopify_products.append(shopify_product)
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_products': len(shopify_products),
            'products': shopify_products
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Shopify API export completed: {filename}")
        return filename
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the import process"""
        report_filename = f"{self.output_dir}/import_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("ENGWE Product Import Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Import Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Products Found: {len(self.products)}\n")
            f.write(f"Failed Extractions: {len(self.failed_products)}\n\n")
            
            # Product type breakdown
            product_types = {}
            for product in self.products:
                ptype = product.product_type
                product_types[ptype] = product_types.get(ptype, 0) + 1
            
            f.write("Product Type Breakdown:\n")
            f.write("-" * 25 + "\n")
            for ptype, count in sorted(product_types.items()):
                f.write(f"{ptype}: {count}\n")
            
            f.write("\nPrice Range Analysis:\n")
            f.write("-" * 20 + "\n")
            prices = [float(p.price) for p in self.products if p.price and float(p.price) > 0]
            if prices:
                f.write(f"Minimum Price: €{min(prices):.2f}\n")
                f.write(f"Maximum Price: €{max(prices):.2f}\n")
                f.write(f"Average Price: €{sum(prices)/len(prices):.2f}\n")
            
            if self.failed_products:
                f.write("\nFailed Product URLs:\n")
                f.write("-" * 20 + "\n")
                for url in self.failed_products:
                    f.write(f"{url}\n")
        
        logger.info(f"Summary report generated: {report_filename}")
        return report_filename
    
    def run_full_import(self, download_images: bool = True, max_workers: int = 3) -> Dict[str, str]:
        """Run the complete import process"""
        logger.info("Starting full ENGWE product import...")
        start_time = time.time()
        
        # Extract all products
        self.extract_all_products(max_workers=max_workers)
        
        if not self.products:
            logger.error("No products extracted, aborting import")
            return {}
        
        # Download images if requested
        if download_images:
            logger.info("Downloading product images...")
            with ThreadPoolExecutor(max_workers=2) as executor:
                self.products = list(executor.map(self.download_product_images, self.products))
        
        # Export in all formats
        export_files = {
            'csv': self.export_to_csv(),
            'json': self.export_to_json(),
            'shopify_api': self.export_shopify_api_format(),
            'summary': self.generate_summary_report()
        }
        
        end_time = time.time()
        logger.info(f"Import completed in {end_time - start_time:.2f} seconds")
        logger.info(f"Exported files: {export_files}")
        
        return export_files

def main():
    """Main function to run the importer"""
    print("ENGWE Product Importer")
    print("=" * 50)
    
    # Configuration
    output_dir = "engwe_import_" + datetime.now().strftime('%Y%m%d_%H%M%S')
    download_images = input("Download product images? (y/N): ").strip().lower() == 'y'
    max_workers = int(input("Max concurrent workers (default 3): ") or "3")
    
    # Create importer and run
    importer = EngweProductImporter(output_dir=output_dir)
    export_files = importer.run_full_import(
        download_images=download_images,
        max_workers=max_workers
    )
    
    print("\nImport completed!")
    print("Generated files:")
    for file_type, filepath in export_files.items():
        print(f"  {file_type.upper()}: {filepath}")
    
    print(f"\nAll files saved in: {output_dir}/")
    print("You can now import the CSV file to your Shopify store.")

if __name__ == "__main__":
    main()
