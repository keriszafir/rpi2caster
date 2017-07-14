# -*- coding: utf-8 -*-
"""datatypes - custom data types and type handling functions for rpi2caster"""
from collections import Iterable, namedtuple, OrderedDict
from contextlib import suppress

# define aliases for boolean values
TRUE_ALIASES = ['true', 'on', 'yes', '1', 't', 'y']
FALSE_ALIASES = ['false', 'off', 'no', '0', 'f', 'n']

# start with an empty dictionary of types and limited parameters;
# after classes are defined, update it
TYPES = OrderedDict()
LIMITED_PARAMETERS = {len: 'length'}

# Type handling routines for common datatypes
# from_str: function converting a string to a value of this datatype,
# to_str: function transforming this datatype to string,
# validated_parameter : function(value) -> param. checked against limits
# type_name : string displayed in prompts, validation messages etc.,
# instancecheck: function used by the ValueListMetaclass
#       for checking the value type
#       isinstance(value, type) -> True if instancecheck returns True
Handler = namedtuple('TypeHandler',
                     ('from_str to_str validated_parameter '
                      'type_name instancecheck'))


def str_to_float(value):
    """Convert a string to float. Works with commas and dots as well."""
    # simplest approach first
    with suppress(ValueError):
        return float(value)

    # maybe it has a comma instead of dot?
    # (some locales use commas as decimal points)
    with suppress(AttributeError, ValueError):
        replaced_comma = value.replace(',', '.')
        return float(replaced_comma)

    # binary, hexadecimal and octal strings should be converted to int
    # then convert to float
    with suppress(ValueError):
        integer = int(value, base=0)
        return float(integer)

    # nothing else to do...
    raise TypeError('{} is not a valid real number'.format(value))


def str_to_int(value):
    """Convert a string to int.
    Floats will be rounded according to math rules.
    Hexstrings and binary strings will be converted as well."""
    # simplest approach first
    with suppress(ValueError):
        return int(value)

    # it may be a binary string or hexstring...
    with suppress(ValueError):
        return int(value, base=0)

    # it may be a float
    with suppress(AttributeError, ValueError):
        float_value = str_to_float(value)
        return round(float_value)

    # nothing else to do...
    raise TypeError('{} is not a valid integer number'.format(value))


def str_to_bool(value=None):
    """Convert a string to boolean.
    0, no, false, off, n, f, none, empty iterable, None, whitespace -> False
    1, yes, true, on, y, t -> True
    any other value -> None

    Failed conversion raises a TypeError with user-friendly message.
    """
    err = 'Invalid value: "{value}". Correct values: {correct}.'
    correct = TYPES[bool].type_name
    values = dict()
    values.update({name: True for name in TRUE_ALIASES})
    values.update({name: False for name in FALSE_ALIASES})
    # try the simplest approach first...
    if not value:
        return False

    # non-empty string/list/etc.? make a string and normalize it
    value_string = str(value).strip().lower()
    if not value_string:
        return False

    # look it up in valid values
    retval = values.get(value_string)

    # unknown values raise ValueError
    if retval is None:
        raise TypeError(err.format(value=value, correct=correct))

    # return True or False
    return retval


def get_type(value):
    """Determine a type of the value. If it fails, default to str."""
    # implementing this with singledispatch failed:
    # custom datatypes were not recognized
    if value is None:
        return None

    # iterate until a match is found
    for datatype, handler in TYPES.items():
        with suppress(TypeError):
            if handler.instancecheck(value):
                return datatype

    return str


def get_handler(datatype):
    """Get a type handler; unknown types will default to str."""
    return TYPES.get(datatype) or TYPES.get(str)


def get_string(value=None, datatype=str):
    """Get a printable string of a value that would act as a prefill
    value for input prompts."""
    to_str = get_handler(datatype).to_str
    return to_str('' if value is None else value)


def get_false_value(datatype):
    """Returns a value (of desired datatype) evaluating False."""
    for candidate in ('', [], (), 0, False):
        with suppress(TypeError, ValueError):
            ret = datatype(candidate)
            if not ret:
                # found a match!
                return ret

    # could not find a matching datatype value...
    return None


