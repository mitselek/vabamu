"""
Quick validation that models work after Pydantic v2 migration.

This script tests:
- EntuEksponaat instantiation and validation
- MuisMuseaal instantiation and validation
- Validator behavior on invalid data
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import EntuEksponaat, MuisMuseaal


def test_entu_basic():
    """Test basic EntuEksponaat creation"""
    print("=" * 60)
    print("TEST 1: EntuEksponaat Basic Instantiation")
    print("=" * 60)
    
    entu = EntuEksponaat(  # type: ignore[call-arg]
        id="67890abcdef1234567890abc",
        code="006562/001",
        name="Test Object",
        date="2024-01-15"
    )
    
    print(f"✓ Created: {entu.code} - {entu.name}")
    print(f"✓ Date parsed: {entu.date} (type: {type(entu.date).__name__})")
    print(f"✓ MongoDB ID: {entu.id}")
    print()


def test_entu_code_format_warning():
    """Test code format validator with non-standard format"""
    print("=" * 60)
    print("TEST 2: EntuEksponaat Code Format Variance")
    print("=" * 60)
    
    import logging
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    
    # This should log a warning but still create the object
    entu = EntuEksponaat(  # type: ignore[call-arg]
        id="67890abcdef1234567890abc",
        code="ABC-123",  # Non-standard format
        name="Non-standard Code Test",
    )
    
    print(f"✓ Created with non-standard code: {entu.code}")
    print("  (Check for warning message above)")
    print()


def test_muis_basic():
    """Test basic MuisMuseaal creation"""
    print("=" * 60)
    print("TEST 3: MuisMuseaal Basic Instantiation")
    print("=" * 60)
    
    muis = MuisMuseaal(  # type: ignore[call-arg]
        acr="VBM",
        trt="_",
        trs=1,
        nimetus="Test Object"
    )
    
    print(f"✓ Created: {muis.acr}{muis.trt}{muis.trs} - {muis.nimetus}")
    print(f"✓ Required fields populated")
    print()


def test_muis_validation_osaleja():
    """Test MuisMuseaal validation: osaleja requires osaleja_roll"""
    print("=" * 60)
    print("TEST 4: MuisMuseaal Validation - osaleja_1 requires osaleja_roll_1")
    print("=" * 60)
    
    try:
        invalid = MuisMuseaal(  # type: ignore[call-arg]  # noqa: F841
            acr="VBM",
            trt="_",
            trs=1,
            nimetus="Test",
            osaleja_1="Doe, John"  # Missing osaleja_roll_1!
        )
        print("✗ FAILED: Should have raised ValidationError")
        return False
    except ValueError as e:
        print(f"✓ Validation works correctly")
        print(f"  Error message: {e}")
        print()
        return True


def test_muis_validation_description():
    """Test MuisMuseaal validation: tekst_1 requires teksti_tyyp_1"""
    print("=" * 60)
    print("TEST 5: MuisMuseaal Validation - tekst_1 requires teksti_tyyp_1")
    print("=" * 60)
    
    try:
        invalid = MuisMuseaal(  # type: ignore[call-arg]  # noqa: F841
            acr="VBM",
            trt="_",
            trs=1,
            nimetus="Test",
            tekst_1="Some description"  # Missing teksti_tyyp_1!
        )
        print("✗ FAILED: Should have raised ValidationError")
        return False
    except ValueError as e:
        print(f"✓ Validation works correctly")
        print(f"  Error message: {e}")
        print()
        return True


def test_muis_complete():
    """Test MuisMuseaal with multiple fields populated"""
    print("=" * 60)
    print("TEST 6: MuisMuseaal Complete Record")
    print("=" * 60)
    
    muis = MuisMuseaal(  # type: ignore[call-arg]
        acr="VBM",
        trt="_",
        trs=1,
        nimetus="Complete Test Object",
        pysiasukoht="Põhihoone/Ladu",
        parameeter_1="kõrgus",
        yhik_1="mm",
        vaartus_1=150.5,
        parameeter_2="laius",
        yhik_2="mm",
        vaartus_2=200.0,
        materjal_1="puit",
        materjali_1_kommentaar="kask",
        tehnika_1="nikerdamine",
        teksti_tyyp_1="füüsiline kirjeldus",
        tekst_1="Käsitsi nikerdatud puidust ese.",
        avalik="y"
    )
    
    print(f"✓ Created complete record: {muis.nimetus}")
    print(f"✓ Measurements: {muis.parameeter_1}={muis.vaartus_1}{muis.yhik_1}, " 
          f"{muis.parameeter_2}={muis.vaartus_2}{muis.yhik_2}")
    print(f"✓ Material: {muis.materjal_1} ({muis.materjali_1_kommentaar})")
    print(f"✓ Technique: {muis.tehnika_1}")
    print(f"✓ Description: {muis.tekst_1}")
    print(f"✓ Public: {muis.avalik}")
    print()


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + "  PYDANTIC V2 MIGRATION VALIDATION".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    tests_passed = 0
    tests_total = 6
    
    try:
        test_entu_basic()
        tests_passed += 1
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}\n")
    
    try:
        test_entu_code_format_warning()
        tests_passed += 1
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}\n")
    
    try:
        test_muis_basic()
        tests_passed += 1
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}\n")
    
    try:
        if test_muis_validation_osaleja():
            tests_passed += 1
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}\n")
    
    try:
        if test_muis_validation_description():
            tests_passed += 1
    except Exception as e:
        print(f"✗ TEST 5 FAILED: {e}\n")
    
    try:
        test_muis_complete()
        tests_passed += 1
    except Exception as e:
        print(f"✗ TEST 6 FAILED: {e}\n")
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n✓ ALL TESTS PASSED! Pydantic v2 migration successful.")
        return 0
    else:
        print(f"\n✗ {tests_total - tests_passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
