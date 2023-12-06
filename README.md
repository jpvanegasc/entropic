# Entropic
> From chaos, information.

Entropic is a data pipeline framework designed to provide scientists with a simple and efficient way to access data from their experiments. This documentation will guide you through the installation, usage, and customization of the Entropic package.

## Requirements
Entropic needs Python 3.9+, and relies mostly on:
* [Pydantic](https://docs.pydantic.dev/latest/) for data validation.
* [Pandas](https://pandas.pydata.org/) for data analysis.

## Installation

You can install Entropic using `pip`:

```bash
pip install entropic
```

## Usage
### Example
The most basic data pipeline that can be created with entropic consists of a `Pipeline` subclass which defines the directories containing the experiment results and a function that will be used to read each result file and create a pandas DataFrame from it:

```python
import pandas as pd

from entropic.process import Pipeline
from entropic import results


class Process(Pipeline):
    source_paths = ["experiments/iteration_1", "experiments/iteration_2"]
    extract_with = pd.read_csv


p = Process()
p.run()


if __name__ == "__main__":
    for iteration in results.all:
        for sample in iteration.samples:
            print(sample.data.raw.head())
```


The main parts from this example are:
1. Define your data processing class by inheriting from Pipeline:
    ```python
    class Process(Pipeline):
        source_paths = ["experiments/iteration_1", "experiments/iteration_2"]
        extract_with = pd.read_csv
    ```
    The `source_paths` variable points to folders which contain the results for an iteration. Within entropic, an iteration can be thought as a set of initial conditions for which you performed an experiment and took various samples with various results. `extract_with` defines a function that will read through all of the sample files and create a DataFrame from it. In this example I'm using `pandas.read_csv`, but it can be any function you want -you can even custom define it and pass it to `extract_with`.
2. Instantiate and run the pipeline:
    ```python
    p = Process()
    p.run()
    ```
3. Access your results using the `results` API:
    ```python
    if __name__ == "__main__":
        for iteration in results.all:
            for sample in iteration.samples:
                print(sample.data.raw.head())
    ```
In this example the accessing of results happens on the same file in which you run the pipeline. However, for performance reasons you might want to consider splitting the processing and the analysis on two different files. In this case you only need to run the processing part once, and your data will be loaded to a JSON-based database.

### Example upgrade
A more realistic example will involve custom iterations and samples, which need custom logic for extracting, transforming or loading them into the database.

```python
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
    source_paths = ["experiments/initial_condition_1"]
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
```


A few changes have been done from the previous example:

1. Custom iteration and sample classes were created:
    ```python
    class KinematicSample(BaseSample):
        data: DataSource
        speed: float = 0
        points_in_data: int = 0


    class KinematicExperiment(Iteration):
        average_speed: float = 0
        sample = KinematicSample
    ```
2. Instead of defining an `extract_with` function, the extract function is defined instead. Also, calculations can be performed on a given iteration using the `transform` function:
    ```python
    class Process(Pipeline):
        source_paths = ["experiments/initial_condition_1"]
        iteration = KinematicExperiment

        def extract(self, file_path):
            raw = pd.read_csv(file_path)
            data_source = DataSource(file_path=file_path, raw=raw)
            return self.get_sample()(data=data_source, points_in_data=raw.shape[0])

        def transform(self, iteration):
            average = 0
            for sample in iteration.samples:
                sample.speed = (sample.data.raw["x"] / sample.data.raw["t"]).mean()
                average += sample.speed
            iteration.average_speed = average / len(iteration.samples)
    ```
    Note that `KinematicExperiment` is being defined as the iteration for the `Process` class. You can access the `iteration` and `sample` using `self.get_iteration()` and `self.get_sample()`. Don't try to access `self.iteration` and `self.sample`, as it might break!
3. In order to properly display results, the custom iteration has to be "added" to the results API:
    ```python
    results.set_iteration(KinematicExperiment)
    ```

