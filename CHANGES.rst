0.26.0 (2025-07-17)
===================

Bug Fixes
---------

- Fix meta.filename for writing to parquet. (`#513
  <https://github.com/spacetelescope/roman_datamodels/issues/513>`_)
- Fix bug in RDM caused by RAD's new "static" manifest. (`#518
  <https://github.com/spacetelescope/roman_datamodels/issues/518>`_)
- Use basenames in meta.filename in parquet metadata. (`#520
  <https://github.com/spacetelescope/roman_datamodels/issues/520>`_)
- Fix bug where DataModel.__deepcopy__ returned a shallow copy. (`#522
  <https://github.com/spacetelescope/roman_datamodels/issues/522>`_)
- Preserves the datatype of filename. (`#527
  <https://github.com/spacetelescope/roman_datamodels/issues/527>`_)
- Remove use of out of date ``exposure_types``. (`#537
  <https://github.com/spacetelescope/roman_datamodels/issues/537>`_)


New Features
------------

- Add ``DataModel.from_schema`` and ``DataModel.fake_data``. (`#514
  <https://github.com/spacetelescope/roman_datamodels/issues/514>`_)
- Update ``roman_datamodels`` to support moving ``mosaic.cal_logs`` to
  ``mosaic.meta.cal_logs`` for consistency with ``wfi_image.meta.cal_logs``.
  (`#516 <https://github.com/spacetelescope/roman_datamodels/issues/516>`_)
- Implement __dir__ for nodes and datamodels. (`#524
  <https://github.com/spacetelescope/roman_datamodels/issues/524>`_)
- Use schemas to check source catalog tables.
  Introduce ForcedImageSourceCatalogModel, ForcedMosaicSourceCatalogModel and
  MultibandSourceCatalogModel. (`#529
  <https://github.com/spacetelescope/roman_datamodels/issues/529>`_)
- Update maker_utils based on level 3 MosaicModel metadata updates and improve
  support for items for create_fake_data. (`#536
  <https://github.com/spacetelescope/roman_datamodels/issues/536>`_)
- Add support for the ``all_array_storage`` save option for asdf files to
  ``DataModel.save`` method. (`#540
  <https://github.com/spacetelescope/roman_datamodels/issues/540>`_)


0.25.0 (2025-05-12)
===================

Bug Fixes
---------

- Use asdf to validate before saving catalog to parquet. (`#503
  <https://github.com/spacetelescope/roman_datamodels/issues/503>`_)
- Fix bug where nodes couldn't be deepcopied after use. (`#511
  <https://github.com/spacetelescope/roman_datamodels/issues/511>`_)


Documentation
-------------

- Remove duplicate build section from readthedocs config. (`#501
  <https://github.com/spacetelescope/roman_datamodels/issues/501>`_)


New Features
------------

- Adds basic keyword group to both L1 Guidewindow datamodels (`#509
  <https://github.com/spacetelescope/roman_datamodels/issues/509>`_)


Deprecations and Removals
-------------------------

- Remove MosaicModel.append_individual_meta (`#485
  <https://github.com/spacetelescope/roman_datamodels/issues/485>`_)


0.24.2 (2025-04-30)
===================

Bug Fixes
---------

- Use a non-root logger. (`#506
  <https://github.com/spacetelescope/roman_datamodels/issues/506>`_)


0.24.0 (2025-04-18)
===================

New Features
------------

- Added datamodels for MA Tables reference files. Tests are added, and a couple
  adjusted for the integer keywords in the datamodel. (`#469
  <https://github.com/spacetelescope/roman_datamodels/issues/469>`_)
- MosaicSourceCatalogModel and ImageSourceCatalogModel now can be serialized to
  parquet format using the ``to_parquet`` method. (`#473
  <https://github.com/spacetelescope/roman_datamodels/issues/473>`_)
- Added epsf and apcorr to ref_files and ref_files to image_source_catalog.
  (`#474 <https://github.com/spacetelescope/roman_datamodels/issues/474>`_)
- Create the WfiWcsModel (`#477
  <https://github.com/spacetelescope/roman_datamodels/issues/477>`_)
- Allow source catalog models to be saved with parquet extension. (`#484
  <https://github.com/spacetelescope/roman_datamodels/issues/484>`_)
- Added astropy table metadata to parquet catalog files. (`#488
  <https://github.com/spacetelescope/roman_datamodels/issues/488>`_)
