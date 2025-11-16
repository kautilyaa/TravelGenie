#!/usr/bin/env python3
"""
Test script to check which Claude models are available with the current API key.
"""

import os
import sys
from anthropic import Anthropic

def test_models():
    """Test various Claude model names to see which ones work."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        return
    
    client = Anthropic(api_key=api_key)
    
    # List of model names to test
    models_to_test = [
        "claude-sonnet-4-20250514",
        "claude-opus-4-1-20250805",
        "claude-3-5-sonnet-20241022",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
        "claude-3-5-haiku-20241022",
        "claude-3-5-opus-20241022",
    ]
    
    print("Testing Claude models with your API key...")
    print("=" * 60)
    
    working_models = []
    failed_models = []
    
    for model in models_to_test:
        try:
            print(f"\nTesting: {model}...", end=" ", flush=True)
            response = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print("✅ WORKS")
            working_models.append(model)
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not_found" in error_msg.lower():
                print("❌ NOT FOUND (404)")
                failed_models.append((model, "404 Not Found"))
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                print("❌ UNAUTHORIZED (401)")
                failed_models.append((model, "401 Unauthorized"))
            else:
                print(f"❌ ERROR: {error_msg[:50]}")
                failed_models.append((model, error_msg[:100]))
    
    print("\n" + "=" * 60)
    print("\nSUMMARY:")
    print(f"✅ Working models ({len(working_models)}):")
    for model in working_models:
        print(f"   - {model}")
    
    if failed_models:
        print(f"\n❌ Failed models ({len(failed_models)}):")
        for model, error in failed_models[:5]:  # Show first 5
            print(f"   - {model}: {error}")
    
    if working_models:
        print(f"\n💡 RECOMMENDATION: Use '{working_models[0]}' as your default model")
    else:
        print("\n⚠️  WARNING: No working models found!")
        print("   Please check:")
        print("   1. Your API key is valid")
        print("   2. Your account has access to Claude models")
        print("   3. Your API key has the necessary permissions")

if __name__ == "__main__":
    test_models()

