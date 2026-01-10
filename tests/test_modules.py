import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent dir to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import extract_shop_type
from database_manager import DatabaseManager

# =============================================================================
# UNIT TESTS: Scraper Helper Functions
# =============================================================================

def test_extract_shop_type_simple():
    """Test standard query extraction."""
    query = "textile shops in Kochi"
    assert extract_shop_type(query) == "Textile Shops"

def test_extract_shop_type_no_location():
    """Test extraction when 'in' keyword is missing."""
    query = "gyms Kochi"
    assert extract_shop_type(query) == "Gyms Kochi"

def test_extract_shop_type_complex_location():
    """Test extraction with multi-word location."""
    query = "best restaurants in new york city"
    assert extract_shop_type(query) == "Best Restaurants"

# =============================================================================
# UNIT TESTS: Database Manager
# =============================================================================

def test_db_manager_offline_init():
    """Test DatabaseManager initializes in offline mode when no keys provided."""
    with patch.dict(os.environ, {}, clear=True):
        db = DatabaseManager(url="", key="")
        assert db.client is None

def test_db_manager_online_init():
    """Test DatabaseManager attempts connection when keys provided."""
    with patch("database_manager.create_client") as mock_create:
        db = DatabaseManager(url="http://fake.url", key="fake-key")
        mock_create.assert_called_once_with("http://fake.url", "fake-key")
        assert db.client is not None

def test_save_data_empty():
    """Test saving empty data returns early."""
    db = DatabaseManager(url="", key="")
    success, msg = db.save_data([])
    assert success is False
    assert msg == "No data to save"
