import pytest
import pandas as pd
from pydantic import ValidationError

from entropic.sources.fields import DataSource

TEST_DATA_FRAME = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})


def test_raw_validation_and_serialization():
    with pytest.raises(ValidationError) as error:
        DataSource(file_path="", raw="invalid df")
    assert "unable to load a `pandas.DataFrame` object from raw" in str(error.value)

    valid = DataSource(file_path="some_path", raw=TEST_DATA_FRAME)
    assert isinstance(valid.model_dump()["raw"], str)


def test_comparisons():
    assert DataSource(file_path="some_path", raw=TEST_DATA_FRAME) == DataSource(
        file_path="some_path", raw=TEST_DATA_FRAME
    )
    assert DataSource(file_path="some_path", raw=TEST_DATA_FRAME) != DataSource(
        file_path="other_path", raw=TEST_DATA_FRAME
    )
    assert (
        DataSource(file_path="some_path", raw=TEST_DATA_FRAME)
        != "not a data source instance"
    )


def test_dump_and_load_compressed():
    compressed = DataSource._dump_data_frame(TEST_DATA_FRAME)
    assert (
        compressed
        == "eJy1Vk9v4kYUN2BRKvUQrWoEUg7IalEPSYod2F1W28PYCWAK7EI22LiqIv8LGGzj+k8MifgGPfTQ3vtxeuyhh36AfpDOjMEBwlZaqRlFeTO/9+b3fm9mnsV7MGAokipRX3WgIV4QxNHbFBGP9NpSBPWCyp9A/xGVpbLHhdzGU8htYvPENwdQOD4vIZhMpTLp8t+pY4os1ojsUbFAanOLodJ5Mv9HKv9nqtwq5z6FuIjkEFQaiTuiUMB+FZl1JPnRKsiENrOV7Cm6V8U/5G4V7FYVf2XKv2Y+hfpQHcW3NaKQ9bWJYSsUCYGv0/FxPU5ZIk8Wj4snz3ukz11q/pdMnizn8r9nvkTuQtZVHF3xC7+RD7Tp6MbiBuYMbcen35R+eKBnEIMz2lOcsUGflGhHsQ0IOKFlwZUfKF4AlxU8n7twyuKpgabM6ke4iPluMLmxpt1luTUNS7/ZxWJZN8HSRSAdOqY212MFoe0uE8dcnRpagHDbCBRdCRSIPtCGA8NNZ4xCrj80Tl/Tqy0xuyoQyND7OhJ0T4npBC+rT3Uk8JYMVMrqpLSTiD2YiP0fEuHyPEMJ5h4+AstUPcVboj3uUvG8eYR23Rmeb84dhDLVs8oZQ68eU2852TPm7JxeEYUvwGDwTnwTt0bh59y3aETgAgDQB/H4HoAq4MagAcAY8GOMcdyOP0L2MvFfRny83rBgv4Ashy0mmSHDYbZrGM+9EmwrlJvDqsT27tTWMFCdrvnO5FRj2fYUsTYTpvOx4LQnqq1bghmNBbs2UcVrFBPq4sLv8MDUzgcTzelDDETr9Z3GCy+FC8EX+Pa93hxGiKcrMTryj9i6r4tMKLFxbllKcoYjkbFQrOoMfZVH+WRXFhcziT2Qt9mA+xv30vmgpjWRD5i6WHMh/0y+wrlhLBMZw3rFkDjMK9h1U7GHU53H/kCWBhPIURldQb0t35TF2lRlB65qa5hvOBw0Ox/G5u2edm0J4xvBq8fziH3dOK+tiENfbtSTegQbnu/Fpfkx3fCsK71pH/th7YHWsm71lhXJSBffdlWnz/YOaW7WGLW5qHd47qkW87+0CM+mRbpC99ZbymKjop4L6M6gtoU7gu9Ic2Y4B+SE8/advsQ8rCy17xWxHmJ908tKZwrC7lW7vqtRtjSn56psFXN0zeqiM+2at/i9j9CjjkbwzY6kbvz0ASfgp47+9S5gk71GLcLjJuHGIOmXpGk4ePfREi+7m3jA9dckDUw6gllAd715048cmGA7TvLFA/Pju4gjcT/CxmutQx/54/EdUSi5ivdTaASnmuue4o9Maf0RKcWfl+LJMUHAP0L/jCDew18+/wJpdjgg"
    )

    decompressed = DataSource._load_data_frame(compressed)
    assert isinstance(decompressed, pd.DataFrame)
    assert (
        from_load.all() == from_test.all()
        for from_load, from_test in zip(decompressed.all(), TEST_DATA_FRAME.all())
    )
