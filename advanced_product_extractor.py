#!/usr/bin/env python3
"""
Advanced Product Extractor for Engwe.com
This module provides detailed product information extraction using web scraping techniques.
"""

import requests
import re
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class AdvancedProductExtractor:
    """Advanced extractor for detailed product information"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_product_json(self, html_content: str) -> Dict[str, Any]:
        """Extract product data from JSON-LD or other structured data"""
        product_data = {}
        
        try:
            # Look for JSON-LD structured data
            json_ld_match = re.search(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([^<]+)</script>', html_content, re.IGNORECASE)
            if json_ld_match:
                json_data = json.loads(json_ld_match.group(1))
                if isinstance(json_data, dict) and json_data.get('@type') == 'Product':
                    product_data.update({
                        'name': json_data.get('name', ''),
                        'description': json_data.get('description', ''),
                        'price': self._extract_price_from_offer(json_data.get('offers', {})),
                        'images': self._extract_images_from_json(json_data),
                        'brand': json_data.get('brand', {}).get('name', 'ENGWE')
                    })
            
            # Look for Shopify product JSON
            shopify_match = re.search(r'window\.ShopifyAnalytics.*?product.*?({.*?}).*?;', html_content, re.DOTALL)
            if shopify_match:
                try:
                    shopify_data = json.loads(shopify_match.group(1))
                    product_data.update(self._parse_shopify_data(shopify_data))
                except:
                    pass
            
            # Look for product configuration in JavaScript
            config_match = re.search(r'var\s+product\s*=\s*({.*?});', html_content, re.DOTALL)
            if config_match:
                try:
                    config_data = json.loads(config_match.group(1))
                    product_data.update(self._parse_config_data(config_data))
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Error extracting JSON data: {e}")
        
        return product_data
    
    def extract_specifications(self, html_content: str) -> Dict[str, Any]:
        """Extract detailed specifications from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        specifications = {}
        
        # Look for specification tables
        spec_tables = soup.find_all('table', class_=re.compile(r'spec|specification|detail', re.I))
        for table in spec_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specifications[key] = value
        
        # Look for specification lists
        spec_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'spec|specification|feature', re.I))
        for spec_list in spec_lists:
            items = spec_list.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if ':' in text:
                    key, value = text.split(':', 1)
                    specifications[key.strip()] = value.strip()
        
        # Extract from description sections
        desc_sections = soup.find_all(['div', 'section'], class_=re.compile(r'description|detail|spec', re.I))
        for section in desc_sections:
            # Look for key-value pairs in text
            text = section.get_text()
            matches = re.findall(r'([A-Za-z][^:]+?):\s*([^\n\r]+)', text)
            for key, value in matches:
                key = key.strip()
                value = value.strip()
                if len(key) < 50 and len(value) < 200:  # Reasonable length limits
                    specifications[key] = value
        
        return specifications
    
    def extract_features(self, html_content: str) -> List[str]:
        """Extract product features and highlights"""
        soup = BeautifulSoup(html_content, 'html.parser')
        features = []
        
        # Look for feature lists
        feature_sections = soup.find_all(['ul', 'ol'], class_=re.compile(r'feature|highlight|benefit', re.I))
        for section in feature_sections:
            items = section.find_all('li')
            for item in items:
                feature = item.get_text(strip=True)
                if feature and len(feature) > 5:  # Filter out very short items
                    features.append(feature)
        
        # Look for feature cards or boxes
        feature_cards = soup.find_all(['div', 'section'], class_=re.compile(r'feature|highlight|card', re.I))
        for card in feature_cards:
            title = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if title:
                feature_text = title.get_text(strip=True)
                if feature_text and len(feature_text) > 5:
                    features.append(feature_text)
        
        # Look for bullet points or checkmarks
        bullet_items = soup.find_all(['li', 'div'], string=re.compile(r'^[•✓✔]'))
        for item in bullet_items:
            feature = item.get_text(strip=True).lstrip('•✓✔ ')
            if feature and len(feature) > 5:
                features.append(feature)
        
        return list(set(features))  # Remove duplicates
    
    def extract_variants(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract product variants (colors, sizes, etc.)"""
        variants = []
        
        try:
            # Look for variant data in JavaScript
            variant_match = re.search(r'variants?["\']?\s*:\s*(\[.*?\])', html_content, re.DOTALL)
            if variant_match:
                variant_data = json.loads(variant_match.group(1))
                for variant in variant_data:
                    if isinstance(variant, dict):
                        variants.append({
                            'name': variant.get('title', variant.get('name', '')),
                            'price': str(variant.get('price', 0)),
                            'sku': variant.get('sku', ''),
                            'available': variant.get('available', True),
                            'inventory_quantity': variant.get('inventory_quantity', 0)
                        })
            
            # Look for color/size options
            soup = BeautifulSoup(html_content, 'html.parser')
            option_selects = soup.find_all('select', {'name': re.compile(r'option|variant|color|size', re.I)})
            for select in option_selects:
                options = select.find_all('option')
                for option in options:
                    if option.get('value') and option.get_text(strip=True):
                        variants.append({
                            'name': option.get_text(strip=True),
                            'value': option.get('value'),
                            'available': not option.has_attr('disabled')
                        })
                        
        except Exception as e:
            logger.warning(f"Error extracting variants: {e}")
        
        return variants
    
    def extract_all_images(self, html_content: str, base_url: str = "https://engwe.com") -> List[str]:
        """Extract all product images from the page"""
        images = []
        
        # Extract from img tags
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src:
                # Filter for product images (usually contain 'files' or 'products')
                if any(keyword in src.lower() for keyword in ['files', 'products', 'cdn.shopify']):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = base_url + src
                    
                    # Get high resolution version
                    if '?v=' in src:
                        src = re.sub(r'\?v=[^&]*', '', src)
                    if '&width=' in src:
                        src = re.sub(r'&width=[^&]*', '', src)
                    
                    images.append(src)
        
        # Extract from CSS background images
        style_matches = re.findall(r'background-image\s*:\s*url\(["\']?([^"\')]+)["\']?\)', html_content)
        for match in style_matches:
            if any(keyword in match.lower() for keyword in ['files', 'products', 'cdn.shopify']):
                if match.startswith('//'):
                    match = 'https:' + match
                elif match.startswith('/'):
                    match = base_url + match
                images.append(match)
        
        # Remove duplicates and return
        return list(set(images))
    
    def _extract_price_from_offer(self, offer_data: Dict) -> str:
        """Extract price from JSON-LD offer data"""
        if isinstance(offer_data, list):
            offer_data = offer_data[0] if offer_data else {}
        
        price = offer_data.get('price', '0')
        return str(price).replace(',', '')
    
    def _extract_images_from_json(self, json_data: Dict) -> List[str]:
        """Extract images from JSON-LD data"""
        images = []
        
        # Single image
        if 'image' in json_data:
            image_data = json_data['image']
            if isinstance(image_data, str):
                images.append(image_data)
            elif isinstance(image_data, list):
                images.extend(image_data)
            elif isinstance(image_data, dict):
                url = image_data.get('url') or image_data.get('@id')
                if url:
                    images.append(url)
        
        return images
    
    def _parse_shopify_data(self, shopify_data: Dict) -> Dict[str, Any]:
        """Parse Shopify analytics data"""
        return {
            'shopify_id': shopify_data.get('id', ''),
            'vendor': shopify_data.get('vendor', ''),
            'product_type': shopify_data.get('type', ''),
            'price': str(shopify_data.get('price', 0))
        }
    
    def _parse_config_data(self, config_data: Dict) -> Dict[str, Any]:
        """Parse product configuration data"""
        return {
            'handle': config_data.get('handle', ''),
            'title': config_data.get('title', ''),
            'vendor': config_data.get('vendor', ''),
            'product_type': config_data.get('type', ''),
            'tags': config_data.get('tags', []),
            'variants': config_data.get('variants', [])
        }
    
    def extract_complete_product(self, product_url: str) -> Dict[str, Any]:
        """Extract complete product information"""
        try:
            response = self.session.get(product_url)
            response.raise_for_status()
            html_content = response.text
            
            # Extract all data
            product_data = self.extract_product_json(html_content)
            product_data['specifications'] = self.extract_specifications(html_content)
            product_data['features'] = self.extract_features(html_content)
            product_data['variants'] = self.extract_variants(html_content)
            product_data['all_images'] = self.extract_all_images(html_content)
            product_data['url'] = product_url
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error extracting complete product data from {product_url}: {e}")
            return {}
