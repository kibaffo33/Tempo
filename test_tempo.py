import pytest
import tempo


db = tempo.Database()


def test_labels_match_algorithms():
    labels = tempo.LABELS.values()
    algorithms = tempo.ALGORITHMS.keys()
    assert list(labels) == list(algorithms)


@pytest.mark.parametrize(
    "algorithm,user_input,modifier,expected_result",
    [
        (tempo.LABELS["epoch"], "0", "0 hours", "1970-01-01 00:00:00"),
        (tempo.LABELS["epoch"], "0", "4 hours", "1970-01-01 04:00:00"),
        (tempo.LABELS["epoch"], "946684800", "0 hours", "2000-01-01 00:00:00"),
        (tempo.LABELS["epoch"], "946684800", "-1 hours", "1999-12-31 23:00:00"),
        (tempo.LABELS["epoch_ms"], "0", "0 hours", "1970-01-01 00:00:00"),
        (tempo.LABELS["epoch_ms"], "0", "4 hours", "1970-01-01 04:00:00"),
        (tempo.LABELS["epoch_ms"], "946684800000", "0 hours", "2000-01-01 00:00:00"),
        (tempo.LABELS["epoch_ms"], "946684800000", "-1 hours", "1999-12-31 23:00:00"),
        (tempo.LABELS["cocoa"], "0", "0 hours", "2001-01-01 00:00:00"),
        (tempo.LABELS["cocoa"], "0", "4 hours", "2001-01-01 04:00:00"),
        (tempo.LABELS["cocoa"], "-978307200", "0 hours", "1970-01-01 00:00:00"),
        (tempo.LABELS["cocoa"], "-978307200", "12 hours", "1970-01-01 12:00:00"),
        (tempo.LABELS["chrome"], "0", "0 hours", "1601-01-01 00:00:00"),
        (tempo.LABELS["chrome"], "0", "2 hours", "1601-01-01 02:00:00"),
        (tempo.LABELS["chrome"], "12345678900000000", "0 hours", "1992-03-21 19:15:00"),
        (tempo.LABELS["chrome"], "12345678900000000", "-4 hours", "1992-03-21 15:15:00"),
    ],
)
def test_timestamps(algorithm, user_input, modifier, expected_result):

    # GIVEN a user input, modifier and algorithm
    db.set_meta("algorithm", algorithm)
    db.set_meta("modifier", modifier)

    # WHEN submitted user_input
    db.insert_timestamp(user_input)

    # THEN check result is as expected
    result = db.get_timestamp()
    assert result == expected_result
