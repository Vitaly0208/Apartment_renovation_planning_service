import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from estimates import (
    check_budget,
    get_total_estimates,
    create_estimate,
)


def test_check_budget_sufficient():
    result = check_budget(150000, 100000)
    assert result["is_sufficient"] is True


def test_check_budget_insufficient():
    result = check_budget(50000, 100000)
    assert result["is_sufficient"] is False


def test_get_total_estimates():
    estimates = []
    create_estimate(estimates, 1, "Гостиная", 30000, 20000)
    create_estimate(estimates, 2, "Спальня", 25000, 15000)
    assert get_total_estimates(estimates) == 90000
