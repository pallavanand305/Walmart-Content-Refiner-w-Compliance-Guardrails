def test_always_passes():
    """Basic test to ensure test runner works"""
    assert True

def test_banned_words_list():
    """Test that banned words list is properly defined"""
    from simple_refiner import WalmartContentRefiner
    refiner = WalmartContentRefiner()
    expected_banned_words = ['cosplay', 'weapon', 'knife', 'uv', 'premium', 'perfect']
    assert refiner.banned_words == expected_banned_words

def test_csv_files_exist():
    """Test that required CSV files exist"""
    import os
    assert os.path.exists('input_data.csv')
    assert os.path.exists('output_refined.csv')