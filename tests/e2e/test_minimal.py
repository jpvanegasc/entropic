import pytest
import pandas as pd

from entropic import results
from entropic.process import Pipeline
from entropic.sources import Iteration


@pytest.fixture
def run_minimal_pipeline():
    class Process(Pipeline):
        source_path = "tests/mocks/"
        extract_with = pd.read_csv

    pipeline = Process()
    pipeline.run()


def test_minimal(run_minimal_pipeline):
    assert len(results.all) == 1

    result = results.all[0]
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
                    "raw": "eJw9lEmu3DAMBe+itSFwkij5XFkECP7dU7SiLNvdLJNv6D/td3v/NGmvPE3bq0+z9trTvL3+tGhvPG20dzxttnc+LdubT1vtXU/b7d1MMaw1XePMKwCFoCAUhgJRKApG4SgghaSgFJYCU2gKTuEZPINn8Kz2qYXgGTyDZ/AMnsEzeAbP4Bk8g2fwDJ7BM3gOz+E5PIfn8LwurBPhOTyH5/AcnsNzeA7P4Tk8h+fwHF7AC3gBL+AFvIAX8KI0K9HgBbyAF/ACXsALeAEv4AW8gDfgDfl52q/rRJfUOWNoyVGqds00S/PilhxdQnPNFbVA3dHVc2+zVZvWAt1sSw6fO4+B3WaoLhmSx0t+EWvmjPxna9dImWOq/3O4W/gey7xkL7PZY6aNmPLf9y6DRSzls/6LQI3NzVS9+qShq8w9tlqRTjB4Gz/YLqXByQiDyYI69/+4dGVmr1HCnuB0mbzfw7/MfBnqpjtWzvHt8MWpi9nwZXOOmyzu5VqZU+yGjEcy1pCy+8SNRW26SgX1BI8nmrHFt94M4o8zyOhNYxnkssPK4BPMLrWUzarCiWjXtQQX7Uvpl9ZuS1xWWgXoBLdcWBjlH+rLMGuO5IV8ceOMLitQPuqYk+yuM5cjy7oZ78L3GzdG3Lh3Haibrnvd5PcydCDftlsCBtPnkqzenT4QH1MjQeXgqUZXK69MvvZ8Lekma884y5/CsCmfkyd5u4PPe4zhMdetUSetKhlZ2pxG9ZKYLK564ykXQqzScC27PePqvbBxVdVP5TrH1ZnU47aP7RcHMa63iPhTWfM17HayY87MMPlYXz1xX0qcrH+G09RujmVz7PSfn78N+wJ7",
                    "filetype": "csv",
                }
            },
            {
                "data": {
                    "file_path": "tests/mocks/kinematic1.csv",
                    "raw": "eJw900uO3DAMRdG9aGwY/Ekiva4MAgS991zaUNfQKB2R4uO/8Wc8/4aMR66h49Fr2HjsGj4ev0aMJ64xxzOvscazrrHHs6+R48lr1HiKUxzWPt3HOa8AiqAQiqEgiqIwiqNAiqRQiqVgiqZwimd4hmd41vV0QXiGZ3iGZ3iGZ3iGZ3iGZ3iGZ3iGZ3iO53iO53iO591ht4jneI7neI7neI7neI7neI7neI4XeIEXeIEXeIEXeNFv1o+GF3iBF3iBF3iBF3iBF3iBN/Gm/Fzj75nELSJLLHPvbyi3aLhtUalvPrdkLauQvqD7uGXOiiyV9U3tlohIXdZP0gPkg2fCZH6z5EghzOpH6bFyrdbOkP7QE+aDT1tz94ceNnWYrjCZeuZOJV6e23tEXwQ4ZmvvXOuE4ZYVIqU26+Si69tWuleciNyyNabPeqk3LVBRuyr95OYWA6qa8yQIKWctl279CxOtueha1u/15er9lGKV+0TsFjetXB3GL2xUMCmBqubJHf2pLdudlC+BPYyk0lx1wkhR5TstRU8uuY//hEavwhfRLkGLL+s3rVzoM9Pz5d/gwjNFfttOhnk+d91hHfcvztyYM9S1N+hL9tvO69UJeT+yuNBhnrzfUp0L8/kb/Q5TmIfp7xZwIw9apv0230Jg2VpU0fn5doMiwpU+3xvfNaHHNZ1cddvfxtDjzpoyU8/y8C/eaqn13n57xKR5BOdrnJXqG5MRxtazXVRP17b0rFlnlqC1dTaOqqYzjSl2lo92rKrWtx3vHnZVbjx8P823kjwg0aPWWmc7KYHN83DZZ1GxylmbVfrz8x8asQG9",
                    "filetype": "csv",
                }
            },
        ],
        "source_path": "tests/mocks/",
    }
