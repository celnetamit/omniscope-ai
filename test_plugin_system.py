"""
Test script for Plugin System
Verifies basic functionality of the plugin system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all plugin system modules can be imported"""
    print("Testing imports...")
    
    try:
        from backend_db.plugin_manager import PluginManagerService, Plugin
        print("✓ Plugin Manager imported")
        
        from backend_db.plugin_sandbox import PluginSandbox
        print("✓ Plugin Sandbox imported")
        
        from backend_db.plugin_security import SecurityScanner
        print("✓ Security Scanner imported")
        
        from backend_db.plugin_api import PluginAPIGateway, PluginInterface
        print("✓ Plugin API imported")
        
        from backend_db.plugin_marketplace import MarketplaceService
        print("✓ Marketplace Service imported")
        
        from backend_db.plugin_version import PluginVersionManager, SemanticVersion
        print("✓ Version Manager imported")
        
        from backend_db.plugin_sdk import PluginSDK, PluginTemplate
        print("✓ Plugin SDK imported")
        
        from modules.plugin_module import router
        print("✓ Plugin Module imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_semantic_version():
    """Test semantic version parsing and comparison"""
    print("\nTesting semantic versioning...")
    
    try:
        from backend_db.plugin_version import SemanticVersion
        
        # Test parsing
        v1 = SemanticVersion("1.2.3")
        assert v1.major == 1
        assert v1.minor == 2
        assert v1.patch == 3
        print("✓ Version parsing works")
        
        # Test comparison
        v2 = SemanticVersion("1.2.4")
        assert v2 > v1
        print("✓ Version comparison works")
        
        # Test prerelease
        v3 = SemanticVersion("1.2.3-alpha.1")
        assert v3 < v1
        print("✓ Prerelease version works")
        
        # Test compatibility
        v4 = SemanticVersion("1.3.0")
        assert v1.is_compatible_with(v4)
        print("✓ Compatibility check works")
        
        v5 = SemanticVersion("2.0.0")
        assert not v1.is_compatible_with(v5)
        print("✓ Breaking change detection works")
        
        return True
    except Exception as e:
        print(f"✗ Semantic version test failed: {e}")
        return False


def test_plugin_api():
    """Test plugin API gateway"""
    print("\nTesting plugin API...")
    
    try:
        from backend_db.plugin_api import PluginAPIGateway, PluginInput, PluginOutput
        
        gateway = PluginAPIGateway()
        
        # Test extension points
        assert len(gateway.EXTENSION_POINTS) == 10
        print(f"✓ Extension points defined: {len(gateway.EXTENSION_POINTS)}")
        
        # Test input validation
        plugin_input = PluginInput(
            data={"test": "data"},
            parameters={"param1": "value1"}
        )
        print("✓ PluginInput creation works")
        
        # Test output
        plugin_output = PluginOutput(
            data={"result": "success"},
            logs=["Test log"],
            warnings=[],
            errors=[]
        )
        print("✓ PluginOutput creation works")
        
        return True
    except Exception as e:
        print(f"✗ Plugin API test failed: {e}")
        return False


def test_security_scanner():
    """Test security scanner patterns"""
    print("\nTesting security scanner...")
    
    try:
        from backend_db.plugin_security import SecurityScanner
        
        # Check patterns are defined
        assert 'python' in SecurityScanner.DANGEROUS_PATTERNS
        assert 'r' in SecurityScanner.DANGEROUS_PATTERNS
        print(f"✓ Security patterns defined for Python and R")
        
        # Check suspicious imports
        assert 'python' in SecurityScanner.SUSPICIOUS_IMPORTS
        assert 'r' in SecurityScanner.SUSPICIOUS_IMPORTS
        print(f"✓ Suspicious imports defined")
        
        return True
    except Exception as e:
        print(f"✗ Security scanner test failed: {e}")
        return False


def test_plugin_sdk():
    """Test plugin SDK template generation"""
    print("\nTesting plugin SDK...")
    
    try:
        from backend_db.plugin_sdk import PluginTemplate
        
        # Check templates exist
        assert PluginTemplate.PYTHON_TEMPLATE
        assert PluginTemplate.R_TEMPLATE
        assert PluginTemplate.MANIFEST_TEMPLATE
        assert PluginTemplate.README_TEMPLATE
        print("✓ Plugin templates defined")
        
        return True
    except Exception as e:
        print(f"✗ Plugin SDK test failed: {e}")
        return False


def test_example_plugins():
    """Test example plugins exist"""
    print("\nTesting example plugins...")
    
    try:
        # Check Python example
        python_plugin = "plugins/examples/data_normalizer/data_normalizer.py"
        python_manifest = "plugins/examples/data_normalizer/manifest.json"
        
        if os.path.exists(python_plugin) and os.path.exists(python_manifest):
            print("✓ Python example plugin exists")
        else:
            print("✗ Python example plugin missing")
            return False
        
        # Check R example
        r_plugin = "plugins/examples/correlation_analyzer/correlation_analyzer.R"
        r_manifest = "plugins/examples/correlation_analyzer/manifest.json"
        
        if os.path.exists(r_plugin) and os.path.exists(r_manifest):
            print("✓ R example plugin exists")
        else:
            print("✗ R example plugin missing")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Example plugins test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Plugin System Verification")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Semantic Version", test_semantic_version),
        ("Plugin API", test_plugin_api),
        ("Security Scanner", test_security_scanner),
        ("Plugin SDK", test_plugin_sdk),
        ("Example Plugins", test_example_plugins)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Plugin system is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
