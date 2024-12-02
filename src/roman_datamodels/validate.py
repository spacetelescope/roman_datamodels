"""
Functions that support validation of model changes
"""

import os
import warnings
from contextlib import contextmanager
from textwrap import dedent

from asdf import schema as asdf_schema

__all__ = [
    "ValidationWarning",
]

ROMAN_VALIDATE = "ROMAN_VALIDATE"
ROMAN_STRICT_VALIDATION = "ROMAN_STRICT_VALIDATION"


def validation_is_disabled():
    MESSAGE = dedent(
        """\
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            !!!! VALIDATION HAS BEEN DISABLED GLOBALLY !!!!!
            !!!! THIS is EXTREMELY DANGEROUS AND MAY   !!!!!
            !!!! RESULT IN SITUATIONS WHERE DATA       !!!!!
            !!!! CANNOT BE WRITTEN AND/OR READ!        !!!!!
            !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            We strongly suggest that you do not turn off
            validation. If you do, you do so at your own
            risk. YOU HAVE BEEN WARNED!

            To turn validation back on, unsent the
            environment variable ROMAN_VALIDATE or set it
            to "true".
        """
    )
    warnings.warn(MESSAGE, ValidationWarning, stacklevel=2)


def will_validate():
    """
    Determine if validation is enabled.
    """
    var = os.getenv(ROMAN_VALIDATE)

    if not (validate := var is None or var.lower() in ["true", "yes", "1"]):
        validation_is_disabled()

    return validate


class ValidationWarning(Warning):
    pass


@contextmanager
def nuke_validation():
    """
    Context manager to temporarily turn all ASDF validation off.
    """

    # Don't nuke validation if we validation is enabled
    if will_validate():
        yield
        return

    ########################### NUKE VALIDATION ###############################
    # This is a horrible hack to disable validation, and is quite dangerous.  #
    # Monkey patching like this is a bad idea, but it is the only way to      #
    # cleanly turn off validation in ASDF, without refactoring large portions #
    # of the ASDF code base. The ASDF package has no intention of supporting  #
    # turning off validation for writing files as this is a bad idea. So,     #
    # we are left with this.                                                  #
    ###########################################################################

    # Save validation function to restore it later
    validate = asdf_schema.validate

    # Monkey patch validation with a function that does nothing
    def _no_validation_for_you(*args, **kwargs):
        pass

    asdf_schema.validate = _no_validation_for_you

    yield

    # Restore validation function upon exit of the context
    asdf_schema.validate = validate
