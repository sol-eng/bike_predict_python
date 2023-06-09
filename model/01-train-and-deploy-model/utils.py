import pandas as pd

from sklearn.base import BaseEstimator,TransformerMixin



class DataCleaner(BaseEstimator, TransformerMixin):
    def __init__(self):
        return None
    
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        df = X.copy()
        df = self.add_dow_as_int(df)
        df = self.add_missing_dow(df)
        return df

    def add_dow_as_int(self, X):
        '''One hot encoding the day of the week'''
        df = X.copy()
        df['date'] = pd.to_datetime(df['date'])
        one_hot = pd.get_dummies(df['dow'])
        df = df.join(one_hot)
        df = df.drop('dow',axis=1)
        return df

    def add_missing_dow(self, X):
        ''' add encoding for missing dow in testing dataset'''
        df = X.copy()
        all_dow = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'
        ]
        dow_in_data = df.columns.drop(['date','hour','month']).to_list()
        dow_not_in_data = np.setdiff1d(all_dow, dow_in_data, assume_unique=False)
        for i in dow_not_in_data:
            df[i] = False
        df = df.drop(columns=["date"])
        # Arrange columns and select final features
        df = df[[
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
        return df