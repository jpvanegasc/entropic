# Entropic
A simple data processing framework for physics that can be integrated with data processing pipelines for a quick, no-frills setup.

## Usage
### Absolute minimum
The simples, most minimal setup for entropic is just declaring the pipeline source path and extract method:

```python
from entropic.sources import Sample
from entropic.process import Pipeline


class Process(Pipeline):
    source_path = "path/to/raw/results"
    extract_with = Sample.read_csv  # wrapper over pandas.read_csv()
```

After running `entropic run` you can access your results with

```python
from entropic.results import Results

for experiment in Results.all:  # Results.all is a generator
    for sample in experiment.samples:  # experiment.samples is a generator
        print(sample.data)  # pandas dataframe
```

### Example upgrade
A bit more complex example would involve creating a Case:

```python
import pandas as pd
from entropic.sources import Case, FloatField
from entropic.process import Pipeline
from entropic.results import Results


class Kinematic(Case):
    speed = FloatField()


class Process(Pipeline):
    source_path = "path/to/raw/results"
    experiment = Kinematic

    def extract(self, filename):
        """Specifies how to load each sample"""
        with open(filename) as f:
            data = f.read()
        # do something with data
        return pd.DataFrame(data)

    def load(self, sample):
        """Specifies how to calculate experiment values"""
        self.speed = sample["x"] / sample["t"]


# Load experiment into results
Results.include(Kinematic)
```

After running `entropic run` you can access your results with

```python
from entropic.results import Results

for experiment in Results.all:
    print(experiment.speed)  # average speed value for all samples
    for sample in experiment.samples:
        print(sample.speed)  # calculated speed for sample
        print(sample.data)  # pandas dataframe
```
