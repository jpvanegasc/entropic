from typing import List, Optional

from entropic.db import default_database

from entropic.sources.sample import Sample


class Iteration:
    samples: List[Sample]
    source_path: Optional[str]

    database = default_database()
