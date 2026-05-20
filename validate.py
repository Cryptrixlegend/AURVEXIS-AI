"""
Quick validation script to check if all modules load correctly.
Run: python validate.py
"""

import sys
import os

print("=" * 60)
print("AURVEXIS AI - Module Validation")
print("=" * 60)

# Add project to path
sys.path.insert(0, '/workspaces/AURVEXIS-AI')

errors = []

print("\n✓ Checking imports...")

try:
    print("  • Importing utils...", end=" ")
    from aurvexis.utils.security import hash_password, new_salt, validate_password
    from aurvexis.utils.helpers import escape_html, sanitize_input
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("utils", str(e)))

try:
    print("  • Importing database...", end=" ")
    from aurvexis.database import Database
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("database", str(e)))

try:
    print("  • Importing auth...", end=" ")
    from aurvexis.auth.auth import Auth
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("auth", str(e)))

try:
    print("  • Importing media/YouTube...", end=" ")
    from aurvexis.media import YouTubeService
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("media", str(e)))

try:
    print("  • Importing tools...", end=" ")
    from aurvexis.tools import ToolRouter
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("tools", str(e)))

try:
    print("  • Importing UI components...", end=" ")
    from aurvexis.ui import get_premium_css, get_animations
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("ui", str(e)))

try:
    print("  • Importing services (note: requires GROQ key)...", end=" ")
    from aurvexis.services import WebSearchService
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("services", str(e)))

try:
    print("  • Importing memory engine...", end=" ")
    from aurvexis.memory import MemoryEngine
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("memory", str(e)))

print("\n✓ Testing functionality...")

try:
    print("  • Testing password hashing...", end=" ")
    salt = new_salt()
    hashed = hash_password("test_password", salt)
    assert len(hashed) == 64
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("hash_test", str(e)))

try:
    print("  • Testing input sanitization...", end=" ")
    dirty = "<script>alert('xss')</script> test"
    clean = sanitize_input(dirty)
    assert "<script>" not in clean
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("sanitize_test", str(e)))

try:
    print("  • Testing tool detection...", end=" ")
    intent = ToolRouter.detect_intent("play some funk music")
    assert intent.name == "YouTube Music"
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("tool_detect_test", str(e)))

try:
    print("  • Testing CSS generation...", end=" ")
    css = get_premium_css()
    assert "glass-card" in css
    assert len(css) > 1000
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    errors.append(("css_test", str(e)))

print("\n" + "=" * 60)

if errors:
    print(f"❌ {len(errors)} errors found:\n")
    for module, error in errors:
        print(f"  {module}: {error}")
    sys.exit(1)
else:
    print("✅ All modules validated successfully!")
    print("\nYou can now run:")
    print("  streamlit run app.py")
    sys.exit(0)