def convert_and_validate(value, default=None, datatype=None,
                         minimum=None, maximum=None,
                         condition=lambda x: True):
    """Wrap a function outputting a string to convert it,
    based on default value or explicitly specified type:

    If conversion fails, raises TypeError.
    If validation fails, raises ValueError.
    If no input and default is None, raises TypeError.

    value: a value to be checked,

    default: a value, exception or None.

             Empty input will result in raising an exception
             (if default is Exception subclass or its instance),
             or returning default value (coerced to a specified datatype).

    datatype: explicitly specified type.
              If None, default value's datatype will be used if possible;
              in case of exceptions etc. the function defaults to str.

    minimum, maximum : limits applying to validated parameter (length or value)
                       of the return value's datatype,

    condition: additional condition for validation to pass.
    """
    # desired type:
    # specified datatype -> type of default value -> string
    default_value_type = get_type(default)
    retval_datatype = datatype or default_value_type or str

    # no input? then raise any exceptions supplied in default value,
    # or return the default value itself
    if not value:
        # None is a special case, return it right away
        if default is None:
            raise ValueError('A value is required.')

        # return a default value then
        default_retval = try_raising(default)
        return default_retval or get_false_value(retval_datatype)

    # desired datatype handler provides info about what to validate
    retval_type_handler = get_handler(retval_datatype)
    validated_parameter = retval_type_handler.validated_parameter

    # convert, validate, return
    converted = convert(value, retval_datatype)
    validated = validate(converted,
                         validated_parameter, minimum, maximum, condition)
    return validated


def try_raising(value):
    """Try to raise an exception from option in the first place.
    Raises from classes (e.g. ValueError)
    or exception objects (e.g. ValueError('Incorrect value!'))

    If that fails, returns the value itself.
    """
    # raise TypeError classes and instances
    if value is TypeError or isinstance(value, TypeError):
        raise value

    # try to raise other exceptions
    try:
        raise value
    except TypeError:
        # it was not an exception after all
        return value


def itself(value):
    """Do-nothing function which returns the input value;
    used as an no-op implementation of converter for types that don't need it,
    equivalent to lambda value: value"""
    return value


def convert(value='', desired_type=str):
    """Converts a value to desired type
    and raises TypeError in case ValueError would normally be raised
    (avoiding TypeError in some cases and ValueError in others,
    e.g. converting a non-numeric string to int).

    Failed conversion raises a TypeError with a user-friendly message.
    """
    # maybe conversion is not necessary at all...
    source_value_type = get_type(value)
    if source_value_type == desired_type:
        return value

    # convert the source value to a string if it's not it
    source_type_handler = get_handler(source_value_type)
    source_to_string = source_type_handler.to_str
    value_string = source_to_string(value)

    # is an explanation available for the desired type?
    # look it up (not found -> None -> AttributeError -> generic message)
    try:
        type_definition = TYPES.get(desired_type)
        description = type_definition.type_name
        converter = type_definition.from_str
        exc_message = 'Wrong value type. Correct type: {}'.format(description)
    except AttributeError:
        exc_message = 'Wrong value type.'
        converter = desired_type

    # normally everything should be okay...
    # otherwise raise with a user-friendly message
    try:
        converted_value = converter(value_string)
        return converted_value
    except TypeError:
        raise TypeError(exc_message)
    except ValueError:
        raise TypeError(exc_message)


