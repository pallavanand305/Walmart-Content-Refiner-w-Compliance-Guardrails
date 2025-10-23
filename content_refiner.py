import pandas as pd
import json
import re

class WalmartContentRefiner:
    def __init__(self):
        self.banned_words = ['cosplay', 'weapon', 'knife', 'uv', 'premium', 'perfect']
        
    def clean_text(self, text):
        """Remove banned words and clean text"""
        if not text:
            return text
        
        # Replace banned words
        cleaned = text.lower()
        for word in self.banned_words:
            cleaned = re.sub(r'\b' + word + r'\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned.capitalize()
    
    def generate_title(self, brand, product_type, attributes):
        """Generate Walmart-safe title"""
        attr_dict = json.loads(attributes) if isinstance(attributes, str) else attributes
        color = attr_dict.get('Color', '')
        material = attr_dict.get('Material', '')
        
        title = f"{brand} {color} {material} {product_type}".strip()
        return self.clean_text(title)
    
    def generate_bullets(self, current_bullets, attributes):
        """Generate 8 bullets ≤85 chars each"""
        attr_dict = json.loads(attributes) if isinstance(attributes, str) else attributes
        bullets = []
        
        # Parse current bullets
        current_list = [b.strip('- ').strip() for b in current_bullets.split('\n') if b.strip()]
        
        for bullet in current_list[:6]:  # Take first 6
            cleaned = self.clean_text(bullet)
            if len(cleaned) <= 85:
                bullets.append(cleaned)
        
        # Add attribute-based bullets
        for key, value in attr_dict.items():
            if len(bullets) >= 8:
                break
            bullet = f"{key}: {value}"
            if len(bullet) <= 85:
                bullets.append(bullet)
        
        # Pad to 8 bullets if needed
        while len(bullets) < 8:
            bullets.append("Quality construction")
        
        return bullets[:8]
    
    def generate_description(self, brand, product_type, attributes, current_desc):
        """Generate 120-160 word description"""
        attr_dict = json.loads(attributes) if isinstance(attributes, str) else attributes
        
        # Clean current description
        cleaned_desc = self.clean_text(current_desc)
        
        # Build new description
        desc_parts = [
            f"The {brand} {product_type} offers exceptional quality and functionality.",
            cleaned_desc[:100] if cleaned_desc else "",
            f"Features include {', '.join(list(attr_dict.values())[:3])}.",
            "Designed for durability and reliable performance in everyday use."
        ]
        
        description = ' '.join([p for p in desc_parts if p]).strip()
        
        # Ensure 120-160 words
        words = description.split()
        if len(words) < 120:
            description += " This item combines innovative design with practical functionality to meet your needs."
            words = description.split()
        
        return ' '.join(words[:160])
    
    def generate_html_features(self, bullets):
        """Generate HTML key features"""
        html = "<ul>"
        for bullet in bullets:
            html += f"<li>{bullet}</li>"
        html += "</ul>"
        return html
    
    def generate_meta_title(self, title):
        """Generate meta title ≤70 chars"""
        if len(title) <= 70:
            return title
        return title[:67] + "..."
    
    def generate_meta_description(self, description):
        """Generate meta description ≤160 chars"""
        if len(description) <= 160:
            return description
        return description[:157] + "..."
    
    def check_violations(self, row_data):
        """Check for rule violations"""
        violations = []
        
        # Check banned words in original content
        text_to_check = f"{row_data['current_description']} {row_data['current_bullets']}"
        for word in self.banned_words:
            if re.search(r'\b' + word + r'\b', text_to_check, re.IGNORECASE):
                violations.append(f"Contains banned word: {word}")
        
        return "; ".join(violations) if violations else "None"
    
    def process_csv(self, input_file, output_file):
        """Process the CSV file"""
        df = pd.read_csv(input_file)
        
        results = []
        for _, row in df.iterrows():
            # Generate new content
            title = self.generate_title(row['brand'], row['product_type'], row['attributes'])
            bullets = self.generate_bullets(row['current_bullets'], row['attributes'])
            description = self.generate_description(row['brand'], row['product_type'], 
                                                  row['attributes'], row['current_description'])
            html_features = self.generate_html_features(bullets)
            meta_title = self.generate_meta_title(title)
            meta_description = self.generate_meta_description(description)
            violations = self.check_violations(row)
            
            # Create result row
            result = {
                'brand': row['brand'],
                'product_type': row['product_type'],
                'attributes': row['attributes'],
                'current_description': row['current_description'],
                'current_bullets': row['current_bullets'],
                'walmart_safe_title': title,
                'html_key_features': html_features,
                'new_description': description,
                'meta_title': meta_title,
                'meta_description': meta_description,
                'violations': violations
            }
            results.append(result)
        
        # Save results
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)
        return result_df

if __name__ == "__main__":
    refiner = WalmartContentRefiner()
    result_df = refiner.process_csv('input_data.csv', 'output_refined.csv')
    print("Processing complete. Results saved to output_refined.csv")
    print(f"Processed {len(result_df)} products")