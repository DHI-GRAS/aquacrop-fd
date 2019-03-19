import pandas as pd

NA_VALUES = ['-9', '-9.00', '-9.9']


def _make_unique(nn):
    from collections import defaultdict
    ncounts = defaultdict(int)
    for n in nn:
        ncounts[n] += 1

    nnu = []
    for n in nn[::-1]:
        c = ncounts[n]
        if c == 1:
            nnu.append(n)
        else:
            nu = f'{n}{c:02d}'
            nnu.append(nu)
            ncounts[n] -= 1
    return nnu[::-1]


NAMES = _make_unique([
    'Day', 'Month', 'Year', 'DAP', 'Stage', 'WC(2.30)', 'Rain', 'Irri', 'Surf',
    'Infilt', 'RO', 'Drain', 'CR', 'Zgwt', 'Ex', 'E', 'E/Ex', 'Trx', 'Tr', 'Tr/Trx',
    'ETx', 'ET', 'ET/ETx', 'GD', 'Z', 'StExp', 'StSto', 'StSen', 'StSalt', 'StWeed',
    'CC', 'CCw', 'StTr', 'Kc(Tr)', 'Trx', 'Tr', 'TrW', 'Tr/Trx', 'WP', 'Biomass', 'HI',
    'YieldPart', 'Brelative', 'WPet', 'WC(2.30)', 'Wr(2.30)', 'Z', 'Wr', 'Wr(SAT)',
    'Wr(FC)', 'Wr(exp)', 'Wr(sto)', 'Wr(sen)', 'Wr(PWP)', 'SaltIn', 'SaltOut', 'SaltUp',
    'Salt(2.30)', 'SaltZ', 'Z', 'ECe', 'ECsw', 'StSalt', 'Zgwt', 'ECgw', 'WC01', 'WC02',
    'WC03', 'WC04', 'WC05', 'WC06', 'WC07', 'WC08', 'WC09', 'WC10', 'WC11', 'WC12',
    'ECe01', 'ECe02', 'ECe03', 'ECe04', 'ECe05', 'ECe06', 'ECe07', 'ECe08', 'ECe09',
    'ECe10', 'ECe11', 'ECe12', 'Rain', 'ETo', 'Tmin', 'Tavg', 'Tmax', 'CO2'
])


def parse_daily_output(path):
    """Parse output file with daily values

    Parameters
    ----------
    path : str
        path to file

    Returns
    -------
    pandas.DataFrame
        parsed data with date index
    """
    df = pd.read_csv(
        path,
        delim_whitespace=True,
        names=NAMES,
        skiprows=4,
        # encoding='latin_1',  # degree sign in (skipped) line 4
        parse_dates={'date': ['Day', 'Month', 'Year']},
        index_col='date',
        na_values=NA_VALUES
    )
    return df


def select_final_output(df):
    """Select a small subset of final output"""
    return {
        'total_irrigation': df['Irri'].sum(),
        'final_yield': df['Brelative'][-1],
        'time': df.index[-1].to_pydatetime()
    }
