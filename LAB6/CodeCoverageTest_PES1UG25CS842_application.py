import pytest
from income_tax import taxable_income, tax_due, refund_status

#Example test cases:
def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000

def test_below_exemption():
    assert tax_due(200000, 30) == 0

#Write the rest of the test cases so that the code is 90- 100% covered.
def test_negative_gross_raises():
    with pytest.raises(ValueError):
        taxable_income(-1, "new", 0)

def test_old_regime():
    assert taxable_income(1000000, "old", 0) == 950000

def test_old_regime_investment_cap():
    assert taxable_income(1000000, "old", 200000) == 800000

def test_unknown_regime_raises():
    with pytest.raises(ValueError):
        taxable_income(1000000, "xyz", 0)

def test_negative_tax_raises():
    with pytest.raises(ValueError):
        tax_due(-1, 30)
def test_small_income_returns_zero():
    assert taxable_income(50000, "new", 0) == 0

def test_tax_age_80_plus():
    assert tax_due(600000, 80) == 5000

def test_tax_age_60_to_79():
    assert tax_due(400000, 65) == 5000

def test_tax_high_slab():
    assert tax_due(1000000, 30) == 112500

def test_refund_on_time():
    assert refund_status(100000, 50000, True) == "refund"

def test_refund_delayed():
    assert refund_status(100000, 50000, False) == "refund delayed"

def test_balance_on_time():
    assert refund_status(50000, 100000, True) == "pay balance"

def test_balance_with_penalty():
    assert refund_status(50000, 100000, False) == "pay balance with penalty"

def test_settled():
    assert refund_status(100000, 100000, True) == "settled"