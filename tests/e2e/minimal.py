import pandas as pd

from entropic.process import Pipeline


class Process(Pipeline):
    source_path = "tests/mocks/"
    extract_with = pd.read_csv


if __name__ == "__main__":
    p = Process()
    p.run()
