import typing


T = typing.TypeVar('T')


def validate_instance(obj: T,
                      clz: type,
                      param_name: typing.Optional[str] = None) -> T:
    """
    Validate that `obj` is instance of `clz` or raise :class:`ValueError` otherwise.

    :param obj: and instance for validation.
    :param clz: the target class.
    :param param_name: name of the object to include in the error message.
    :return: the `obj` if the validation passes.
    :raise ValueError: if the instance check fails.
    """
    if not isinstance(obj, clz):
        if param_name is None:
            raise ValueError(f'The object must be an instance of {clz} but was {type(obj)}')
        else:
            raise ValueError(f'{param_name} must be an instance of {clz} but was {type(obj)}')
    return obj


def validate_optional_instance(obj: typing.Optional[T],
                               clz: type,
                               param_name: typing.Optional[str] = None) -> typing.Optional[T]:
    """
    Validate that `obj` is instance of `clz` or `None`, or raise :class:`ValueError` otherwise.

    :param obj: and instance for validation or `None`.
    :param clz: the target class.
    :param param_name: name of the object to include in the error message.
    :return: the `obj` if the validation passes.
    :raise ValueError: if `obj` is *not* `None` and the instance check fails.
    """
    if obj is not None:
        return validate_instance(obj, clz, param_name)
