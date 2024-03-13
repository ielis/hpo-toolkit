from . import sort  # TODO: probably not necessary

from ._io import looks_like_url, looks_gzipped
from ._io import open_text_io_handle, open_text_io_handle_for_reading, open_text_io_handle_for_writing
from ._log import setup_logging, DEFAULT_LOG_FMT
from ._validate import validate_instance, validate_optional_instance

__all__ = [
    'looks_like_url', 'looks_gzipped',
    'open_text_io_handle_for_reading', 'open_text_io_handle_for_writing',
    'setup_logging', 'DEFAULT_LOG_FMT',
    'validate_instance', 'validate_optional_instance'
]
