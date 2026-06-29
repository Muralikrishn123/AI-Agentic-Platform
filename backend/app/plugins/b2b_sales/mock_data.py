"""
Centralized Mock Database for B2B Sales Intelligence Plugin.
Dynamically generates 100+ target company profiles with complete schemas.
"""
from app.plugins.b2b_sales.generator import generate_mock_companies

# Generate 100 highly realistic companies
COMPANIES = generate_mock_companies(count=100)
