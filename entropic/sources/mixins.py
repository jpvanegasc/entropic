import pandas as pd


class PandasReadMixin:
    def read_csv(self, filename) -> pd.DataFrame:
        return pd.read_csv(filename)
