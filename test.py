print("Starting test...")

try:
    from flask import Flask
    print("✓ Flask imported")
    
    from models import db, User
    print("✓ Models imported")
    
    from datetime import datetime
    print("✓ Datetime imported")
    
    print("\nAll imports successful! The issue is elsewhere.")
    
except Exception as e:
    print(f"✗ Error: {e}")
