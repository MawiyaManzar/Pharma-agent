#!/usr/bin/env python3
"""
Setup diagnostic script for Pharma Agentic AI.
Checks if all dependencies are installed and configuration is correct.
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    print("=" * 60)
    print("Checking Dependencies...")
    print("=" * 60)
    
    # Map package names to their import names
    required_packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "langgraph": "langgraph",
        "langchain": "langchain",
        "langchain_google_genai": "langchain_google_genai",
        "streamlit": "streamlit",
        "reportlab": "reportlab",
        "openpyxl": "openpyxl",
        "pandas": "pandas",
        "python-dotenv": "dotenv",  # python-dotenv package imports as dotenv
        "pydantic": "pydantic",
        "requests": "requests",
    }
    
    missing = []
    installed = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            installed.append(package_name)
            print(f"✓ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"✗ {package_name} - MISSING")
    
    print()
    if missing:
        print(f"❌ {len(missing)} package(s) missing:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nTo install all dependencies, run:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print(f"✅ All {len(installed)} required packages are installed!")
        return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n" + "=" * 60)
    print("Checking Configuration...")
    print("=" * 60)
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("\nCreate a .env file with the following content:")
        print("   GOOGLE_API_KEY=your_google_api_key_here")
        print("   API_URL=http://localhost:8000")
        return False
    
    print("✓ .env file exists")
    
    # Load and check .env
    from dotenv import load_dotenv
    load_dotenv()
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    if not google_api_key:
        print("❌ GOOGLE_API_KEY not set in .env file")
        return False
    
    print(f"✓ GOOGLE_API_KEY is set (length: {len(google_api_key)} characters)")
    print(f"✓ API_URL is set to: {api_url}")
    
    return True

def check_imports():
    """Check if critical modules can be imported."""
    print("\n" + "=" * 60)
    print("Checking Module Imports...")
    print("=" * 60)
    
    try:
        from src.workflows import DrugRepurposingWorkflow
        print("✓ DrugRepurposingWorkflow")
    except Exception as e:
        print(f"✗ DrugRepurposingWorkflow - {e}")
        return False
    
    try:
        from src.reports import ReportGenerator
        print("✓ ReportGenerator")
    except Exception as e:
        print(f"✗ ReportGenerator - {e}")
        return False
    
    try:
        from src.api.main import app
        print("✓ FastAPI app")
    except Exception as e:
        print(f"✗ FastAPI app - {e}")
        return False
    
    return True

def main():
    """Run all checks."""
    print("\n" + "=" * 60)
    print("Pharma Agentic AI - Setup Diagnostic")
    print("=" * 60 + "\n")
    
    deps_ok = check_dependencies()
    env_ok = check_env_file()
    imports_ok = check_imports()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if deps_ok and env_ok and imports_ok:
        print("✅ All checks passed! You're ready to run the application.")
        print("\nTo start:")
        print("  1. Backend:  uvicorn src.api.main:app --reload --port 8000")
        print("  2. Frontend: streamlit run src/ui/app.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        if not deps_ok:
            print("\nFix: pip install -r requirements.txt")
        if not env_ok:
            print("\nFix: Create .env file with GOOGLE_API_KEY")
        return 1

if __name__ == "__main__":
    sys.exit(main())

