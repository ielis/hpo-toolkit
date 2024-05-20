import gzip
import io
import logging
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
    return file.startswith('http://') or file.startswith('https://')


def looks_gzipped(file: str) -> bool:
    """
    Checks file suffix to determine if it looks gzipped.

    :param file: file path to check.
    :return: `True` if the `file` ends with `.gz`.
    """
    return file.endswith('.gz')


def _parse_encoding(encoding, logger) -> str:
    if encoding is None:
        encoding = sys.getdefaultencoding()
        logger.debug(f'Using default encoding \'{encoding}\'')
    else:
        logger.debug(f'Using provided encoding \'{encoding}\'')
    return encoding


def open_text_io_handle_for_reading(
        fh: typing.Union[typing.IO, str],
        timeout: int = 30,
        encoding: str = None,
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
    logger = logging.getLogger('hpotk.util')
    encoding = _parse_encoding(encoding, logger)

    logger.debug(f'Opening {fh}')
    if isinstance(fh, str):
        # Can be a path to local file or URL
        if looks_like_url(fh):
            ctx = ssl.create_default_context(cafile=certifi.where())
            logger.debug(f'Looks like a URL: {fh}')
            if not isinstance(timeout, int) or timeout <= 0:
                raise ValueError(f'If {fh} looks like URL then timeout {timeout} must be a positive `int`')
            logger.debug(f'Downloading with timeout={timeout}s')
            handle = urlopen(
                fh,
                timeout=timeout,
                context=ctx,
            )
        else:
            logger.debug(f'Looks like a local file: {fh}')
            handle = open(fh, 'rb')

        if looks_gzipped(fh):
            logger.debug(f'Looks like a gzipped data, decompressing on the fly')
            return gzip.open(handle, mode='rt', newline='', encoding=encoding)
        else:
            logger.debug(f'Looks like decompressed data')
            return io.TextIOWrapper(handle, encoding=encoding)
    elif isinstance(fh, typing.IO):
        if isinstance(fh, typing.BinaryIO):
            logger.debug(f'Looks like a binary IO')
            return io.TextIOWrapper(fh, encoding=encoding)
        elif isinstance(fh, typing.TextIO):
            return fh
        else:
            raise ValueError(f'Unexpected type {type(fh)}')
    else:
        raise ValueError(f'Unexpected type {type(fh)}')


def open_text_io_handle(fh: typing.Union[typing.IO, str],
                        timeout: int = 30,
                        encoding: str = None) -> typing.TextIO:
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
    warnings.warn('The method has been deprecated and will be removed in v1.0.0. '
                  'Use `open_text_io_handle_for_reading` instead', DeprecationWarning, stacklevel=2)
    return open_text_io_handle_for_reading(fh, timeout, encoding)


def open_text_io_handle_for_writing(fh: typing.Union[str, typing.IO],
                                    encoding: str = None) -> typing.TextIO:
    """
    Open a `io.TextIO` file handle based on `fpath`.

    :param fh: a `str` with a path to a local file The content will be compressed on the fly if the file name ends
      with `.gz`.
    :param encoding: encoding used to encode the output or the system preferred encoding if unset.
    :return: a :class:`io.TextIO` wrapper.
    """
    logger = logging.getLogger('hpotk.util')
    encoding = _parse_encoding(encoding, logger)

    if isinstance(fh, str):
        if looks_gzipped(fh):
            logger.debug(f'Looks like a gzipped data, compressing on the fly')
            return gzip.open(fh, mode='wt', newline='', encoding=encoding)
        else:
            return open(fh, 'w')
    elif isinstance(fh, typing.BinaryIO):
        logger.debug(f'Looks like a binary IO')
        return io.TextIOWrapper(fh, encoding=encoding)
    elif isinstance(fh, typing.TextIO):
        return fh
    else:
        raise ValueError(f'Unexpected type {type(fh)}')
