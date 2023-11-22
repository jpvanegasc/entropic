# Entropic
A simple data processing framework for a quick, no-frills setup of a data pipeline.

## Usage
### Absolute minimum
The simples, most minimal setup for entropic is just declaring the pipeline source path and extract method:

```python
# pipeline.py
import pandas as pd
from entropic.process import Pipeline


class Process(Pipeline):
    source_path = "path/to/raw/results"
    extract_with = pd.read_csv


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
        print(sample.data)
```
