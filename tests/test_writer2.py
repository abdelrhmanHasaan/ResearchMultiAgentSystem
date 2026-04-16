#!/usr/bin/env python3
"""
Simple Test for writer2.py
Run: python -m tests.test_simple
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.writer2 import sanitize_text_for_pdf, EnhancedWriterAgent

print("=" * 50)
print("TEST 1: Basic Sanitization")
print("=" * 50)

tests = [
    ("AIndriven", "AI-driven"),
    ("expertnlevel", "expert-level"),
    ("humanninnthenloop", "human-in-the-loop"),
    ("precision =0.78vs.0.52", "precision = 0.78 vs. 0.52"),
    ("30nday realntime", "30-day real-time"),
    ("≈12%", "~12%"),
    ("ALF Research Report", "AI Research Report"),
]

all_pass = True
for inp, expected in tests:
    result = sanitize_text_for_pdf(inp)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_pass = False
    print(f"{status} '{inp}'")
    print(f"   → '{result}'")

print(f"\nSanitization: {'PASS ✓' if all_pass else 'FAIL ✗'}")

print("\n" + "=" * 50)
print("TEST 2: Report Generation")
print("=" * 50)

try:
    agent = EnhancedWriterAgent()
    result = agent.run("AI in Healthcare", options={"detail_level": "brief"})
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ PDF: {result['pdf']}")
        
        # Check for artifacts
        text = result['report'][:1000]
        bad_patterns = ['AIndriven', 'expertnlevel', '30nday', '≈', '国']
        found = [b for b in bad_patterns if b in text]
        
        if found:
            print(f"❌ Artifacts found: {found}")
        else:
            print("✅ No artifacts detected!")
            
except Exception as e:
    print(f"❌ {e}")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)