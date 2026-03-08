#!/usr/bin/env python3
"""
Test script for TextLeaf application
Tests basic functionality without requiring MoviePy
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        from config import Config
        assert Config.PAGE_DURATION == 0.5
        assert Config.DEFAULT_FPS == 30
        assert len(Config.RESOLUTIONS) > 0
        print("✓ Configuration OK")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False


def test_image_generator():
    """Test image generator"""
    print("\nTesting image generator...")
    try:
        from image_generator import ImageGenerator
        
        # Create generator
        gen = ImageGenerator(resolution='9:16')
        print(f"  - Image size: {gen.width}x{gen.height}")
        
        # Generate single page
        page = gen.generate_page("Test Text", 1, add_watermark=False)
        print(f"  - Generated page: {page.size}")
        
        assert page.size == (1080, 1920)
        print("✓ Image generator OK")
        return True
    except Exception as e:
        print(f"✗ Image generator failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_video_calculator():
    """Test video calculations"""
    print("\nTesting video calculations...")
    try:
        from video_generator import VideoGenerator
        
        info = VideoGenerator.calculate_video_info(10)
        print(f"  - 10 seconds = {info['num_pages']} pages")
        
        assert info['num_pages'] == 20
        assert info['duration'] == 10
        assert info['page_duration'] == 0.5
        
        print("✓ Video calculator OK")
        return True
    except Exception as e:
        print(f"✗ Video calculator failed: {e}")
        return False


def test_oxapay_service():
    """Test OxaPay service structure"""
    print("\nTesting OxaPay service...")
    try:
        from oxapay_service import OxaPayService
        
        service = OxaPayService()
        networks = service.get_supported_networks()
        print(f"  - Supported networks: {len(networks)}")
        
        assert len(networks) > 0
        print("✓ OxaPay service OK")
        return True
    except Exception as e:
        print(f"✗ OxaPay service failed: {e}")
        return False


def test_flask_app():
    """Test Flask application structure"""
    print("\nTesting Flask application...")
    try:
        from app import app
        
        # Check routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        print(f"  - Registered routes: {len(routes)}")
        
        essential_routes = ['/', '/api/generate', '/api/calculate']
        for route in essential_routes:
            assert route in routes, f"Missing route: {route}"
        
        print("✓ Flask application OK")
        return True
    except Exception as e:
        print(f"✗ Flask application failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("TextLeaf Application Tests")
    print("=" * 50)
    
    tests = [
        test_config,
        test_image_generator,
        test_video_calculator,
        test_oxapay_service,
        test_flask_app
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 50)
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
