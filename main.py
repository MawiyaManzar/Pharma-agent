"""
Main entry point for the Pharma Agentic AI system.
This is a placeholder that will be replaced by the Streamlit UI.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point"""
    print("Pharma Agentic AI - Drug Repurposing Intelligence Platform")
    print("Version: 0.1.0")
    print("\nProject structure initialized successfully!")
    print("Run 'streamlit run src/ui/app.py' to start the UI")
    return 0

if __name__ == "__main__":
    sys.exit(main())

