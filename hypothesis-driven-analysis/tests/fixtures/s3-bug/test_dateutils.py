from dateutils import parse_date

EXPECTED_YEAR = 2026


def test_parse_dates():
    assert parse_date("2026-07-14T03:12:09Z").year == EXPECTED_YEAR
