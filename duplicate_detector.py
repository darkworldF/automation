#!/usr/bin/env python3
"""
Duplicate Detection Script for ENGWE Products
Compares imported products with existing products to avoid duplicates
"""

import json
import csv
import difflib
from typing import List, Dict, Set, Tuple
import os
import argparse

class DuplicateDetector:
    """Detects duplicate products between import data and existing store data"""
    
    def __init__(self):
        self.similarity_threshold = 0.8  # 80% similarity for name matching
        
    def load_import_data(self, import_file: str) -> List[Dict]:
        """Load products from import file (JSON or CSV)"""
        products = []
        
        if import_file.endswith('.json'):
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'products' in data:
                    products = data['products']
                else:
                    products = data
                    
        elif import_file.endswith('.csv'):
            with open(import_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
        
        return products
    
    def load_existing_products(self, existing_file: str) -> List[Dict]:
        """Load existing products from your store export"""
        return self.load_import_data(existing_file)
    
    def normalize_name(self, name: str) -> str:
        """Normalize product name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase and remove common variations
        name = name.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['engwe', 'electric', 'e-bike', 'ebike', 'bike']
        suffixes = ['electric bike', 'e-bike', 'ebike']
        
        for prefix in prefixes:
            if name.startswith(prefix + ' '):
                name = name[len(prefix):].strip()
        
        for suffix in suffixes:
            if name.endswith(' ' + suffix):
                name = name[:-len(suffix)].strip()
        
        # Remove extra spaces and special characters
        import re
        name = re.sub(r'[^a-z0-9\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two product names"""
        norm_name1 = self.normalize_name(name1)
        norm_name2 = self.normalize_name(name2)
        
        if not norm_name1 or not norm_name2:
            return 0.0
        
        return difflib.SequenceMatcher(None, norm_name1, norm_name2).ratio()
    
    def extract_model_number(self, name: str) -> str:
        """Extract model number from product name"""
        import re
        
        # Look for patterns like M1, M20, EP-2, Engine Pro 3.0, etc.
        patterns = [
            r'\b([A-Z]+[0-9]+(?:\.[0-9]+)?)\b',  # M1, M20, etc.
            r'\b(EP-[0-9]+)\b',  # EP-2
            r'\b(Engine\s+Pro\s+[0-9.]+)\b',  # Engine Pro 3.0
            r'\b(L[0-9]+)\b',  # L20
            r'\b(P[0-9]+)\b',  # P20
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return ""
    
    def detect_duplicates(self, import_products: List[Dict], existing_products: List[Dict]) -> Dict:
        """Detect duplicate products between import and existing data"""
        duplicates = []
        exact_matches = []
        potential_duplicates = []
        unique_imports = []
        
        # Create lookup sets for existing products
        existing_names = {self.normalize_name(p.get('name', p.get('Title', ''))) for p in existing_products}
        existing_skus = {p.get('sku', p.get('Variant SKU', '')) for p in existing_products if p.get('sku', p.get('Variant SKU', ''))}
        existing_handles = {p.get('handle', p.get('Handle', '')) for p in existing_products if p.get('handle', p.get('Handle', ''))}
        
        for import_product in import_products:
            import_name = import_product.get('name', import_product.get('Title', ''))
            import_sku = import_product.get('sku', import_product.get('Variant SKU', ''))
            import_handle = import_product.get('handle', import_product.get('Handle', ''))
            
            is_duplicate = False
            match_info = {
                'import_product': import_product,
                'match_type': None,
                'matched_product': None,
                'similarity_score': 0.0
            }
            
            # Check for exact SKU match
            if import_sku and import_sku in existing_skus:
                match_info['match_type'] = 'exact_sku'
                exact_matches.append(match_info)
                is_duplicate = True
                continue
            
            # Check for exact handle match
            if import_handle and import_handle in existing_handles:
                match_info['match_type'] = 'exact_handle'
                exact_matches.append(match_info)
                is_duplicate = True
                continue
            
            # Check for name similarity
            best_similarity = 0.0
            best_match = None
            
            for existing_product in existing_products:
                existing_name = existing_product.get('name', existing_product.get('Title', ''))
                similarity = self.calculate_name_similarity(import_name, existing_name)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = existing_product
            
            if best_similarity >= self.similarity_threshold:
                match_info['match_type'] = 'name_similarity'
                match_info['matched_product'] = best_match
                match_info['similarity_score'] = best_similarity
                potential_duplicates.append(match_info)
                is_duplicate = True
            
            # Check model number match
            if not is_duplicate:
                import_model = self.extract_model_number(import_name)
                if import_model:
                    for existing_product in existing_products:
                        existing_name = existing_product.get('name', existing_product.get('Title', ''))
                        existing_model = self.extract_model_number(existing_name)
                        
                        if import_model == existing_model:
                            match_info['match_type'] = 'model_number'
                            match_info['matched_product'] = existing_product
                            potential_duplicates.append(match_info)
                            is_duplicate = True
                            break
            
            if not is_duplicate:
                unique_imports.append(import_product)
        
        return {
            'exact_matches': exact_matches,
            'potential_duplicates': potential_duplicates,
            'unique_imports': unique_imports,
            'summary': {
                'total_import_products': len(import_products),
                'total_existing_products': len(existing_products),
                'exact_matches_count': len(exact_matches),
                'potential_duplicates_count': len(potential_duplicates),
                'unique_imports_count': len(unique_imports)
            }
        }
    
    def generate_report(self, duplicate_analysis: Dict, output_file: str = None) -> str:
        """Generate a detailed duplicate detection report"""
        if output_file is None:
            output_file = 'duplicate_detection_report.txt'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ENGWE Product Duplicate Detection Report\n")
            f.write("=" * 50 + "\n\n")
            
            summary = duplicate_analysis['summary']
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total products to import: {summary['total_import_products']}\n")
            f.write(f"Total existing products: {summary['total_existing_products']}\n")
            f.write(f"Exact matches (duplicates): {summary['exact_matches_count']}\n")
            f.write(f"Potential duplicates: {summary['potential_duplicates_count']}\n")
            f.write(f"Unique products to import: {summary['unique_imports_count']}\n\n")
            
            # Exact matches
            if duplicate_analysis['exact_matches']:
                f.write("EXACT MATCHES (Skip These)\n")
                f.write("-" * 30 + "\n")
                for match in duplicate_analysis['exact_matches']:
                    product = match['import_product']
                    name = product.get('name', product.get('Title', 'Unknown'))
                    f.write(f"- {name} ({match['match_type']})\n")
                f.write("\n")
            
            # Potential duplicates
            if duplicate_analysis['potential_duplicates']:
                f.write("POTENTIAL DUPLICATES (Review These)\n")
                f.write("-" * 40 + "\n")
                for match in duplicate_analysis['potential_duplicates']:
                    import_product = match['import_product']
                    import_name = import_product.get('name', import_product.get('Title', 'Unknown'))
                    
                    f.write(f"Import: {import_name}\n")
                    
                    if match['matched_product']:
                        existing_name = match['matched_product'].get('name', match['matched_product'].get('Title', 'Unknown'))
                        f.write(f"Existing: {existing_name}\n")
                    
                    f.write(f"Match Type: {match['match_type']}\n")
                    
                    if match['similarity_score'] > 0:
                        f.write(f"Similarity: {match['similarity_score']:.2%}\n")
                    
                    f.write("\n")
            
            # Unique products
            f.write("UNIQUE PRODUCTS (Safe to Import)\n")
            f.write("-" * 35 + "\n")
            for product in duplicate_analysis['unique_imports']:
                name = product.get('name', product.get('Title', 'Unknown'))
                f.write(f"- {name}\n")
        
        return output_file
    
    def create_filtered_import_file(self, duplicate_analysis: Dict, original_file: str, output_file: str = None) -> str:
        """Create a new import file with duplicates removed"""
        if output_file is None:
            base, ext = os.path.splitext(original_file)
            output_file = f"{base}_filtered{ext}"
        
        unique_products = duplicate_analysis['unique_imports']
        
        if original_file.endswith('.json'):
            # Create filtered JSON
            export_data = {
                'filtered_date': '2025-10-18',
                'original_count': duplicate_analysis['summary']['total_import_products'],
                'filtered_count': len(unique_products),
                'removed_duplicates': duplicate_analysis['summary']['exact_matches_count'] + duplicate_analysis['summary']['potential_duplicates_count'],
                'products': unique_products
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        elif original_file.endswith('.csv'):
            # Create filtered CSV
            if unique_products:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=unique_products[0].keys())
                    writer.writeheader()
                    writer.writerows(unique_products)
        
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Detect duplicate products between import and existing data')
    parser.add_argument('import_file', help='Path to import file (JSON or CSV)')
    parser.add_argument('existing_file', help='Path to existing products file (JSON or CSV)')
    parser.add_argument('--output-report', help='Output file for duplicate report')
    parser.add_argument('--output-filtered', help='Output file for filtered import data')
    parser.add_argument('--threshold', type=float, default=0.8, help='Similarity threshold (0.0-1.0)')
    
    args = parser.parse_args()
    
    detector = DuplicateDetector()
    detector.similarity_threshold = args.threshold
    
    print("Loading import data...")
    import_products = detector.load_import_data(args.import_file)
    print(f"Loaded {len(import_products)} products to import")
    
    print("Loading existing products...")
    existing_products = detector.load_existing_products(args.existing_file)
    print(f"Loaded {len(existing_products)} existing products")
    
    print("Detecting duplicates...")
    duplicate_analysis = detector.detect_duplicates(import_products, existing_products)
    
    print("\nDuplicate Detection Results:")
    print(f"- Exact matches: {duplicate_analysis['summary']['exact_matches_count']}")
    print(f"- Potential duplicates: {duplicate_analysis['summary']['potential_duplicates_count']}")
    print(f"- Unique products: {duplicate_analysis['summary']['unique_imports_count']}")
    
    # Generate report
    report_file = detector.generate_report(duplicate_analysis, args.output_report)
    print(f"\nDetailed report saved to: {report_file}")
    
    # Create filtered import file
    if duplicate_analysis['summary']['unique_imports_count'] < duplicate_analysis['summary']['total_import_products']:
        filtered_file = detector.create_filtered_import_file(duplicate_analysis, args.import_file, args.output_filtered)
        print(f"Filtered import file saved to: {filtered_file}")
        print("Use this file for importing to avoid duplicates.")
    else:
        print("No duplicates found - original file can be imported as-is.")

if __name__ == "__main__":
    main()
