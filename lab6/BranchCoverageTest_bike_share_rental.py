import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock


# =============== ride_cost ===============
def test_standard_ride():
    assert ride_cost("standard", 45, False, False) == 40


@pytest.mark.parametrize("bike", ["scooter", "", "Standard"])
def test_unknown_bike_type(bike):
    with pytest.raises(ValueError, match="unknown bike type"):
        ride_cost(bike, 30, False, False)


@pytest.mark.parametrize("minutes", [0, -5])
def test_invalid_duration(minutes):
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", minutes, False, False)


def test_one_minute_is_one_block():
    assert ride_cost("standard", 1, False, False) == 20


def test_exact_block_boundary_30_and_31():
    assert ride_cost("standard", 30, False, False) == 20
    assert ride_cost("standard", 31, False, False) == 40


def test_subscriber_single_block_is_free():
    assert ride_cost("electric", 30, True, False) == 0


def test_subscriber_pays_after_first_block():
    assert ride_cost("standard", 45, True, False) == 20


def test_non_subscriber_pays_all_blocks():
    assert ride_cost("cargo", 60, False, False) == 100


def test_peak_surcharge_standard():
    assert ride_cost("standard", 30, False, True) == 35


def test_peak_surcharge_electric():
    assert ride_cost("electric", 30, False, True) == 50


def test_peak_no_surcharge_for_cargo():
    assert ride_cost("cargo", 30, False, True) == 50


def test_off_peak_no_surcharge():
    assert ride_cost("electric", 30, False, False) == 35


def test_subscriber_and_peak_combined():
    # 60 min = 2 blocks, 1 free -> 35 + 15
    assert ride_cost("electric", 60, True, True) == 50


def test_long_ride_fee_applied_over_180():
    # 181 min = 7 blocks * 20 + 100
    assert ride_cost("standard", 181, False, False) == 240


def test_no_long_fee_at_exactly_180():
    # 180 min = 6 blocks * 20, no fee
    assert ride_cost("standard", 180, False, False) == 120


def test_long_ride_subscriber():
    # 200 min = 7 blocks, 1 free -> 6*20 + 100
    assert ride_cost("standard", 200, True, False) == 220


# =============== dock_status ===============
@pytest.mark.parametrize("capacity", [0, -1])
def test_invalid_capacity(capacity):
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, capacity)


def test_negative_bike_count():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(-1, 10)


def test_bikes_exceed_capacity():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(11, 10)


def test_dock_empty():
    assert dock_status(0, 10) == "empty"


def test_dock_full():
    assert dock_status(10, 10) == "full"


def test_dock_single_slot_edge_cases():
    assert dock_status(0, 1) == "empty"
    assert dock_status(1, 1) == "full"


@pytest.mark.parametrize("bikes", [1, 2])
def test_dock_few_bikes(bikes):
    assert dock_status(bikes, 10) == "few bikes"


@pytest.mark.parametrize("bikes", [8, 9])
def test_dock_few_slots(bikes):
    assert dock_status(bikes, 10) == "few slots"


@pytest.mark.parametrize("bikes", [3, 5, 7])
def test_dock_available(bikes):
    assert dock_status(bikes, 10) == "available"


# =============== can_unlock ===============
def test_unlock_blocked_by_active_ride():
    assert can_unlock(500, True, 30) is False


@pytest.mark.parametrize("age", [0, 15])
def test_unlock_under_16_denied(age):
    assert can_unlock(500, False, age) is False


@pytest.mark.parametrize("age", [16, 17])
def test_unlock_teen_needs_100(age):
    assert can_unlock(100, False, age) is True
    assert can_unlock(99, False, age) is False


@pytest.mark.parametrize("age", [18, 40])
def test_unlock_adult_needs_50(age):
    assert can_unlock(50, False, age) is True
    assert can_unlock(49, False, age) is False
