from hypothesis import given, settings, strategies as st
from bike_share_rental_parser import parse_ride_duration, format_station_code, parse_ride_log

# Anything a careless caller might pass in, not just strings.
ANYTHING = st.one_of(
    st.none(), st.booleans(), st.integers(), st.floats(),
    st.binary(), st.lists(st.integers()), st.text(),
)


# ---------- 1. Fuzz tests: no function may crash on any input ----------
@given(st.text() | st.none())
def test_parse_ride_duration_no_crash(s):
    try:
        parse_ride_duration(s)
    except Exception as e:
        assert False, f"parse_ride_duration crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_format_station_code_no_crash(s):
    try:
        format_station_code(s)
    except Exception as e:
        assert False, f"format_station_code crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_parse_ride_log_no_crash(s):
    try:
        parse_ride_log(s)
    except Exception as e:
        assert False, f"parse_ride_log crashed with: {e!r} for input {s!r}"


# ---------- 2. Fuzz tests with non-string inputs ----------
@given(ANYTHING)
def test_parse_ride_duration_any_type(x):
    try:
        parse_ride_duration(x)
    except Exception as e:
        assert False, f"parse_ride_duration crashed with: {e!r} for input {x!r}"


@given(ANYTHING)
def test_format_station_code_any_type(x):
    try:
        format_station_code(x)
    except Exception as e:
        assert False, f"format_station_code crashed with: {e!r} for input {x!r}"


@given(ANYTHING)
def test_parse_ride_log_any_type(x):
    try:
        parse_ride_log(x)
    except Exception as e:
        assert False, f"parse_ride_log crashed with: {e!r} for input {x!r}"


# ---------- 3. Property tests: valid input still gives the right answer ----------
@given(st.integers(0, 99), st.integers(0, 59))
def test_valid_duration_round_trip(h, m):
    assert parse_ride_duration(f"{h:02d}:{m:02d}") == h * 60 + m


@given(st.sampled_from("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"),
       st.integers(0, 9999))
def test_valid_station_code_format(letter, number):
    assert format_station_code(f"{letter}{number}") == f"{letter.upper()}-{number}"


@given(st.sampled_from(["standard", "electric", "cargo"]),
       st.integers(1, 100000), st.booleans())
def test_valid_ride_log(bike, minutes, sub):
    line = f"{bike},{minutes},{'yes' if sub else 'no'}"
    assert parse_ride_log(line) == (bike, minutes, sub)
