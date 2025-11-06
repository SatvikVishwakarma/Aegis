#!/usr/bin/env python3
"""
Test script for Agent Package Builder
Validates that all components are working correctly
"""
import os
import sys
from pathlib import Path

def check_template_files():
    """Verify all required template files exist"""
    print("🔍 Checking template files...")
    
    template_dir = Path(__file__).parent / "Server" / "agent-template"
    
    if not template_dir.exists():
        print("❌ ERROR: Template directory not found!")
        return False
    
    required_files = [
        "AegisAgent.exe",
        "appsettings.template.json",
        "INSTALL.template.ps1",
        "UNINSTALL.template.ps1",
        "README.template.txt"
    ]
    
    all_exist = True
    for filename in required_files:
        file_path = template_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {filename} ({size:,} bytes)")
        else:
            print(f"  ❌ {filename} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_python_modules():
    """Verify Python modules can be imported"""
    print("\n🔍 Checking Python modules...")
    
    sys.path.insert(0, str(Path(__file__).parent / "Server"))
    
    modules = [
        ("agent_builder", "AgentPackageBuilder"),
        ("agent_routes", "router"),
    ]
    
    all_imported = True
    for module_name, obj_name in modules:
        try:
            module = __import__(module_name)
            if hasattr(module, obj_name):
                print(f"  ✅ {module_name}.{obj_name}")
            else:
                print(f"  ❌ {module_name} - missing {obj_name}")
                all_imported = False
        except Exception as e:
            print(f"  ❌ {module_name} - import error: {e}")
            all_imported = False
    
    return all_imported


def check_dashboard_files():
    """Verify Dashboard files exist"""
    print("\n🔍 Checking Dashboard files...")
    
    dashboard_dir = Path(__file__).parent / "Dashboard"
    
    files = [
        "src/app/dashboard/agents/page.tsx",
        "src/app/dashboard/layout.tsx",
    ]
    
    all_exist = True
    for filepath in files:
        file_path = dashboard_dir / filepath
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {filepath} ({size:,} bytes)")
        else:
            print(f"  ❌ {filepath} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_template_placeholders():
    """Verify template files contain required placeholders"""
    print("\n🔍 Checking template placeholders...")
    
    template_dir = Path(__file__).parent / "Server" / "agent-template"
    
    checks = [
        ("appsettings.template.json", ["{{SERVER_URL}}", "{{API_KEY}}", "{{GROUP}}"]),
        ("INSTALL.template.ps1", ["{{GROUP}}", "{{SERVER_URL}}"]),
        ("README.template.txt", ["{{GROUP}}", "{{SERVER_URL}}"]),
    ]
    
    all_valid = True
    for filename, placeholders in checks:
        file_path = template_dir / filename
        if not file_path.exists():
            print(f"  ❌ {filename} - NOT FOUND")
            all_valid = False
            continue
        
        content = file_path.read_text(encoding='utf-8')
        missing = [p for p in placeholders if p not in content]
        
        if missing:
            print(f"  ❌ {filename} - missing placeholders: {', '.join(missing)}")
            all_valid = False
        else:
            print(f"  ✅ {filename} - all placeholders present")
    
    return all_valid


def main():
    """Run all checks"""
    print("=" * 60)
    print("Agent Package Builder - Implementation Validation")
    print("=" * 60)
    
    checks = [
        ("Template Files", check_template_files),
        ("Python Modules", check_python_modules),
        ("Dashboard Files", check_dashboard_files),
        ("Template Placeholders", check_template_placeholders),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! Implementation is ready.")
        return 0
    else:
        print("❌ Some checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
