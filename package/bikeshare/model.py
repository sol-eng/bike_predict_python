import pandas as pd

def get_dow(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    return df


def one_hot_encode(df: pd.DataFrame) -> pd.DataFrame:
    return pd.get_dummies(df, prefix=[""], prefix_sep="", columns = ['dow'])


def select_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df[[
        'lat',
        'lon',
        'hour',
        'month',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]]