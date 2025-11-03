"""Verify project setup is correct."""
import sys
from pathlib import Path


def check_imports():
    """Check if all imports work correctly."""
    print("Checking imports...")
    
    try:
        from shared.config import settings
        print("✅ Config module imports correctly")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from core.models import Character, Location, Note
        print("✅ Core models import correctly")
    except Exception as e:
        print(f"❌ Core models import failed: {e}")
        return False
    
    try:
        from infrastructure.api.rick_and_morty_client import RickAndMortyAPIClient
        print("✅ API client imports correctly")
    except Exception as e:
        print(f"❌ API client import failed: {e}")
        return False
    
    try:
        from infrastructure.repositories.character_repository import (
            SQLiteCharacterRepository
        )
        print("✅ Repository imports correctly")
    except Exception as e:
        print(f"❌ Repository import failed: {e}")
        return False
    
    try:
        from infrastructure.llm.openai_provider import OpenAIProvider
        print("✅ LLM provider imports correctly")
    except Exception as e:
        print(f"❌ LLM provider import failed: {e}")
        return False
    
    try:
        from core.services import LocationService, CharacterService
        print("✅ Services import correctly")
    except Exception as e:
        print(f"❌ Services import failed: {e}")
        return False
    
    return True


def check_files():
    """Check if required files exist."""
    print("\nChecking required files...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "infrastructure/db/schema.sql",
        "scripts/init_db.py",
        "shared/config.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist


def check_env():
    """Check if .env file exists."""
    print("\nChecking environment configuration...")
    
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        print("✅ .env file exists")
        
        # Check for required keys
        env_content = env_path.read_text()
        required_keys = ["OPENAI_API_KEY"]
        for key in required_keys:
            if key in env_content:
                print(f"✅ {key} is configured")
            else:
                print(f"⚠️  {key} not found in .env (will need to be set)")
    else:
        print("⚠️  .env file not found")
        print("   Create backend/.env with your OPENAI_API_KEY")
    
    return True


def check_database():
    """Check if database is initialized."""
    print("\nChecking database...")
    
    db_path = Path(__file__).parent.parent / "data" / "app.db"
    if db_path.exists():
        print("✅ Database file exists")
        return True
    else:
        print("⚠️  Database not initialized")
        print("   Run: python scripts/init_db.py")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Rick & Morty AI Challenge - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("File Structure", check_files),
        ("Python Imports", check_imports),
        ("Environment Config", check_env),
        ("Database", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASS" if result else "⚠️  NEEDS ATTENTION"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the server.")
    else:
        print("\n⚠️  Some checks need attention. Review the output above.")
    
    sys.exit(0 if all_passed else 1)

