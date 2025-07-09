import gzip
import io
import logging
import pathlib
import ssl
import sys
import typing
import warnings
from urllib.request import urlopen

import certifi


def looks_like_url(file: str) -> bool:
    """
    Checks if the `file` looks like a URL.

    :param file: file to check.
    :return: `True` if the `file` starts with `http://` or `https://`.
    """
    return file.startswith("http://") or file.startswith("https://")


def looks_gzipped(file: str) -> bool:
    """
    Checks file suffix to determine if it looks gzipped.

    :param file: file path to check.
    :return: `True` if the `file` ends with `.gz`.
    """
    return file.endswith(".gz")


def _parse_encoding(
    encoding: typing.Optional[str],
    logger: logging.Logger,
) -> str:
    if encoding is None:
        encoding = sys.getdefaultencoding()
        logger.debug("Using default encoding '%s'", encoding)
    else:
        logger.debug("Using provided encoding '%s'", encoding)
    return encoding


def open_text_io_handle_for_reading(
    fh: typing.Union[typing.TextIO, typing.BinaryIO, pathlib.Path, str],
    timeout: int = 30,
    encoding: typing.Optional[str] = None,
) -> typing.TextIO:
    """
    Open a `io.TextIO` file handle based on `fh`.

    :param fh: a `str` or `typing.IO` to read from. If `str`, then it should be a path to a local file or a URL
      of a remote resource. Either `http` or `https` protocols are supported. The content will be uncompressed
      on the fly if the file name ends with `.gz`. If `fh` is an IO wrapper, the function ensures we get a text wrapper
      that uses given encoding.
    :param timeout: timeout in seconds used when accessing a remote resource.
    :param encoding: encoding used to decode the input or the system preferred encoding if unset.
    :return: the :class:`io.TextIO` wrapper.
    """
    logger = logging.getLogger("hpotk.util")
    encoding = _parse_encoding(encoding, logger)

    logger.debug(f"Opening {fh}")
    if isinstance(fh, (pathlib.Path, str)):
        # Can be a path to local file or URL
        fp = str(fh)
        if looks_like_url(fp):
            ctx = ssl.create_default_context(cafile=certifi.where())
            logger.debug("Looks like a URL: %s", fp)
            if not isinstance(timeout, int) or timeout <= 0:
                raise ValueError(f"If {fp} looks like URL then timeout {timeout} must be a positive `int`")
            logger.debug("Downloading with timeout=%ds", timeout)
            handle = urlopen(
                fp,
                timeout=timeout,
                context=ctx,
            )
        else:
            logger.debug("Looks like a local file: %s", fp)
            handle = open(fp, "rb")

        if looks_gzipped(fp):
            logger.debug("Looks like a gzipped data, decompressing on the fly")
            return gzip.open(handle, mode="rt", newline="", encoding=encoding)
        else:
            logger.debug("Looks like decompressed data")
            return io.TextIOWrapper(handle, encoding=encoding)
    elif isinstance(fh, typing.IO):
        if isinstance(fh, typing.BinaryIO):
            logger.debug("Looks like a binary IO")
            return io.TextIOWrapper(fh, encoding=encoding)
        elif isinstance(fh, typing.TextIO):
            return fh
        else:
            raise ValueError(f"Unexpected type {type(fh)}")
    else:
        raise ValueError(f"Unexpected type {type(fh)}")


def open_text_io_handle(
    fh: typing.Union[typing.TextIO, typing.BinaryIO, str],
    timeout: int = 30,
    encoding: typing.Optional[str] = None,
) -> typing.TextIO:
    """
    Open a `io.TextIO` file handle based on `fh`.

    :param fh: a `str` or `typing.IO` to read from. If `str`, then it should be a path to a local file or a URL
      of a remote resource. Either `http` or `https` protocols are supported. The content will be uncompressed
      on the fly if the file name ends with `.gz`. If `fh` is an IO wrapper, the function ensures we get
      a text wrapper that uses given encoding.
    :param timeout: timeout in seconds used when accessing a remote resource.
    :param encoding: encoding used to decode the input or the system preferred encoding if unset.
    :return: the :class:`io.TextIO` wrapper.
    """
    # REMOVE(v1.0.0)
    warnings.warn(
        "The method has been deprecated and will be removed in v1.0.0. Use `open_text_io_handle_for_reading` instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return open_text_io_handle_for_reading(fh, timeout, encoding)


def open_text_io_handle_for_writing(
    fh: typing.Union[typing.TextIO, typing.BinaryIO, pathlib.Path, str],
    encoding: typing.Optional[str] = None,
) -> typing.TextIO:
    """
    Open a `io.TextIO` file handle based on `fpath`.

    :param fh: a `str` with a path to a local file The content will be compressed on the fly if the file name ends
      with `.gz`.
    :param encoding: encoding used to encode the output or the system preferred encoding if unset.
    :return: a :class:`io.TextIO` wrapper.
    """
    logger = logging.getLogger("hpotk.util")
    encoding = _parse_encoding(encoding, logger)

    if isinstance(fh, (pathlib.Path, str)):
        fp = str(fh)
        if looks_gzipped(fp):
            logger.debug("Looks like gzipped data, compressing on the fly")
            return gzip.open(fh, mode="wt", newline="", encoding=encoding)
        else:
            return open(fh, "w")
    elif isinstance(fh, typing.BinaryIO):
        logger.debug("Looks like a binary IO")
        return io.TextIOWrapper(fh, encoding=encoding)
    elif isinstance(fh, typing.TextIO):
        return fh
    else:
        raise ValueError(f"Unexpected type {type(fh)}")
