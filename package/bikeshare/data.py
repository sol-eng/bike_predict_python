import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Clean the date column
    out['date'] = pd.to_datetime(out['date'])

    # One hot encode dow column
    out = pd.get_dummies(out, prefix=[""], prefix_sep="", columns = ['dow'])

    # Select final columns
    cols = [
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
    ]

    return out[cols]