"""
Setup Verification Script for mc-sz-integration Branch

This script verifies that all components are properly installed and configured.
Run this before using the trading agents system.
"""

import sys
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_imports():
    """Verify all required packages are installed"""
    print_header("Checking Required Packages")

    packages = {
        'langchain_core': 'langchain-core',
        'langchain_google_genai': 'langchain-google-genai',
        'langgraph': 'langgraph',
        'pydantic': 'pydantic',
        'requests': 'requests',
        'yfinance': 'yfinance',
        'pandas': 'pandas',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'dotenv': 'python-dotenv',
    }

    missing = []
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[FAIL] {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\n[WARNING] Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    else:
        print("\n[OK] All required packages installed!")
        return True

def check_env_file():
    """Verify .env file exists and has required keys"""
    print_header("Checking Environment Configuration")

    env_file = Path(__file__).parent / ".env"

    if not env_file.exists():
        print("[FAIL] .env file not found!")
        print("   Create .env file from .env.example:")
        print("   cp .env.example .env")
        return False

    print("[OK] .env file exists")

    # Check for required keys
    with open(env_file) as f:
        env_content = f.read()

    required_keys = {
        'GOOGLE_GENAI_API_KEY': 'Required for LLM (Google Gemini)',
        'NEWSAPI_KEY': 'Required for news data (get free at newsapi.org)',
    }

    optional_keys = {
        'FMP_API_KEY': 'Optional - Financial Modeling Prep (250/day free)',
        'ALPHA_VANTAGE_API_KEY': 'Optional - Backup news source',
    }

    missing_required = []
    for key, desc in required_keys.items():
        if key in env_content and f"{key}=your_" not in env_content:
            print(f"[OK] {key} - {desc}")
        else:
            print(f"[FAIL] {key} - MISSING - {desc}")
            missing_required.append(key)

    for key, desc in optional_keys.items():
        if key in env_content and f"{key}=your_" not in env_content:
            print(f"[OK] {key} - {desc}")
        else:
            print(f"[WARNING]  {key} - Optional - {desc}")

    if missing_required:
        print(f"\n[WARNING]  Missing required API keys: {', '.join(missing_required)}")
        print("\nGet your API keys:")
        print("  - Google Gemini: https://makersuite.google.com/app/apikey")
        print("  - NewsAPI: https://newsapi.org/register")
        return False
    else:
        print("\n[OK] All required API keys configured!")
        return True

def check_project_structure():
    """Verify all required files and folders exist"""
    print_header("Checking Project Structure")

    required_paths = {
        'agent/news_analyst.py': 'SZ\'s news analyst',
        'agent/market_analyst_v2.py': 'Technical analysis agent',
        'agent/fundamentals_analyst_v2.py': 'Financial analysis agent',
        'agent/bull_debater_v2.py': 'Bull case builder',
        'agent/bear_debater_v2.py': 'Bear case builder',
        'agent/supervisor_v2.py': 'Risk-tiered supervisor',
        'tools/news_tools_newsapi.py': 'NewsAPI integration',
        'tools/analyst_tools_fmp.py': 'Technical tools (FMP)',
        'tools/fundamental_tools_fmp.py': 'Financial tools (FMP)',
        'ui/web_app.py': 'FastAPI web server',
        'ui/static/dashboard.html': 'Web dashboard UI',
        'ui/static/app.js': 'Frontend logic',
        'ui/static/styles.css': 'Dashboard styles',
        'ui/cache_manager.py': 'Cache management',
        'config.py': 'Configuration',
        'state.py': 'State schema',
        'trading_graph.py': 'LangGraph workflow',
        'main.py': 'CLI entry point',
    }

    project_root = Path(__file__).parent
    all_exist = True

    for path, desc in required_paths.items():
        full_path = project_root / path
        if full_path.exists():
            print(f"[OK] {path} - {desc}")
        else:
            print(f"[FAIL] {path} - MISSING - {desc}")
            all_exist = False

    if all_exist:
        print("\n[OK] All required files present!")
    else:
        print("\n[WARNING]  Some files are missing - check branch checkout")

    return all_exist

def test_imports():
    """Test that core modules can be imported"""
    print_header("Testing Module Imports")

    try:
        print("Testing trading_graph import...")
        from trading_graph import create_trading_graph
        print("[OK] trading_graph imports successfully")

        print("Testing config import...")
        import config
        print("[OK] config imports successfully")

        print("Testing state import...")
        import state
        print("[OK] state imports successfully")

        print("\n[OK] All core modules import successfully!")
        return True

    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("  MC-SZ Integration Branch - Setup Verification")
    print("=" * 60)

    checks = [
        ("Package Installation", check_imports),
        ("Environment Configuration", check_env_file),
        ("Project Structure", check_project_structure),
        ("Module Imports", test_imports),
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))

    # Final summary
    print_header("Verification Summary")

    all_passed = all(result for _, result in results)

    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status} - {name}")

    if all_passed:
        print("\n*** All checks passed! System is ready to use. ***")
        print("\nNext steps:")
        print("  1. CLI: python main.py --ticker MSFT")
        print("  2. Web UI: cd ui && python web_app.py")
        print("     Then open: http://localhost:8000")
        return 0
    else:
        print("\n*** Some checks failed. Please fix the issues above. ***")
        return 1

if __name__ == "__main__":
    exit(main())