- Added L1 Detector-Level Guide Window File Datamodels, maker utilities, and
  tests. (`#489
  <https://github.com/spacetelescope/roman_datamodels/issues/489>`_)
- Added L1 Average FACE Guide Window File Datamodels, maker utils, & test.
  (`#492 <https://github.com/spacetelescope/roman_datamodels/issues/492>`_)


Misc
----

- test with latest supported Python version (`#463
  <https://github.com/spacetelescope/roman_datamodels/issues/463>`_)
- This PR adjusts several RTB directed L1 & L2 metadata datamodel changes,
  tests, and TVAC/FPS conversions. (`#487
  <https://github.com/spacetelescope/roman_datamodels/issues/487>`_)


0.23.1 (2025-02-14)
===================

New Features
------------

- Added support for skycell reference file (`#441
  <https://github.com/spacetelescope/roman_datamodels/issues/441>`_)
- Start versioning files by allows Node instances to use multiple versions of
  tags. (`#445
  <https://github.com/spacetelescope/roman_datamodels/issues/445>`_)
- Allow ``rdm.open`` to open file-like objects (like those returned by s3fs)
  (`#453 <https://github.com/spacetelescope/roman_datamodels/issues/453>`_)
- Provide conversion from TVAC/FPS models to ScienceRawModel (`#455
  <https://github.com/spacetelescope/roman_datamodels/issues/455>`_)


0.23.0 (2025-01-16)
===================

Bug Fixes
---------

- Renamed mosaic association model variable name. (`#412
  <https://github.com/spacetelescope/roman_datamodels/issues/412>`_)


Documentation
-------------

- Updated the documentation to match the present code version. (`#437
  <https://github.com/spacetelescope/roman_datamodels/issues/437>`_)


New Features
------------

- Remove units from reference files. (`#408
  <https://github.com/spacetelescope/roman_datamodels/issues/408>`_)
- Rename source_detection to source_catalog to match romancal step. (`#428
  <https://github.com/spacetelescope/roman_datamodels/issues/428>`_)
- Change default compression to lz4. The previous default was no compression.
  (`#440 <https://github.com/spacetelescope/roman_datamodels/issues/440>`_)
- Add support for opening SSC models using ``rdm_open``. (`#448
  <https://github.com/spacetelescope/roman_datamodels/issues/448>`_)


Misc
----

- Bump min Python version to 3.11 per SPEC 0. (`#432
  <https://github.com/spacetelescope/roman_datamodels/issues/432>`_)


Deprecations and Removals
-------------------------

- Remove validation on assignment. (`#417
  <https://github.com/spacetelescope/roman_datamodels/issues/417>`_)


0.22.0 (2024-11-15)
===================

Bug Fixes
---------

- Only use ``roman.meta`` attributes for crds parameter selection. (`#372
  <https://github.com/spacetelescope/roman_datamodels/issues/372>`_)
- Use a shorter string "?" for maker_utils default values for strings. (`#388
  <https://github.com/spacetelescope/roman_datamodels/issues/388>`_)
- Fix Enum bug in python < 3.11 for the dqflags. (`#425
  <https://github.com/spacetelescope/roman_datamodels/issues/425>`_)


Documentation
-------------

- use ``towncrier`` to handle change log entries (`#384
  <https://github.com/spacetelescope/roman_datamodels/issues/384>`_)


New Features
------------

- Open ``.json`` files as ``ModelLibrary`` if ``romancal`` is installed. (`#389
  <https://github.com/spacetelescope/roman_datamodels/issues/389>`_)
- Added datamodels and tests for ePSF, ABVegaOffset, and ApCorr reference
  files. (`#393
  <https://github.com/spacetelescope/roman_datamodels/issues/393>`_)
- Add ``ref_file`` entry for reference pixel subtraction reference file (`#397
  <https://github.com/spacetelescope/roman_datamodels/issues/397>`_)
- Add python 3.13 support. (`#401
  <https://github.com/spacetelescope/roman_datamodels/issues/401>`_)
- Update datamodels and tests for L1/L2 Roman Doc (`#404
  <https://github.com/spacetelescope/roman_datamodels/issues/404>`_)
- Have datamodels update their ``meta.filename`` attribute match the filename
  of the
  file they were loaded from. This means users can rename files on disk, but
  when they
  open them in datamodels, the filename will be updated to match the new
  filename. (`#409
  <https://github.com/spacetelescope/roman_datamodels/issues/409>`_)


Misc
----

