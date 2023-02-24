0.15.0 (unreleased)
===================

- Added support for Inverse Nonlinearity data model, maker utilities, and tests. [#125]


0.14.1 (2023-01-31)
===================

- Move metadata to ``pyproject.toml`` in accordance with PEP621 [#100]
- Cleanup ``enum`` validation code. [#112]
- Add ``pre-commit`` support. [#119]
- Apply ``isort`` and ``black`` code formatters to all files. [#120]
- Switch from ``flake8`` to ``ruff`` for code linting. [#121]
- Start using ``codespell`` for automated spell checking. [#122]

0.14.0 (2022-11-14)
===================

- Explicitly add ``gwcs`` to the list of dependencies. [#108]
- Remove the unused ``stnode_test`` module. [#110]
- Add support for non-VOUnits to be used by Roman. [#109]
- Changed science arrays to quantities. [#111]


0.13.0 (2022-08-23)
===================

- pin ``asdf`` above ``2.12.1`` to fix issue with `jsonschema` release [#91]
- Add ability to access information stored in ``rad`` schemas relative to the information stored in the datamodel. [#93]
- Add ``IPAC/SSC`` as valid ``origin`` values. [#95]

0.12.3 (2022-08-09)
===================

- Removed CRDS version information from basic maker utility. [#80]

- Updated utilities and test for change in dimensionality of err variable in ramp datamodel. [#82]

- Add support for new ``rad`` schema tags. [#86, #90]

- Removed keywords from guidestar. [#88]

- Fixed format of exposure times factory functions, changed filter 'W146' to 'F146'. [#87]

- Update create_ref_file() to match updated schema. [#89]

0.12.2 (2022-04-26)
===================

- Added function for model equality. [#79]

0.12.1 (2022-04-26)
===================
- Removed ``observation.date`` and ``observation.time`` from CRDS parameters. [#78]

0.12.0 (2022-04-25)
===================

- Setup the initial infrastructure and basic files for documenting the roman_datamodels package [#67]

- Fix bug with asdf.fits_embed. [#69]

- Added distortion data model, utilities, and tests. [#70]

- Removed exptype and p_keyword from Distortion maker utility and factory. [#71]

- Updated photom maker utilities and tests. [#72]

- Corrected photom units to megajanskies. [#73]

- Moved ma_table_name and ma_table_number from observation to exposure groups. [#74]

- Update astropy min version pin to 5.0.4. [#75]

- Add utilities for ``ref_file``. [#76]

0.10.0 (2022-02-15)
===================

- Updated maker utility and factory for dark ref model to include group keywords from exposure. [#66]

- Updated maker utilities for level 1, level 2, and ramp models to reflect changes in reference pixels. [#65]


0.9.0 (2022-02-04)
==================

- Updated rampfit and flat maker utilities to support the same functionality as the other model maker functions. Streamlined and commented all maker utility functions. Added tests to complete coverage of roman_datamodels/testing/utils.py. Cleaned out some deprecated code. [#59]

- Updated stnode tests to include all cal steps. [#60]

- Fix bug with asdf 2.9.x due to change in private variable name. [#63]

0.8.0 (2021-11-22)
==================

- Add support for the cal_logs array, which will be used to store calibration
  log messages. [#53]

0.7.0 (2021-11-10)
==================

- Modified DNode and LNode classes to provide asdf info method introspection
  into the contents of the class. [#61]

- Modified open function to handle accepting model instances that are checked
  against a target datamodel class, whether supplied directly as a model instance,
  or obtained by the referenced ASDF file. [#52]

- Created maker utility and tests for ramp_fit_output files. [#50]

0.6.0 (2021-10-26)
==================

- Reverted Exposure time types from string back to astropy Time. [#49]

- Added ability to add attributes to datamodels [#33]

- Added support for Saturation reference files. [#37]

- Updated Ramp Pedestal Array to 2D. Fixed reference model casting in test_models. [#38]

- Implemented support and tests for linearity reference model. Corrected dimension order in factories. Added primary array definition to MaskRefModel. [#39]

- Updated tests and makers for exposure and optical_element requirements in reference files. [#42]

- Changed exposure ``start_time``, ``mid_time``, and ``end_time`` to string to match RAD update. [#40]

- Implemented support, tests, and maker utility for Super Bias reference files. [#45]

- Created maker utility and tests for wfi photom reference files. [#43]

- Added support, tests, and maker utility for Pixel Area reference files. [#44]

- Added check to ensure opening a Roman file with datamodel class
  that doesn't match the class implied by the tag raises an exception. [#35]

0.5.2 (2021-08-26)
==================

- Updated ENGINEERING value to F213 in optical_element. [#29]

- Workaround for setuptools_scm issues with recent versions of pip. [#31]

0.5.1 (2021-08-24)
==================

- Added tests for mask maker utility. [#25]

- Added Dark Current model maker and tests. [#26]

- Added Readnoise maker utility and tests. [#23]

- Added Gain maker utility and tests. [#24]

0.5.0 (2021-08-07)
==================

0.4.0 (2021-08-06)
==================

- Added support for ScienceRawModel. Removed basic from ref_common in testing/utils. [#20]

- Added support for dq_init step in cal_step. [#18]

0.3.0 (2021-07-23)
==================

- Added code for DQ support. Added ramp and mask helper functions. Removed refout and zeroframe. [#17]

0.2.0 (2021-06-28)
==================

- Added support for ramp, ramp_fit_output, wfi_img_photom models. [#15]

- Set rad requirement to 0.2.0 and update factories and tests.  Add ``DarkRefModel``,
  ``GainRefModel``, and ``MaskRefModel``. [#11]
