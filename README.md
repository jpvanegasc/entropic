# Entropic
A simple data processing framework for physics that can be integrated with data processing pipelines for a quick, no-frills setup.

## Usage
### Absolute minimum
The simples, most minimal setup for entropic is just declaring the pipeline source path and extract method:

```python
# pipeline.py
from entropic.sources import Sample
from entropic.process import Pipeline


class Process(Pipeline):
    source_path = "path/to/raw/results"
    extract_with = Sample.read_csv  # wrapper over pandas.read_csv()


if __name__ == "__main__":
    pipe = Process()
    pipe.run()
```

Run `python3 pipeline.py` and access your results with

```python
# results.py
from entropic import results

for iteration in results.all:
    for sample in iteration.samples:
        print(sample.data)  # pandas dataframe
```
