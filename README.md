# Entropic
> From chaos, information.

Entropic is a data pipeline framework designed to provide scientists with a simple and efficient way to access data from their experiments. This documentation will guide you through the installation, usage, and customization of the Entropic package.

## Requirements
Entropic needs Python 3.8+, and relies mostly on:
* [Pydantic](https://docs.pydantic.dev/latest/) for data validation.
* [Pandas](https://pandas.pydata.org/) for data analysis.

## Installation

You can install Entropic using `pip`:

```bash
pip install entropic
```

## Usage
### Example
The most basic data pipeline that can be created with entropic consists of a `Pipeline` subclass which defines the directory containing all of the experiment results and a function that will be used to read each result file and create a pandas DataFrame from it:

```python
import pandas as pd

from entropic.process import Pipeline
from entropic import results


class Process(Pipeline):
    source_path = "../tests/mocks/"
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
        source_path = "../tests/mocks/"
        extract_with = pd.read_csv
    ```
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

