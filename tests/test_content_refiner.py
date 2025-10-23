import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_refiner import WalmartContentRefiner

class TestWalmartContentRefiner(unittest.TestCase):
    
    def setUp(self):
        self.refiner = WalmartContentRefiner()
    
    def test_banned_words_removal(self):
        """Test that banned words are properly removed"""
        text = "This is a perfect premium weapon with UV protection"
        cleaned = self.refiner.clean_text(text)
        for word in self.refiner.banned_words:
            self.assertNotIn(word.lower(), cleaned.lower())
    
    def test_title_generation(self):
        """Test title generation with brand and attributes"""
        brand = "TestBrand"
        product_type = "Kitchen Appliance"
        attributes = '{"Color": "Red", "Material": "Steel"}'
        title = self.refiner.generate_title(brand, product_type, attributes)
        self.assertIn(brand, title)
        self.assertIn("Red", title)
        self.assertIn("Steel", title)
    
    def test_bullet_count(self):
        """Test that exactly 8 bullets are generated"""
        current_bullets = "- Feature 1\n- Feature 2\n- Feature 3"
        attributes = '{"Color": "Blue", "Material": "Plastic"}'
        bullets = self.refiner.generate_bullets(current_bullets, attributes)
        self.assertEqual(len(bullets), 8)
    
    def test_bullet_length_limit(self):
        """Test that bullets are within 85 character limit"""
        current_bullets = "- Feature 1\n- Feature 2"
        attributes = '{"Color": "Blue"}'
        bullets = self.refiner.generate_bullets(current_bullets, attributes)
        for bullet in bullets:
            self.assertLessEqual(len(bullet), 85)
    
    def test_description_word_count(self):
        """Test that description is between 120-160 words"""
        brand = "TestBrand"
        product_type = "Test Product"
        attributes = '{"Color": "Blue", "Material": "Plastic"}'
        current_desc = "This is a test description"
        description = self.refiner.generate_description(brand, product_type, attributes, current_desc)
        word_count = len(description.split())
        self.assertGreaterEqual(word_count, 120)
        self.assertLessEqual(word_count, 160)
    
    def test_meta_title_length(self):
        """Test that meta title is within 70 character limit"""
        title = "Very Long Product Title That Might Exceed The Seventy Character Limit"
        meta_title = self.refiner.generate_meta_title(title)
        self.assertLessEqual(len(meta_title), 70)
    
    def test_meta_description_length(self):
        """Test that meta description is within 160 character limit"""
        long_desc = "This is a very long description " * 10
        meta_desc = self.refiner.generate_meta_description(long_desc)
        self.assertLessEqual(len(meta_desc), 160)
    
    def test_html_features_format(self):
        """Test that HTML features are properly formatted"""
        bullets = ["Feature 1", "Feature 2", "Feature 3"]
        html = self.refiner.generate_html_features(bullets)
        self.assertTrue(html.startswith("<ul>"))
        self.assertTrue(html.endswith("</ul>"))
        self.assertIn("<li>Feature 1</li>", html)

if __name__ == '__main__':
    unittest.main()