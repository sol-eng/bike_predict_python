import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Clean the date column
    out['date'] = pd.to_datetime(out['date'])

    # Specify categories for dow
    days_of_week = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]
    out['dow'] = pd.Categorical(
        out['dow'],
        categories=days_of_week
    )

    # One hot encode dow column
    out = pd.get_dummies(out, prefix=[""], prefix_sep="", columns = ['dow'])

    # Select final columns
    cols = ['lat', 'lon', 'hour', 'month'] + days_of_week

    return out[cols]