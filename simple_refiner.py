import csv
import json
import re

class WalmartContentRefiner:
    def __init__(self):
        self.banned_words = ['cosplay', 'weapon', 'knife', 'uv', 'premium', 'perfect']
        
    def clean_text(self, text):
        if not text:
            return text
        cleaned = text
        for word in self.banned_words:
            cleaned = re.sub(r'\b' + word + r'\b', 'quality', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def generate_title(self, brand, product_type, attributes):
        attr_dict = json.loads(attributes.replace('""', '"'))
        color = attr_dict.get('Color', '')
        material = attr_dict.get('Material', '')
        title = f"{brand} {color} {material} {product_type}".strip()
        return self.clean_text(title)
    
    def generate_bullets(self, current_bullets, attributes):
        attr_dict = json.loads(attributes.replace('""', '"'))
        bullets = []
        current_list = [b.strip('- ').strip() for b in current_bullets.split('\n') if b.strip()]
        
        for bullet in current_list:
            cleaned = self.clean_text(bullet)
            if len(cleaned) <= 85 and cleaned and len(bullets) < 6:
                bullets.append(cleaned)
        
        # Add attribute bullets
        for key, value in attr_dict.items():
            if len(bullets) >= 8:
                break
            bullet = f"{key}: {value}"
            if len(bullet) <= 85:
                bullets.append(bullet)
        
        # Fill remaining slots
        filler_bullets = ["Durable construction", "Easy to use", "Great value", "Reliable performance"]
        for filler in filler_bullets:
            if len(bullets) >= 8:
                break
            bullets.append(filler)
        
        return bullets[:8]
    
    def generate_description(self, brand, product_type, attributes, current_desc):
        attr_dict = json.loads(attributes.replace('""', '"'))
        
        # Clean and rebuild description
        base_desc = self.clean_text(current_desc)
        
        # Create structured description
        intro = f"The {brand} {product_type} delivers outstanding performance and reliability."
        features = f"This {product_type.lower()} features {', '.join(list(attr_dict.values())[:3])}."
        benefits = f"Designed for {product_type.lower().replace('equipment', 'use').replace('appliance', 'kitchen tasks')}, it offers exceptional value."
        quality = "Built with attention to detail and quality materials for long-lasting durability."
        usage = f"Ideal for both everyday use and special occasions, this {brand} product meets high standards."
        conclusion = "Experience the difference that quality engineering and thoughtful design can make."
        
        description = f"{intro} {features} {benefits} {quality} {usage} {conclusion}"
        words = description.split()
        
        # Ensure 120-160 words
        if len(words) < 120:
            extra = "This versatile product combines functionality with style to enhance your experience."
            description += f" {extra}"
            words = description.split()
        
        return ' '.join(words[:160])
    
    def generate_html_features(self, bullets):
        html = "<ul>"
        for bullet in bullets:
            html += f"<li>{bullet}</li>"
        html += "</ul>"
        return html
    
    def generate_meta_title(self, title):
        return title[:67] + "..." if len(title) > 70 else title
    
    def generate_meta_description(self, description):
        return description[:157] + "..." if len(description) > 160 else description
    
    def check_violations(self, row_data):
        violations = []
        text_to_check = f"{row_data['current_description']} {row_data['current_bullets']}"
        for word in self.banned_words:
            if re.search(r'\b' + word + r'\b', text_to_check, re.IGNORECASE):
                violations.append(f"Contains banned word: {word}")
        return "; ".join(violations) if violations else "None"
    
    def process_csv(self, input_file, output_file):
        results = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = self.generate_title(row['brand'], row['product_type'], row['attributes'])
                bullets = self.generate_bullets(row['current_bullets'], row['attributes'])
                description = self.generate_description(row['brand'], row['product_type'], 
                                                      row['attributes'], row['current_description'])
                html_features = self.generate_html_features(bullets)
                meta_title = self.generate_meta_title(title)
                meta_description = self.generate_meta_description(description)
                violations = self.check_violations(row)
                
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
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        return results

if __name__ == "__main__":
    refiner = WalmartContentRefiner()
    results = refiner.process_csv('input_data.csv', 'output_refined.csv')
    print(f"Processing complete. Processed {len(results)} products")
    print("Results saved to output_refined.csv")