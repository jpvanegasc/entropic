from entropic.sources import Sample
from entropic.process import Pipeline


class Process(Pipeline):
    source_path = "tests/mocks/"
    extract_with = Sample.read_csv


if __name__ == "__main__":
    p = Process()
    p.run()
