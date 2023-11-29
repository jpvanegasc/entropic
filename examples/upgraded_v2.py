import pandas as pd
from entropic.sources import Sample
from entropic.process import Pipeline
from entropic import results


class KinematicSample(Sample):
    speed: float = 0


class Process(Pipeline):
    source_paths = ["tests/mocks"]
    extract_with = pd.read_csv
    sample = KinematicSample  # this will set the sample in the iteration, most likely in the metaclass __new__

    def transform(self, iteration):
        for sample in iteration.samples:
            sample.speed = (sample.data.raw["x"] / sample.data.raw["t"]).mean()


p = Process()
p.run()

if __name__ == "__main__":
    for iteration in results.all:
        print(iteration.source_path)
        for sample in iteration.samples:
            print(sample.speed)
