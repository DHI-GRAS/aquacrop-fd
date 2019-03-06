
def date_to_num(date):
    """Convert datetime to days since 1901"""
    num = (date.year - 1901) * 365.25
    num += [
        0, 31, 59.25, 90.25, 120.25,
        151.25, 181.25, 212.25, 243.25,
        273.25, 304.25, 334.25
    ][date.month - 1]
    num += date.day
    return int(num)
