#!/usr/bin/env python3
"""
Two-Step Product Import Tool
Step 1: Fetch and Preview Products
Step 2: Upload to Shopify
"""

import os
import json
import requests
from datetime import datetime
from engwe_product_importer import EngweProductImporter
import webbrowser

class TwoStepImporter:
    def __init__(self):
        self.preview_file = "products_preview.json"
        self.preview_html = "products_preview.html"
        self.fetched_products = []
        
    def step1_fetch_and_preview(self):
        """Step 1: Fetch all products and create preview"""
        print("🔍 STEP 1: Fetching products from engwe.com...")
        print("=" * 50)
        
        # Initialize the importer
        importer = EngweProductImporter()
        
        # Fetch all products
        print("📡 Scanning engwe.com for products...")
        product_urls = importer.get_all_product_urls()
        print(f"✅ Found {len(product_urls)} products")
        
        print("\n📥 Downloading product details...")
        products = []
        for i, url in enumerate(product_urls, 1):
            print(f"  → Processing {i}/{len(product_urls)}: {url.split('/')[-1]}")
            product_data = importer.scrape_product_data(url)
            if product_data:
                products.append(product_data)
        
        self.fetched_products = products
        
        # Save to JSON for step 2
        with open(self.preview_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        # Create HTML preview
        self.create_html_preview(products)
        
        print(f"\n✅ SUCCESS! Fetched {len(products)} products")
        print(f"📁 Data saved to: {self.preview_file}")
        print(f"🌐 Preview created: {self.preview_html}")
        print("\n🔍 Opening preview in your browser...")
        
        # Open preview in browser
        webbrowser.open(f"file://{os.path.abspath(self.preview_html)}")
        
        print("\n" + "=" * 50)
        print("🎯 READY FOR STEP 2!")
        print("Review the products in your browser, then run:")
        print("python two_step_importer.py --step2")
        print("=" * 50)
        
        return len(products)
    
    def step2_upload_to_shopify(self):
        """Step 2: Upload fetched products to Shopify"""
        print("🚀 STEP 2: Uploading products to Shopify...")
        print("=" * 50)
        
        # Check if preview data exists
        if not os.path.exists(self.preview_file):
            print("❌ ERROR: No preview data found!")
            print("Please run Step 1 first: python two_step_importer.py --step1")
            return False
        
        # Load previewed products
        with open(self.preview_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"📤 Found {len(products)} products ready for upload")
        
        # Import shopify API importer
        try:
            from shopify_api_importer import ShopifyAPIImporter
            import configparser
            
            # Load config
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            # Create API importer
            api_importer = ShopifyAPIImporter(config)
            
            # Upload products
            print("\n🔄 Starting upload to Shopify...")
            success_count = 0
            
            for i, product in enumerate(products, 1):
                print(f"  → Uploading {i}/{len(products)}: {product.get('title', 'Unknown')}")
                
                if api_importer.create_product(product):
                    success_count += 1
                    print(f"    ✅ Success")
                else:
                    print(f"    ❌ Failed")
            
            print(f"\n🎉 UPLOAD COMPLETE!")
            print(f"✅ Successfully uploaded: {success_count}/{len(products)} products")
            print(f"❌ Failed uploads: {len(products) - success_count}")
            
            if success_count > 0:
                print("\n📋 Next steps:")
                print("1. Log into your Shopify admin")
                print("2. Go to Products section")
                print("3. Review and publish imported products")
            
            return True
            
        except ImportError:
            print("❌ ERROR: Shopify API importer not found!")
            print("Please make sure shopify_api_importer.py exists")
            return False
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False
    
    def create_html_preview(self, products):
        """Create an HTML preview of all products"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Engwe Products Preview - Ready for Import</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats {{
            background: white;
            padding: 1.5rem;
            margin: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 1rem;
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            display: block;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 1rem;
            margin-top: 0.5rem;
        }}
        
        .action-panel {{
            background: #e8f5e8;
            border: 2px solid #4caf50;
            border-radius: 12px;
            padding: 2rem;
            margin: 2rem;
            text-align: center;
        }}
        
        .action-panel h2 {{
            color: #2e7d32;
            margin-bottom: 1rem;
        }}
        
        .action-panel p {{
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            color: #4caf50;
        }}
        
        .action-panel code {{
            background: #2e7d32;
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1.1rem;
            display: inline-block;
            font-family: 'Courier New', monospace;
        }}
        
        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
            padding: 2rem;
        }}
        
        .product-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .product-image {{
            width: 100%;
            height: 250px;
            object-fit: cover;
            background: #f5f5f5;
        }}
        
        .product-info {{
            padding: 1.5rem;
        }}
        
        .product-title {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            color: #333;
            line-height: 1.4;
        }}
        
        .product-price {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #e91e63;
            margin-bottom: 1rem;
        }}
        
        .product-description {{
            color: #666;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .product-meta {{
            border-top: 1px solid #eee;
            padding-top: 1rem;
            font-size: 0.9rem;
            color: #888;
        }}
        
        .variants-info {{
            background: #f8f9fa;
            padding: 0.8rem;
            border-radius: 6px;
            margin-top: 1rem;
        }}
        
        .variants-info strong {{
            color: #667eea;
        }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stats {{
                flex-direction: column;
            }}
            
            .products-grid {{
                grid-template-columns: 1fr;
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Products Preview</h1>
        <p>All products fetched from engwe.com • Ready for import to nlebike.com</p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <span class="stat-number">{len(products)}</span>
            <div class="stat-label">Total Products</div>
        </div>
        <div class="stat-item">
            <span class="stat-number">{sum(len(p.get('variants', [])) for p in products)}</span>
            <div class="stat-label">Total Variants</div>
        </div>
        <div class="stat-item">
            <span class="stat-number">{sum(len(p.get('images', [])) for p in products)}</span>
            <div class="stat-label">Total Images</div>
        </div>
        <div class="stat-item">
            <span class="stat-number">{len([p for p in products if p.get('price', 0) > 0])}</span>
            <div class="stat-label">With Pricing</div>
        </div>
    </div>
    
    <div class="action-panel">
        <h2>🚀 Ready for Step 2!</h2>
        <p>Review the products below, then run the upload command:</p>
        <code>python two_step_importer.py --step2</code>
    </div>
    
    <div class="products-grid">
"""
        
        for product in products:
            title = product.get('title', 'Unknown Product')
            price = product.get('price', 0)
            description = product.get('description', 'No description available')[:200] + "..."
            images = product.get('images', [])
            variants = product.get('variants', [])
            
            # Get first image or placeholder
            image_url = images[0] if images else "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='250' height='250' viewBox='0 0 250 250'%3E%3Crect width='250' height='250' fill='%23f0f0f0'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-family='Arial' font-size='14' fill='%23999'%3ENo Image%3C/text%3E%3C/svg%3E"
            
            html_content += f"""
        <div class="product-card">
            <img src="{image_url}" alt="{title}" class="product-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'250\' height=\'250\' viewBox=\'0 0 250 250\'%3E%3Crect width=\'250\' height=\'250\' fill=\'%23f0f0f0\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' dy=\'.3em\' font-family=\'Arial\' font-size=\'14\' fill=\'%23999\'%3ENo Image%3C/text%3E%3C/svg%3E'">
            <div class="product-info">
                <div class="product-title">{title}</div>
                <div class="product-price">${price}</div>
                <div class="product-description">{description}</div>
                <div class="variants-info">
                    <strong>Variants:</strong> {len(variants)} available<br>
                    <strong>Images:</strong> {len(images)} photos
                </div>
            </div>
        </div>
"""
        
        html_content += """
    </div>
    
    <div class="footer">
        <p>🤖 Generated by Engwe Product Importer</p>
        <p>Ready to upload to nlebike.com Shopify store</p>
    </div>
</body>
</html>
"""
        
        with open(self.preview_html, 'w', encoding='utf-8') as f:
            f.write(html_content)

def main():
    import sys
    
    importer = TwoStepImporter()
    
    if '--step2' in sys.argv:
        importer.step2_upload_to_shopify()
    else:
        # Default to step 1
        importer.step1_fetch_and_preview()

if __name__ == "__main__":
    main()