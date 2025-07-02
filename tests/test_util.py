import typing
import gzip
import pathlib

import pytest

from hpotk.util import open_text_io_handle_for_writing, open_text_io_handle_for_reading


class TestOpenIoForWriting:
    @pytest.fixture(scope="class")
    def payload(self) -> typing.Sequence[str]:
        return ["abc\n", "def\n", "123\n"]

    @pytest.fixture(scope="function")
    def tmp_file(
        self,
        tmp_path: pathlib.Path,
    ) -> pathlib.Path:
        return tmp_path.joinpath("something.csv.gz")

    def test_works_with_path_and_hpotk(
        self,
        payload: typing.Sequence[str],
        tmp_file: pathlib.Path,
    ):
        with open_text_io_handle_for_writing(tmp_file) as fh:
            fh.writelines(payload)

        with open_text_io_handle_for_reading(tmp_file) as fh:
            actual = fh.readlines()

        assert actual == payload

    def test_works_with_path_and_gzip(
        self,
        payload: typing.Sequence[str],
        tmp_file: pathlib.Path,
    ):
        with open_text_io_handle_for_writing(tmp_file) as fh:
            fh.writelines(payload)

        with gzip.open(tmp_file, "rt") as fh:
            actual = fh.readlines()

        assert actual == payload