def validate(value, validated_parameter=None,
             minimum=None, maximum=None, condition=None):
    """Validate the value.

    Check condition, if specified. If it evaluates True, process further.

    If validated parameter and minimum and/or maximum is given, check limits.

    If any check evaluates False, raise ValueError and inform what went wrong.

    value : value to be checked,
    validated_parameter : fun(x)->limited parameter, or None (skip limit check)
                          (examples: lambda x: x; len)

    minimum, maximum : min and max value of the validated parameter for the
                       validation to pass, if specified.
                       If None, don't check this limit.

    condition : fun(x)->bool, or None (skip condition check)
                If retval evaluates False, fail validation.
    """
    # parameter name: if available, provide more info for the user
    try:
        name = LIMITED_PARAMETERS.get(validated_parameter)
        message = 'current {value_name} of {value} is {issue} than {limit}.'
    except AttributeError:
        name = ''
        message = 'value is {issue} than {limit}.'

    # check the value against condition
    if condition is not None and not condition(value):
        raise ValueError('value does not match conditions')

    # is there anything to check? if not, pass right away
    if not validated_parameter:
        return value

    # then check limits
    parameter_value = validated_parameter(value)

    if minimum is not None and parameter_value < minimum:
        # validation error
        error_data = dict(value_name=name, value=parameter_value,
                          issue='smaller', limit=minimum)
        raise ValueError(message.format(**error_data))

    if maximum is not None and parameter_value > maximum:
        # validation error
        error_data = dict(value_name=name, value=parameter_value,
                          issue='greater', limit=maximum)
        raise ValueError(message.format(**error_data))

    # validation pass
    return value


def make_handler(outer_type, inner_type):
    """Make a handler for container type for specified inner types"""
    container = Container(outer_type, inner_type)
    type_names = {int: 'integer numbers', float: 'decimal numbers'}
    name = type_names.get(inner_type, 'values')
    return Handler(from_str=container,
                   to_str=lambda v: ', '.join(str(i) for i in v),
                   validated_parameter=len,
                   instancecheck=container.instancecheck,
                   type_name='comma-separated {}'.format(name))


class Container:
    """A container (tuple, list) of specified inner types"""
    def __init__(self, outer_type, inner_type):
        self.outer_type = outer_type
        self.inner_type = inner_type

    def __call__(self, source):
        items = self.parse(source)
        return self.convert(items)

    @staticmethod
    def parse(source):
        """check and dispatch on inner value type"""
        if isinstance(source, str):
            items = (x.strip() for x in source.split(','))
        elif isinstance(source, Iterable):
            items = iter(source)
        else:
            # single item -> make a tuple
            items = (source, )

        return items

    def convert(self, items):
        """convert the values to a desired type"""
        collection = (convert(x, self.inner_type) for x in items)
        return self.outer_type(collection)

    def instancecheck(self, value):
        """check if we have the instance of this container"""
        checks = {int: lambda x: all(isinstance(v, int) for v in x),
                  float: lambda x: all(isinstance(v, (int, float)) for v in x),
                  str: ' '.join}
        try:
            check_inner = checks.get(self.inner_type)
            return isinstance(value, self.outer_type) and check_inner(value)
        except (TypeError, ValueError):
            return False


# itself function is defined => create a limit name for it
LIMITED_PARAMETERS[itself] = 'value'
# define datatype handlers
# and add them in the sequence from most to least specific
# (type checking is iterative and we don't want generic types like list
# to overshadow specific ones like list of integers)
TYPES[bool] = Handler(from_str=str_to_bool, to_str=str,
                      validated_parameter=None,
                      type_name='y/n, yes/no, on/off,  1/0, true/false, t/f',
                      instancecheck=lambda i: i is True or i is False)

TYPES[Exception] = Handler(from_str=itself, to_str=lambda _: '',
                           validated_parameter=len,
                           type_name='',
                           # is an exception object or Exception subclass
                           instancecheck=lambda i:
                           isinstance(i, Exception) or
                           isinstance(i, type) and issubclass(i, Exception))

TYPES[int] = Handler(from_str=str_to_int,
                     to_str=str,
                     validated_parameter=itself,
                     type_name='integer number e.g. 5',
                     instancecheck=lambda i: isinstance(i, int))

TYPES[float] = Handler(from_str=str_to_float,
                       to_str=lambda x: str(float(x)),
                       validated_parameter=itself,
                       type_name='decimal number e.g. 5.5',
                       instancecheck=lambda i: isinstance(i, float))

TYPES[str] = Handler(from_str=str, to_str=str,
                     validated_parameter=len,
                     type_name='',
                     instancecheck=lambda i: isinstance(i, str))

# add handlers for container types
for outer in (list, tuple, set):
    for inner in (int, float, str):
        TYPES[(outer, inner)] = make_handler(outer, inner)
    # add a generic list/tuple/set not specifying inner type
    TYPES[outer] = make_handler(outer, str)
