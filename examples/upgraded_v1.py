import pandas as pd
from entropic.sources import Iteration
from entropic.process import Pipeline
from entropic import results


class KinematicExperiment(Iteration):
    speed: float = 0


class Process(Pipeline):
    source_paths = ["tests/mocks"]
    iteration = KinematicExperiment
    extract_with = pd.read_csv

    def transform(self, iteration: KinematicExperiment):
        average_speed = 0
        for sample in iteration.samples:
            average_speed += (sample.data.raw["x"] / sample.data.raw["t"]).mean()
        iteration.speed = average_speed


p = Process()
p.run()

results.set_iteration(KinematicExperiment)

if __name__ == "__main__":
    for iteration in results.all:
        print(iteration.source_path)
        for sample in iteration.samples:
            print(sample.data.raw.head())
