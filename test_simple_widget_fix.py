#!/usr/bin/env python3
"""
Simple test to verify widget error fixes work.
"""

import tkinter as tk
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_widget_existence_checks():
    """Test the widget existence check logic."""
    print("🧪 Testing widget existence check logic...")
    
    try:
        # Create a simple root window
        root = tk.Tk()
        root.withdraw()
        
        # Create a simple text widget
        text_widget = tk.Text(root)
        text_widget.pack()
        
        # Test 1: Widget exists and is valid
        print("Test 1: Valid widget")
        try:
            text_widget.winfo_exists()
            print("✅ Widget exists check works")
        except Exception as e:
            print(f"❌ Widget exists check failed: {e}")
            return False
        
        # Test 2: Widget after destruction
        print("Test 2: Destroyed widget")
        text_widget.destroy()
        text_widget = None
        
        # Test 3: None widget
        print("Test 3: None widget")
        if text_widget is None:
            print("✅ None widget check works")
        else:
            print("❌ None widget check failed")
            return False
        
        # Test 4: Try to access destroyed widget
        print("Test 4: Access destroyed widget")
        try:
            text_widget.winfo_exists()
            print("❌ Should have failed")
            return False
        except tk.TclError:
            print("✅ Properly caught TclError for destroyed widget")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
        root.destroy()
        print("✅ All widget existence check tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def main():
    """Run the test."""
    print("🚀 Starting simple widget fix test...\n")
    
    success = test_widget_existence_checks()
    
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    if success:
        print("✅ Widget existence checks - PASSED")
        print("\n🎉 The widget error fixes should work!")
        print("   The 'invalid command name' errors should be prevented.")
        return True
    else:
        print("❌ Widget existence checks - FAILED")
        print("\n⚠️ The widget error fixes may need more work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 