from typing import List, Optional

from entropic.sources.sample import Sample


class Iteration:
    samples: List[Sample]
    source_path: Optional[str]
