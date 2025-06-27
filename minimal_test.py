#!/usr/bin/env python3
"""
Minimal test to identify the exact error.
"""

import sys
import os

def test_basic_imports():
    """Test basic imports."""
    try:
        print("Testing basic imports...")
        import tkinter as tk
        print("✓ tkinter works")
        return True
    except Exception as e:
        print(f"❌ tkinter error: {e}")
        return False 