import datetime


def test_date_to_num():
    from aquacrop_fd import utils
    date = datetime.date(1990, 3, 22)
    res = utils.date_to_num(date)
    expected = 32588
    assert res == expected
