import logging

DEFAULT_LOG_FMT = '%(asctime)s %(name)-20s %(levelname)-3s : %(message)s'


def setup_logging(level: int = logging.INFO,
                  log_fmt: str = DEFAULT_LOG_FMT):
    """
    Create a basic configuration for the logging library. Set up console and file handler using provided `log_fmt`.

    The `level` signifies the desired verbosity.
    Use:

    - `10` for `DEBUG`
    - `20` for `INFO`
    - `30` for `WARNING`
    - `40` for `ERROR`
    - `50` for `CRITICAL`

    :param level: the verbosity to use, `INFO` by default.
    :param log_fmt: format string for logging.
    """
    # create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter(log_fmt)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

