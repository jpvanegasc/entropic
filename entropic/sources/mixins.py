import pandas as pd


class PandasReadMixin:
    def read_csv(self, filename):
        return pd.read_csv(filename)
