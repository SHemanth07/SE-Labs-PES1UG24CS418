import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock


# ---------- ride_cost ----------
def test_standard_ride():
    assert ride_cost("standard", 45, False, False) == 40


def test_unknown_bike_type():
    with pytest.raises(ValueError):
        ride_cost("scooter", 30, False, False)


def test_zero_minutes():
    with pytest.raises(ValueError):
        ride_cost("standard", 0, False, False)


def test_subscriber_first_block_free():
    assert ride_cost("standard", 30, True, False) == 0


def test_subscriber_pays_extra_blocks():
    # 45 min = 2 blocks, 1 free -> 1 * 20
    assert ride_cost("standard", 45, True, False) == 20


def test_peak_surcharge_electric():
    # 1 block * 35 + 15 peak
    assert ride_cost("electric", 30, False, True) == 50


def test_long_ride_fee():
    # 181 min = 7 blocks * 20 + 100 long fee
    assert ride_cost("standard", 181, False, False) == 240


# ---------- dock_status ----------
def test_dock_available():
    assert dock_status(5, 10) == "available"


def test_dock_invalid_capacity():
    with pytest.raises(ValueError):
        dock_status(0, 0)


def test_dock_invalid_bike_count():
    with pytest.raises(ValueError):
        dock_status(-1, 10)


def test_dock_empty():
    assert dock_status(0, 10) == "empty"


def test_dock_full():
    assert dock_status(10, 10) == "full"


def test_dock_few_bikes():
    assert dock_status(1, 10) == "few bikes"


def test_dock_few_slots():
    assert dock_status(9, 10) == "few slots"


# ---------- can_unlock ----------
def test_unlock_active_ride():
    assert can_unlock(500, True, 30) is False


def test_unlock_too_young():
    assert can_unlock(500, False, 15) is False


def test_unlock_teen_enough_balance():
    assert can_unlock(100, False, 17) is True


def test_unlock_adult_enough_balance():
    assert can_unlock(50, False, 30) is True
