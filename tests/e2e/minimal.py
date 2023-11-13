from entropic.sources import Sample
from entropic.process import Pipeline


class Process(Pipeline):
    source_path = "../mocks/"
    extract_with = Sample.read_csv
