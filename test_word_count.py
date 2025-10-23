from simple_refiner import WalmartContentRefiner

# Test word count
refiner = WalmartContentRefiner()
brand = "TestBrand"
product_type = "Test Product"
attributes = '{"Color": "Blue", "Material": "Plastic"}'
current_desc = "This is a test description"

description = refiner.generate_description(brand, product_type, attributes, current_desc)
word_count = len(description.split())

print(f"Generated description word count: {word_count}")
print(f"Description: {description}")
print(f"Test passes: {120 <= word_count <= 160}")