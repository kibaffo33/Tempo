import pytest
import tempo


db = tempo.Database()


@pytest.mark.parametrize("milliseconds", (True, False))
def test_epoch_timestamp_zero(milliseconds):

    # GIVEN user_input of zero
    user_input = "0"

    # WHEN inputting timestamp
    db.insert(user_input, milliseconds)

    # THEN confirm result is as expected
    expected = "1970-01-01 00:00:00"
    result = db.get_timestamp()
    assert result == expected


@pytest.mark.parametrize("milliseconds", (True, False))
def test_epoch_timestamp_millenium(milliseconds):

    # GIVEN user_input of zero
    user_input = "946684800"
    if milliseconds:
        user_input = str(int(user_input) * 1000)

    # WHEN inputting timestamp
    db.insert(user_input, milliseconds)

    # THEN confirm result is as expected
    expected = "2000-01-01 00:00:00"
    result = db.get_timestamp()
    assert result == expected
