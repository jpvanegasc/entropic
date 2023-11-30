import os
from unittest.mock import patch

import pytest
import pandas as pd

from entropic import results
from entropic.process import Pipeline
from entropic.sources import Iteration
from entropic.db import TinyDBHandler


@pytest.fixture
def database():
    DB_PATH = ".entropic-essential-test"
    db = TinyDBHandler(path=DB_PATH)
    patch("entropic.results.database", db).start()
    patch("entropic.sources.Iteration.database", db).start()

    yield db

    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass


@pytest.fixture
def run_essential_pipeline(database):
    class Process(Pipeline):
        source_paths = ["tests/mocks/"]
        extract_with = pd.read_csv

    pipeline = Process()
    pipeline.run()

    # run again to test no duplicate samples or data sources are created
    pipeline.run()


def test_essential(run_essential_pipeline):
    all_results = list(results.all)
    assert len(all_results) == 1

    result = all_results[0]
    assert isinstance(result, Iteration)
    assert len(result.samples) == 2

    for sample in result.samples:
        assert sample.data
        assert sample.data.file_path
        assert isinstance(sample.data.raw, pd.DataFrame)

    assert result.model_dump() == {
        "samples": [
            {
                "data": {
                    "file_path": "tests/mocks/kinematic2.csv",
                    "raw": "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",
                }
            },
            {
                "data": {
                    "file_path": "tests/mocks/kinematic1.csv",
                    "raw": "eJy1lmlsG0UUx9eOj02b0LRkjUNdMKY1oXVSO7ZLHZJ21o5PkrQxjR2nQNgr9qa7a+MjthvCoaoSSKGFSuWSSEuRuFVAIPhSyn2LikMghKhUgTgkQKq4VIE43u46TkPCB5AY5eeZeTPz3n9m3qyynYy7CB1x2EA82tBPsAS2CsNub9BpsEYNpm006rCGZhzTAXrAABgBHGgElgHLgSagGTgHWAG0ACuBVcC5QCtAACbgPMAMtAHnA6sBC7AGuAC4ELACFwE24GJgLbAOsAOXAO3ApcB6YAPgADqATmAj4GzGe1yYWrpqNYHB7jIO+GkhDITBYsbnRsy4ptYyYe1LWGUnr2rhl9UYViBrUx9liRxx9H/Rs33twA7u6pEHxau+nr62fR/Lz2YePSp8ezzXJK+xP6O3ELo2L2ZoaTNrioTWxJpmcdPjevsHDXb838Rvc8ANYYRW3kMLISup3Zhh/sZ+2q/5ZtszPx/tPr318duMh/Y/h6GPvnkkeTCPo0eaNtw109GCtj5RbDjtaEW9pjUrqV4zSnczhw1aC3rszCU9JzRWdPd7v9PdBht6qTql+3X9WnR8Y+iPazR2tIf97N3XrO3o2urq41+Z1qPk7NO3H1zrQBOtNx2b0Xai2dvu1e7UO9G2Q/efyDW5UPf3/TceaO5CB04deezOZjd69ahtwxbcgz7ojL3Sc64XGZ4Sjrzbugm98Na62RMNl6H1a14c3mvcjN67654/D5/jQw/e8fmP9zV3I+3z7ic/XnU5+vKqH459oetBwslVB7wtvWij88WpQeMWNFI2OzfjW9GhwwffOaJHKHJy+S/nzSAkXGTszi8nET7z2/vX30KimU+eOF3S+9EFH+JvWPb4Uas5/XSPMYAe2r26fObWALrh2Geplw19qF3TSKy8uQ+9fvDi9il9EF339m+7N80EUVLz8LpeLIRWfB0LbtkTQm8+0DjWgofRVuPOF768NYxOnqrs0usjKPjHiScH9kbQD8FP7afwKFqccXMjZnzuruQbX2z9rxl39woLsWwu4yr1jMPtzzbbv/tXApZKubYeL2Y2FJgMJ1KEDgzrtJDXGLFMriuYiW2ztDn+z6z/X/dnOtZiYu246ZPmVjm22ZCjJJYqmPfppmy8xHKVMSYrlESpYOu27pyy7QIbtGx5SkpzNofVJlEiBwapJAjQKxSpfBG6TqWdzUHTq7Y5ue2avho6qsMxxTtX87vQzTjPCezYQpuqa6xYzclGW0nimSyrSiiJuWp9IEtPcExRtotckWKpIgXWKRsnwXReSstThneEOjbbps8Ss1CFTVm+QIRq+psGXipu8ixWUDefJUDexLTDOh+isjhEZYkQ40KWWjLIWQN/D6NsK89RxWxe2brA03kqX5VX5apUPp8ty6smuXyBz0qy1eXpdHa6bNPz4c8a7Op0dbpt05i5iYzHtyW71YdgPmPcqBQyQJLkEKmWK0jSQ/rTZIgk02Qgrdj8/gXjZbkO1seDQwG1P+dFGY/KtV+p07X+3KSU7LKcSnp3pUYGoO2B9f7LoqJQGg0nPCNdg5N0JFGkpQF+G++nuWosT8Hc6EQ2HZViGVpkhShfTkdFb4ZODstzSmyyUugPkDzjjmcYaQhsZLnWn2QC0U3RvuG5vqD2Q76RK2UftViCL0eLcYELJ3bLcZLuAk+LoeLolTA37HXR4XIhGoiJVDJRGA35SqmkS5Dn0VKiQAfAj+QHXRDb5XNyI35B1ZooUcnBydHwMC/HhrlFJiKMsxGhrPgNxCZTYk5IuYfU8WTCmUrGM2w4KO8JziNRSnX5dsHeJcWfkBiO805PVHIt1D5/TnVdUUn1OSoKAh2Oj9f3Eog5lbNbSi+cP9uXctbO1kWP+L0j7riXCctnTPKgwzk4saRW5fzHQdNCDel/0uD5Zw2jBborNB9n8ZmJdNiXmdfpEthwCPIonqnfR8TFymtT7pgA9kmGh3URuM+wwDNiqMqpfspcMlRlRJ9b1TIqMNJgju7yKHsd2DFUGgh4KlHJKd97LVcHx1kxUWW6hEla9hmIVvsngqWBaswHSSy/ATJefwR9w8rLgsQmK/Wkl9/DXFGaHEmG5fcB7y1cswfkkZDyXlLwSsiB2rsZqq/LKDWzlD9WaabJPmU9o4pSSmh+Jtnbi5mtOSp/XYkrdjC5XIfyQbHWPhhW9VPS5rBgGPxhW4wYth3+1f4LjZMyFw==",
                }
            },
        ],
        "source_path": "tests/mocks",
    }
