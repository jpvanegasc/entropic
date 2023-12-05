# Reference
## Processing
### `Pipeline`
#### Overview

The `Pipeline` class is a base class designed to facilitate the creation of data processing pipelines. It enforces a structured approach to defining and executing data processing steps, such as extraction, transformation, and loading (ETL).


#### Class Attributes

- **iteration**: `Iteration`
  - Iteration to be used for processing. Defaults to `Iteration`
  
- **source_paths**: List[Union[Path, str]]
  - A list of path-like objects or strings representing the source paths from which data will be extracted.

- **extract_with**: Callable
  - A callable object or function responsible for extracting data from a given file path into samples for each iteration.

#### Methods

* `__init__(self)`
    - Initializes the Pipeline instance. Raises an error if an attempt is made to instantiate the base `Pipeline` class directly.

* `get_source_paths(self) -> List[Union[Path, str]]`
    - Returns the list of source paths defined in the pipeline.

* `get_iteration(self) -> Type[IterationType]`
    - Returns the iteration type associated with the pipeline.

* `get_iteration_by_path(self, source_path: Union[Path, str]) -> Optional[IterationType]`
    - Wrapper over `Iteration.get_or_create(source_path=source_path)`

* `get_sample(self) -> Any`
    - Returns the sample associated with the iteration.

* `get_files_from_path(self, path: Union[Path, str]) -> List[Path]`
    - Retrieves a list of `Path` objects representing files in the specified path.

* `extract(self, file_path: Union[Path, str]) -> IterationType`
    - Extracts data from the specified file using the defined `extract_with` method and returns an `Iteration` object.

* `transform(self, iteration: IterationType) -> IterationType`
    - Transforms the given iteration and returns the transformed iteration.

* `load(self, iteration: IterationType) -> Any`
    - Loads the specified iteration by saving it.

* `extract_all_iterations(self) -> List[IterationType]`
    - Extracts data from all specified source paths and returns a list of iterations.

* `transform_all_iterations(self, iterations: List[IterationType]) -> List[IterationType]`
    - Transforms a list of iterations and returns the transformed list.

* `load_all_iterations(self, iterations: List[IterationType]) -> List[Any]`
    - Loads a list of iterations by saving them, and returns the list of results.

* `run(self) -> List[Any]`
    - Executes the entire pipeline, including extraction, transformation, and loading, and returns the final results.

## Sources
### `Iteration`
#### Overview

The `Iteration` class is a generic class designed to represent iterations of data processing. It includes methods for serialization, validation, retrieval, and storage of data samples associated with a specific source path.

#### Class Attributes

- **database**: ClassVar
  - Description: The database used for storage. By default, it is set to `default_database()`.

- **sample**: ClassVar
  - Description: The sample class associated with the iteration.

- **samples**: List[SampleType]
  - Description: A list of samples associated with the iteration. Initialized as an empty list.

- **source_path**: Path
  - Description: The source path associated with the iteration.

#### Methods

* `serialize_source_path(self, source_path: Path) -> str`
    - Serializes the source path to a string for storage.

* `validate_samples(cls, value: list) -> List[SampleType]`
    - Validates a list of samples using the associated sample class.

* `serialize_samples(self, samples: list) -> List[dict]`
    - Serializes a list of samples to a list of dictionaries for storage.

* `get_or_create(cls, **kwargs) -> Iteration`
    - Retrieves an existing iteration from the database or creates a new one based on the provided keyword arguments.

* `save(self) -> dict`
    - Saves the iteration in the database using the serialized data.

* `upsert_sample(self, sample: SampleType) -> SampleType`
    - Updates or inserts a sample into the iteration's sample list.

#### Pydantic Fields

- **database**: ClassVar
  - Type: ClassVar
  - Description: The database used for storage.

- **sample**: ClassVar
  - Type: ClassVar
  - Description: The sample class associated with the iteration.

- **samples**: List[SampleType]
  - Type: List[SampleType]
  - Description: A list of samples associated with the iteration.

- **source_path**: Path
  - Type: Path
  - Description: The source path associated with the iteration.

#### Pydantic Validators

- **validate_samples(cls, value: list) -> List[SampleType]**
  - Description: Validates a list of samples using the associated sample class.

#### Pydantic Serialization

- **serialize_source_path(self, source_path: Path) -> str**
  - Description: Serializes the source path to a string for storage.

- **serialize_samples(self, samples: list) -> List[dict]**
  - Description: Serializes a list of samples to a list of dictionaries for storage.

