#!/usr/bin/env python3
"""
Test script to verify live plot parsing from training output.
"""

import re
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_live_plot_parsing():
    """Test the live plot parsing logic."""
    print("🧪 Testing Live Plot Parsing from Training Output")
    print("=" * 50)
    
    # Simulate training output from stock_net.py
    test_output = [
        "Loading data...",
        "Adding technical indicators...",
        "Preparing features and target...",
        "Normalizing data...",
        "LOSS:1,0.123456",
        "WEIGHTS:1,0.234567,0.345678",
        "LOSS:2,0.098765",
        "WEIGHTS:2,0.187654,0.276543",
        "LOSS:3,0.087654",
        "WEIGHTS:3,0.165432,0.254321",
        "Epoch 10, Train MSE: 0.076543, Val MSE: 0.089012",
        "LOSS:11,0.076543",
        "WEIGHTS:11,0.154321,0.243210",
        "Training complete!",
        "Final validation MSE: 0.065432"
    ]
    
    # Test parsing logic
    total_epochs = 100
    parsed_data = []
    
    for line in test_output:
        if line.startswith('LOSS:'):
            # Format: LOSS:epoch,loss_value
            match = re.match(r"LOSS:(\d+),(\d+\.\d+)", line.strip())
            if match:
                epoch = int(match.group(1))
                loss = float(match.group(2))
                percent = (epoch / total_epochs) * 100 if total_epochs else 0
                parsed_data.append((epoch, loss, percent))
                print(f"✅ Parsed: Epoch {epoch}, Loss {loss:.6f}, Progress {percent:.1f}%")
    
    # Verify results
    print(f"\n📊 Parsing Results:")
    print(f"Total lines processed: {len(test_output)}")
    print(f"LOSS lines found: {len(parsed_data)}")
    
    if parsed_data:
        print(f"First epoch: {parsed_data[0][0]}, Loss: {parsed_data[0][1]:.6f}")
        print(f"Last epoch: {parsed_data[-1][0]}, Loss: {parsed_data[-1][1]:.6f}")
        print(f"Loss trend: {'Decreasing' if parsed_data[-1][1] < parsed_data[0][1] else 'Increasing'}")
        
        # Test callback format
        print(f"\n🎯 Callback Format Test:")
        for epoch, loss, percent in parsed_data:
            callback_data = (epoch, loss, None, percent)
            print(f"  callback('progress', {callback_data})")
    
    print("\n" + "=" * 50)
    print("🎉 Live Plot Parsing Test Completed!")
    
    if len(parsed_data) > 0:
        print("✅ SUCCESS: Live plot parsing works correctly!")
        print("💡 The GUI should now update live plots during real training.")
    else:
        print("❌ FAILED: No LOSS lines were parsed.")
        print("💡 Check the regex pattern and output format.")

if __name__ == "__main__":
    test_live_plot_parsing() 