- Use multiclass of ``np.uint32`` and ``Enum`` rather than a subclass of ``IntEnum``
  for
  the dqflags as suggested by the numpy devs. (`#402
  <https://github.com/spacetelescope/roman_datamodels/issues/402>`_)
- Corrected CRDS keywords.
  Updated for Build 17 release of the RAD software package. (`#423
  <https://github.com/spacetelescope/roman_datamodels/issues/423>`_)


Deprecations and Removals
-------------------------

- Remove units from roman_datamodels. (`#405
  <https://github.com/spacetelescope/roman_datamodels/issues/405>`_)
- Remove units from Guidewindow related data models. (`#415
  <https://github.com/spacetelescope/roman_datamodels/issues/415>`_)


0.22.0 (2024-08-06)
===================

- Fix mk_level2_image utility for 3d shape. [#378]

0.21.0 (2024-08-06)
===================

- Recursively convert all meta attributes during model casting. [#352]

- replace usages of ``copy_arrays`` with ``memmap`` [#360]

- Enable asdf "lazy_tree" mode for all roman datamodels files [#358]

- Fix to preserve extra TVAC specific data when processed through DQ Init. [#369]

- Added maker utilities and a test for sky background metadata. [#370]


0.20.0 (2024-05-15)
===================

- Separated TVAC and FPS into their own makers to freeze from from main development. [#347]

- Added statistics blocks to the TVAC and FS models. [#351]

- Fix bug that prevented proper handling of ``np.NDArray``\s. [#350]


0.19.2 (2024-05-08)
===================

- Adds test to ensure that the base ``common`` keyword groups exist within the ``schema.info`` tree. [#338]

- Replaced the previous test for ``schema_info`` with something more robust. [#344]

- Add conversion of dict to string during Qtable construction [#348]

- Do not include QTables in individual image metadata [#349]


0.19.1 (2024-04-04)
===================

- Remove the ``psutil`` dependency. [#320]

- Move ``dqflags`` from ``romancal`` to ``roman_datamodels``. [#293]

- Added documentation for ``stnode``. [#316]

- Add support for ``FPS`` and ``TVAC`` models. [#309]

- Make datamodels follow the same subscription pattern as the ``stnode`` based
  objects. [#322]

- Changed image units from e/s to DN/s (and added support for MJy/sr). [#327]

- Add attributes under the ``basic`` schema to ``WfiMosaic.meta``. [#328]

- Split cal_step into L2 and L3 versions. [#334]

- Add Members Keyword to Resample datamodel maker utility. [#333]

- Add initialization for the flux step meta. [#332]

- Create ``outlier_detection`` schema and add bit mask field to both it and ``resample``. [#336]

- Add models for Level 2 and Level 3 source catalog and segmentation map. [#331]


0.19.0 (2024-02-09)
===================

- Allow assignment to or creation of node attributes using dot notation of object instances
  with validation. [#284]

- Bugfix for ``model.meta.filename`` not matching the filename of the file on disk. [#295]

- Bugfix for ``meta.model_type`` not being set to match the model writing the file. [#296]

- Add ``meta.wcs`` to ``maker_utils``. [#302]

- Remove duplicate validation during ``DataModel.to_asdf``, replace assumed validation
  during ``AsdfFile.__init__`` with call to ``AsdfFile.validate``  [#301]

0.18.0 (2023-11-06)
===================

- Allow DNode and LNode subclass instances to be assigned to tree attributes and support
  validation of all such instances. [#275]

- Update minimum version of astropy to 5.3.0 in order to fix a bug due to a breaking
  change in astropy. [#258]

- Update minimum version of numpy to 1.22 as this is the oldest version of numpy
  which is currently supported. [#258]

- Fix the initialization of empty DataModels and clean up the datamodel core. [#251]

- Add slope and error to dark RefModel and tests. [#280]

- Added truncation to exposure. [#283]

- Added optional dq array to science raw maker utility and test. [#282]

- Updated the WFI_Mosaic datamodel, maker utilities, and tests to a more streamlined metadata design for level 3 products. [#288]


0.17.1 (2023-08-03)
===================

- Fix newly required units from rand [#256]

0.17.0 (2023-07-28)
===================

- Add checks for for association processing [#241]

- Make a shallow copy when opening an existing datamodel, rather than
  a full copy.  [#232]

- Remove the ``random_utils`` module and make ``maker_utils`` entirely deterministic. [#217]

- Add tests to ensure consistency between file-level schemas in RAD and the corresponding
  datamodels in ``roman_datamodels``. [#214]

- Make ``maker_utils`` return the node when writing the node to a file. [#218]

- Clean up overlooked randomness in ``maker_utils`` and tests. [#236]

- Remove the unused ``target`` keyword from ``rdm_open`` and fix the original issue that the
  keyword was meant to address; namely, passing a datamodel instance to the constructor for
  that datamodel instance should return the instance back with no modifications. [#235]

- Use ValidationError from asdf.exceptions instead of jsonschema. Increase minimum
  asdf version to 2.15.0. [#234]

- Update ``maker_utils`` to support the new ``cal_step`` keys. [#228, #243]

- Clean up the ``rdm_open`` function. [#233]

- Include tests in coverage and turn testing warnings into errors. [#238]

- Add ``__repr__`` to ``DNode``. [#245]

- Further adjustments to support CRDS for the ``inverselinearity`` reference file. [#248]

0.16.1 (2023-06-27)
===================

A minor release to set the minimum version of RAD to 0.16.0.

0.16.0 (2023-06-23)
===================

- Remove ``ModelContainer`` from ``roman_datamodels.datamodels``. [#204]

- Update the ``reftype`` for ``InverseLinearityRev``. [#195]

- Bugfix for initializing ``Datamodel`` objects from the incorrect ``stnode`` classes. [#200]

- Refactor the ``maker_utils`` to be easier to maintain and test. [#193]

- Remove the ``STUserDict`` class and fix bugs in ``stnode`` related to ``copy``. [#191]

- Add constructor for ``RampModel`` from the ``ScienceRawModel``. [#202]

- Add ``maker_utils`` for all the datamodels. [#198]

- Update ``roman_datamodels`` to support the new reference file for the
  reference pixel correction. [#190]

- Update ``DataModel.schema_uri`` to use non-deprecated
  ``TagDefinition.schema_uris`` from asdf [#209]

- Remove the ``util`` and ``mktest`` modules. [#212]

- Refactor the ``maker_utils`` API so that it is uniform across all tests. [#207]

- Remove the ``testing.factories`` module. [#197]

- Refactor ``datamodels`` to be easier to maintain and test by turning it into
  a sub-package and splitting the module apart. [#201]

- Remove the ``filetype`` module. [#219]

- Update ``roman_datamodels`` to support the new ``msos_stack-1.0.0`` schema. [#206]

- Refactor ``stnode`` to be easier to maintain and test by turning it into a
  sub-package and splitting the module apart. [#213]

- Remove the unused project deployment scripts and actions. [#222]

- Refactor the ASDF extension to be entirely part of the stnode sub-package. [#220]

0.15.0 (2023-05-15)
===================

- Updates the maker utilities for guide windows to include gw_science_file_source  [#179]

- Remove use of deprecated ``pytest-openfiles`` ``pytest`` plugin. This has been replaced by
  catching ``ResourceWarning`` s. [#142]

- Add support for read pattern in data model makers and factories. [#154]

- Remove ``source_type_apt`` from ``target-1.0.0`` related datamodels. [#152]

- Enable seeding for ``random_utils`` functions. [#148]

- Add Changelog checking CI. [#161]

- Add Pull Request Template. [#147]

- Add Level 3 MosaicModel and Resample stnodes, maker utils, factories, and tests. [#163]

- Renamed n_ints to n_groups. Did some shape variable cleanup. [#165]

- Bugfix for the ``amp33`` shape in ``mk_ramp``. [#166]

- Remove the deprecated ``roman_datamodels.units`` module. [#172]

- Bugfix for ``photmjsr`` not being able to be set or validated properly. [#170]

- Add ability to turn off data validation via an environment variable. [#173]
- Add support for model containers constructed from ``Iterable`` [#164]

- drop support for Python 3.8 [#155]


0.14.2 (2023-03-31)
===================

- Added support for Inverse Nonlinearity data model, maker utilities, and tests. [#125]

- Moved datamodel maker utilities and split random functions out to utility file. [#128]

- Begin process of removing ``roman_datamodels.units`` for non-VOUnit support in favor
  of non-VOUnit support coming directly via ``asdf-astropy``. [#131]

- Suppress erfa warnings for randomly generated future times [#138]

- update minimum version of ``numpy`` to ``1.20`` and add minimum dependency testing to CI [#114]

- Use available tag schema if available during datamodels.validate [#140]

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

- pin ``asdf`` above ``2.12.1`` to fix issue with ``jsonschema`` release [#91]
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
