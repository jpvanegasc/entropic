import pandas as pd
from entropic.sources import Sample, Iteration
from entropic.process import Pipeline
from entropic import results


class KinematicSample(Sample):
    speed: float = 0


class KinematicExperiment(Iteration):
    average_speed: float = 0
    sample = KinematicSample


class Process(Pipeline):
    source_paths = ["../tests/mocks"]
    extract_with = pd.read_csv
    iteration = KinematicExperiment

    def transform(self, iteration):
        average = 0
        for sample in iteration.samples:
            sample.speed = (sample.data.raw["x"] / sample.data.raw["t"]).mean()
            average += sample.speed
        iteration.average_speed = average / len(iteration.samples)


p = Process()
p.run()

results.set_iteration(KinematicExperiment)

if __name__ == "__main__":
    for iteration in results.all:
        print(iteration.average_speed)
        for sample in iteration.samples:
            print(sample.speed)
