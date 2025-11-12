#!/usr/bin/env python3
"""
Test script to validate the login modal implementation without running the GUI.
Tests imports, class structure, and basic functionality.
"""
import sys
import os

# Add the src/app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from pages.login_modal import LoginModal
        print("✓ LoginModal import successful")
        return True
    except ImportError as e:
        print(f"✗ LoginModal import failed: {e}")
        return False

def test_class_structure():
    """Test the basic structure of the LoginModal class."""
    try:
        from pages.login_modal import LoginModal
        import inspect
        
        # Check class exists and has required methods
        methods = [method for method in dir(LoginModal) if not method.startswith('_')]
        required_methods = ['_create_modal', '_build_content', '_on_login_click', 'close_modal']
        
        missing_methods = [method for method in required_methods if method not in methods]
        if missing_methods:
            print(f"✗ Missing required methods: {missing_methods}")
            return False
        else:
            print("✓ LoginModal has all required methods")
            
        # Check method signatures
        constructor_sig = inspect.signature(LoginModal.__init__)
        expected_params = ['parent', 'on_login', 'on_register', 'on_forgot_password', 'on_mock_session']
        actual_params = list(constructor_sig.parameters.keys())
        
        missing_params = [param for param in expected_params if param not in actual_params]
        if missing_params:
            print(f"✗ Missing constructor parameters: {missing_params}")
            return False
        else:
            print("✓ LoginModal constructor has correct parameters")
            
        return True
    except Exception as e:
        print(f"✗ Class structure test failed: {e}")
        return False

def test_integration():
    """Test integration with main app."""
    try:
        # Test that app.py imports LoginModal
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        if 'from pages.login_modal import LoginModal' in app_content:
            print("✓ app.py imports LoginModal")
        else:
            print("✗ app.py does not import LoginModal")
            return False
            
        if 'show_login_modal' in app_content:
            print("✓ app.py has show_login_modal method")
        else:
            print("✗ app.py missing show_login_modal method")
            return False
            
        if '_handle_login_success' in app_content:
            print("✓ app.py has login success handler")
        else:
            print("✗ app.py missing login success handler")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def test_theme_colors():
    """Test that required theme colors are defined."""
    try:
        # Check theme tokens have link colors
        with open('ui/theme_tokens.py', 'r') as f:
            tokens_content = f.read()
            
        if 'LINK_PRIMARY = ""' in tokens_content:
            print("✓ Theme tokens define LINK_PRIMARY")
        else:
            print("✗ Theme tokens missing LINK_PRIMARY")
            return False
            
        if 'LINK_HOVER = ""' in tokens_content:
            print("✓ Theme tokens define LINK_HOVER")
        else:
            print("✗ Theme tokens missing LINK_HOVER")
            return False
            
        # Check theme manager has the colors
        with open('ui/theme_manager.py', 'r') as f:
            manager_content = f.read()
            
        if '"LINK_PRIMARY": Palette.PRIMARY,' in manager_content:
            print("✓ Theme manager defines LINK_PRIMARY for both themes")
        else:
            print("✗ Theme manager missing LINK_PRIMARY definitions")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Theme colors test failed: {e}")
        return False

def test_modal_features():
    """Test that modal has all required features."""
    try:
        with open('pages/login_modal.py', 'r') as f:
            modal_content = f.read()
            
        # Check for required features
        features = {
            '25% screen dimensions': 'modal_width = max(screen_width // 4, 400)',
            'Centered positioning': 'pos_x = (screen_width - modal_width) // 2',
            'Device Name field': 'Preferred Device Name',
            'Password field': 'Password',
            'Register link': 'Register',
            'Forgot Password link': 'Forgot Password',
            'Mock User Session': 'Mock User Session',
            'Background overlay': 'attributes(\'-alpha\', 0.5)',
            'Modal behavior': 'grab_set()',
            'Accessibility (Enter key)': 'bind(\'<Return>\'',
            'Accessibility (Escape key)': 'bind(\'<Escape>\'',
            'Responsive design': 'modal_width = max(screen_width // 4, 400)',
        }
        
        all_found = True
        for feature, pattern in features.items():
            if pattern in modal_content:
                print(f"✓ Modal has {feature}")
            else:
                print(f"✗ Modal missing {feature}")
                all_found = False
                
        return all_found
    except Exception as e:
        print(f"✗ Modal features test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Login Modal Implementation")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Class Structure Test", test_class_structure),
        ("Integration Test", test_integration),
        ("Theme Colors Test", test_theme_colors),
        ("Modal Features Test", test_modal_features),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Login modal implementation is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())