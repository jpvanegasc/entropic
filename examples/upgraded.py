import pandas as pd

from entropic import results
from entropic.sources import BaseSample, Iteration
from entropic.process import Pipeline
from entropic.sources.fields import DataSource


class KinematicSample(BaseSample):
    data: DataSource
    speed: float = 0
    points_in_data: int = 0


class KinematicExperiment(Iteration):
    average_speed: float = 0
    sample = KinematicSample


class Process(Pipeline):
    source_paths = ["../tests/mocks"]
    iteration = KinematicExperiment

    def extract(self, source_path):
        iteration = self.get_iteration_by_path(source_path)
        for file_path in self.get_files_from_path(source_path):
            raw = pd.read_csv(file_path)
            data_source = DataSource(file_path=file_path, raw=raw)
            sample = self.get_sample()(data=data_source, points_in_data=raw.shape[0])
            iteration.upsert_sample(sample)
        return iteration

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
        print(f"Iteration average speed={iteration.average_speed}")
        for i, sample in enumerate(iteration.samples):
            print(f"Sample {i+1}")
            print(f"speed={sample.speed}")
            print(f"rows={sample.points_in_data}")
            print()
