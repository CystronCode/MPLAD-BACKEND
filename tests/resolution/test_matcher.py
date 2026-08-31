# tests/resolution/test_matcher.py
# Adversarial unit test suite for 7-stage entity resolution pipeline

import pytest
from backend.app.normalization.taxonomy import normalize_asset_description, CanonicalAssetType
from backend.app.resolution.cleaner import clean_and_expand_school_name
from backend.app.resolution.matcher import calculate_composite_match_score, resolve_project

def test_taxonomy_normalization():
    desc1 = "Construction of 2 Additional Class rooms at GHS Rampur Block-1"
    asset1, qty1 = normalize_asset_description(desc1)
    assert asset1 == CanonicalAssetType.ADDITIONAL_CLASSROOM
    assert qty1 == 2

    desc2 = "Supply of computers and setup of smart ICT lab"
    asset2, qty2 = normalize_asset_description(desc2)
    assert asset2 == CanonicalAssetType.COMPUTER_LAB
    assert qty2 == 1

    desc3 = "Provision of drinking water and girls toilet facility"
    asset3, qty3 = normalize_asset_description(desc3)
    assert asset3 == CanonicalAssetType.TOILET_BLOCK

def test_cleaner_and_abbreviation_expansion():
    cleaned = clean_and_expand_school_name("Construction of 2 rooms at GHS Rampur")
    assert "government high school" in cleaned
    assert "rampur" in cleaned

def test_adversarial_exact_and_fuzzy_matches():
    # Case 1: Standard match with abbreviation expansion and campus proximity
    score1, status1 = calculate_composite_match_score(
        project_text_raw="Construction of 2 rooms at GHS Rampur",
        candidate_name_raw="Government High School Rampur",
        project_coords=(31.1423, 77.1724),
        candidate_coords=(31.1421, 77.1722)
    )
    assert score1 >= 0.85
    assert status1 == "AUTO_ACCEPTED"

    # Case 2: Out of bounds spatial rejection (> 5km)
    score2, status2 = calculate_composite_match_score(
        project_text_raw="GHS Rampur",
        candidate_name_raw="Government High School Rampur",
        project_coords=(31.1423, 77.1724),
        candidate_coords=(31.2500, 77.3500)
    )
    assert score2 == 0.0
    assert "SPATIAL_REJECT" in status2

def test_reverse_spatial_fallback_for_renamed_school():
    score, status = calculate_composite_match_score(
        project_text_raw="Shaheed Bhagat Singh Memorial High School",
        candidate_name_raw="Government High School Rampur",
        project_coords=(31.1423, 77.1724),
        candidate_coords=(31.1421, 77.1722)
    )
    assert score >= 0.85
    assert "REVERSE_SPATIAL" in status
