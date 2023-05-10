"""
Functions that support validation of model changes
"""

import os
import warnings
from textwrap import dedent

import jsonschema
from asdf import AsdfFile
from asdf import schema as asdf_schema
from asdf import yamlutil
from asdf.util import HashableDict

__all__ = [
    "ValidationWarning",
    "value_change",
]

ROMAN_VALIDATE = "ROMAN_VALIDATE"
ROMAN_STRICT_VALIDATION = "ROMAN_STRICT_VALIDATION"


def validation_is_disabled():
    MESSAGE = dedent(
        """\
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            !!!! VALIDATION HAS BEEN DISABLED        !!!!!
            !!!! THIS is EXTREMELY DANGEROUS AND MAY !!!!!
            !!!! RESULT IN SITUATIONS WHERE DATA     !!!!!
            !!!! CANNOT BE WRITTEN AND/OR READ!      !!!!!
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            We strongly suggest that you do not turn off
            validation. If you do, you do so at your own
            risk. YOU HAVE BEEN WARNED!

            To turn validation back on, unsent the
            environment variable ROMAN_VALIDATE or set it
            to "true".
        """
    )
    warnings.warn(MESSAGE, ValidationWarning)


def will_validate():
    """
    Determine if validation is enabled.
    """
    var = os.getenv(ROMAN_VALIDATE)

    if not (validate := var is None or var.lower() in ["true", "yes", "1"]):
        validation_is_disabled()

    return validate


def strict_validation_is_disabled():
    MESSAGE = dedent(
        """\
            Strict validation has been disabled. This may result
            in validation errors arising when writing data.

            To turn strict validation back on, unset the
            environment variable ROMAN_STRICT_VALIDATION or set
            it to "true".
        """
    )

    warnings.warn(MESSAGE, ValidationWarning)


def will_strict_validate():
    """
    Determine if strict validation is enabled.
    """
    var = os.getenv(ROMAN_STRICT_VALIDATION)

    if not (validate := var is None or var.lower() in ["true", "yes", "1"]):
        strict_validation_is_disabled()

    return validate


class ValidationWarning(Warning):
    pass


def value_change(value, pass_invalid_values, strict_validation):
    """
    Validate a change in value against a schema.
    Trap error and return a flag.
    """
    try:
        _check_value(value)
        update = True
    except jsonschema.ValidationError as errmsg:
        update = False
        if pass_invalid_values:
            update = True
        if strict_validation:
            raise errmsg
        else:
            warnings.warn(errmsg, ValidationWarning)
    return update


def _check_type(validator, types, instance, schema):
    """
    Callback to check data type. Skips over null values.
    """
    if instance is None:
        errors = []
    else:
        errors = asdf_schema.validate_type(validator, types, instance, schema)
    return errors


validator_callbacks = HashableDict(asdf_schema.YAML_VALIDATORS)
validator_callbacks.update({"type": _check_type})


def _check_value(value):
    """
    Perform the actual validation.
    """

    validator_context = AsdfFile()

    if hasattr(value, "_schema"):
        temp_schema = value._schema()
    else:
        temp_schema = {"$schema": "http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema"}
    validator = asdf_schema.get_validator(temp_schema, validator_context, validators=validator_callbacks)

    value = yamlutil.custom_tree_to_tagged_tree(value, validator_context)
    validator.validate(value, _schema=temp_schema)
    validator_context.close()


def _error_message(path, error):
    """
    Add the path to the attribute as context for a validation error
    """
    if isinstance(path, list):
        spath = [str(p) for p in path]
        name = ".".join(spath)
    else:
        name = str(path)

    error = str(error)
    if len(error) > 2000:
        error = error[0:1996] + " ..."
    errfmt = "While validating {} the following error occurred:\n{}"
    errmsg = errfmt.format(name, error)
    return errmsg
