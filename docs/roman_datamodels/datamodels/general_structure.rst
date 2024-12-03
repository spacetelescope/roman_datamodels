General Structure of a Roman datamodel
======================================

Overview
........

When opening a Roman ASDF data file as such::

  import roman_datamodels as rdm
  dm = rdm.open('some_roman_data.asdf')

What is returned is a Python object that on the surface is very similar to its
JWST equivalent, and provides all the relevant methods that make sense for Roman
(for example, those that relate to FITS issues in JWST are not needed for Roman).

It should be mentioned that all Reference files are also in ASDF format; each
reference file type has its own datamodel, whose structure has a standard set
of attributes between all reference files (fairly small), and quite a bit of
variation in the rest of the attributes.

Some of the most relevant methods are:

- **clone:** an in-memory copy
- **save:** save in a new file
- **close:** close the file
- **get_primary_array_name:** the attribute name of the primary array
- **shape**: shape of primary array
- **to_flat_dict:** return all items as a flat dictionary with keys as dotted
  attribute paths such as ``meta.exposure.start_time``
- **items:** return all items as a list of key, value pairs, with keys expressed as
  dotted attribute paths
- **get_crds_parameters:** obtain all parameters used to select reference files
  in CRDS
- **validate:** check datamodel against schemas
- **info:** display information about the contents
- **search:** search for attributes or values

While ASDF permits a wide variety of legal attribute names, the convention is that Roman
only uses attribute name that are legal Python variable names. This is so they can be
used as Python object attributes. Using the above example for the keys that ``to_flat_dict``
returns, that permits using ``dm.meta.exposure.start_time`` to obtain the value of that attribute
instead of ``dm.tree['roman']['meta']['exposure']['start_time']``. The latter can still be used
if you enjoy typing lots of brackets and quotes instead of periods.

Generally, the large data related items, such as the image array and associated data quality,
error, and other arrays are at the top of the contents of the roman attribute. The related
metadata is to be found under the meta attribute.

We will show two examples, one of a reference file, and one of a image data set,
starting with the reference file first since it generally is much simpler

Reference File Example
......................

The following displays the output of the info method on a Dark reference file::

  root (AsdfObject)
  ├─asdf_library (Software)
  │ ├─author (str): The ASDF Developers
  │ ├─homepage (str): http://github.com/asdf-format/asdf
  │ ├─name (str): asdf
  │ └─version (str): 3.4.0
  ├─history (dict)
  │ └─extensions (list)
  │   ├─[0] (ExtensionMetadata)
  │   │ ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │   │ ├─extension_uri (str): asdf://asdf-format.org/core/extensions/core-1.5.0
  │   │ ├─manifest_software (Software)
  │   │ │ ├─name (str): asdf_standard
  │   │ │ └─version (str): 1.1.1
  │   │ └─software (Software)
  │   │   ├─name (str): asdf-astropy
  │   │   └─version (str): 0.6.1
  │   ├─[1] (ExtensionMetadata)
  │   │ ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │   │ ├─extension_uri (str): asdf://astropy.org/astropy/extensions/units-1.0.0
  │   │ └─software (Software)
  │   │   ├─name (str): asdf-astropy
  │   │   └─version (str): 0.6.1
  │   └─[2] (ExtensionMetadata)
  │     ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │     ├─extension_uri (str): asdf://stsci.edu/datamodels/roman/extensions/datamodels-1.0
  │     ├─manifest_software (Software)
  │     │ ├─name (str): rad
  │     │ └─version (str): 0.22.1.dev4+gdf2aa07.d20241122
  │     └─software (Software)
  │       ├─name (str): roman_datamodels
  │       └─version (str): 0.22.1.dev9+g6580f18.d20241120
  └─roman (DarkRef) # Dark Reference File Schema
    ├─meta (dict)
    │ ├─author (str): test system
    │ ├─description (str): blah blah blah
    │ ├─exposure (dict)
    │ │ ├─groupgap (int): 0
    │ │ ├─ma_table_name (str): ?
    │ │ ├─ma_table_number (int): -999999
    │ │ ├─nframes (int): 8
    │ │ ├─ngroups (int): 6
    │ │ ├─p_exptype (str): WFI_IMAGE|WFI_GRISM|WFI_PRISM|
    │ │ └─type (str): WFI_IMAGE
    │ ├─instrument (dict)
    │ │ ├─detector (str): WFI01
    │ │ ├─name (str): WFI
    │ │ └─optical_element (str): F158
    │ ├─origin (Origin): STSCI # Institution / Organization Name
    │ ├─pedigree (str): GROUND
    │ ├─reftype (str): DARK
    │ ├─telescope (Telescope): ROMAN # Telescope Name
    │ └─useafter (Time): 2020-01-01T00:00:00.000
    ├─data (Quantity): shape=(2, 4096, 4096), dtype=float32 # Dark Current Array
    ├─dq (NDArrayType): shape=(4096, 4096), dtype=uint32 # 2-D Data Quality Array
    ├─dark_slope (Quantity): shape=(4096, 4096), dtype=float32 # Dark Current Rate Array
    └─dark_slope_error (Quantity): shape=(4096, 4096), dtype=float32 # Dark Current Rate Uncertainty Array


Everything appearing before the ``roman`` attribute is general metadata about
versions of various aspects of the ASDF file and the extensions it is using.
For Roman, the general convention is that all metadata appears under the meta
attribute, and that science and associated arrays appear directly under the
``roman`` attribute. You should note that the metadata has attributes that
consist of groups of other attributes (e.g., ``exposure`` and ``instrument``).

Most users of the datamodel objects do not need to deal with the schemas,
unless they are involved in creating new types of files, or are dealing
with validation errors that aren't obvious from the validation error
messages. But we will spend some space with some schema examples. Those
doing an initial read of this documentation should feel free to skip
the schema examples.

The corresponding schema for the dark model above is::

    %YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/dark-1.0.0

    title: Dark Reference File Schema

    datamodel_name: DarkRefModel

    type: object
    properties:
      meta:
        allOf:
          - $ref: ref_common-1.0.0
          - type: object
            properties:
              reftype:
                type: string
                enum: [DARK]
              exposure:
                type: object
                properties:
                  ngroups:
                    title: Number of Resultants
                    description: |
                      The number of resultants averaged according to
                      Multi-Accumulation (MA) Table read pattern.
                    type: integer
                  nframes:
                    title: Number of frames per resultant # should be removed
                    type: integer
                  groupgap:
                    title: Number of Skips Between Resultants
                    description: |
                      The number of frames skipped between resultants according to
                      MA Table read pattern.
                    type: integer
                  ma_table_name:
                    title: Multi-Accumulation Table Name
                    description: |
                      The name of the MA Table used. Not a unique identifier; see
                      ma_table_number.
                    type: string
                  ma_table_number:
                    title: Multi-Accumulation Table Number
                    description: |
                      The unique number of the MA Table used. A modification to a MA
                      Table that keeps the same name will have a new
                      ma_table_number.
                    type: integer
                required: [ngroups, nframes, groupgap, ma_table_name, ma_table_number]
            required: [exposure]
          - $ref: ref_exposure_type-1.0.0
          - $ref: ref_optical_element-1.0.0
      data:
        title: Dark Current Array
        description: |
          The dark current array represents the integrated number of counts due to
          the accumulation of dark current electrons in the pixels.
        tag: tag:stsci.edu:asdf/unit/quantity-1.*
        properties:
          value:
            tag: tag:stsci.edu:asdf/core/ndarray-1.*
            datatype: float32
            exact_datatype: true
            ndim: 3
          unit:
            tag: tag:astropy.org:astropy/units/unit-1.*
            enum: ["DN"]
      dq:
        title: 2-D Data Quality Array
        description: |
          The 2-D data quality array for the Dark Current Array.
        tag: tag:stsci.edu:asdf/core/ndarray-1.*
        datatype: uint32
        exact_datatype: true
        ndim: 2
      dark_slope:
        title: Dark Current Rate Array
        description: |
          The dark current rate array represents the slope of the integrated number
          of counts due to the accumulation of dark current electrons in the pixels
          calculated from slope fitting the Dark Current Array.
        tag: tag:stsci.edu:asdf/unit/quantity-1.*
        properties:
          value:
            tag: tag:stsci.edu:asdf/core/ndarray-1.*
            datatype: float32
            exact_datatype: true
            ndim: 2
          unit:
            tag: tag:astropy.org:astropy/units/unit-1.*
            enum: ["DN / s"]
      dark_slope_error:
        title: Dark Current Rate Uncertainty Array
        description: |
          The uncertainty calculated from the slope fitting of the Dark Current
          Array.
        tag: tag:stsci.edu:asdf/unit/quantity-1.*
        properties:
          value:
            tag: tag:stsci.edu:asdf/core/ndarray-1.*
            datatype: float32
            exact_datatype: true
            ndim: 2
          unit:
            tag: tag:astropy.org:astropy/units/unit-1.*
            enum: ["DN / s"]
    required: [meta, data, dq, dark_slope, dark_slope_error]
    flowStyle: block
    propertyOrder: [meta, data, dq, dark_slope, dark_slope_error]
    ...


This won't go in to a great deal of detail about schemas but a few things will be
noted. The end of the schema lists the required attributes, and also specifies
the order they should appear in the output. The data array attributes specifies the
dimensionality of the arrays and their numeric type. The details of the ``meta``
are mostly specified in other schemas (done this way since these are shared
amongst many schemas), with exception of the ``reftype`` and ``exposure``
attributes. For those one can see their type and sometimes their permissible
values are listed. The other schemas referenced are: ref_common-1.0.0,
ref_exposure_type-1.0.0, and ref_optical_element-1.0.0. These are displayed below.

ref_common-1.0.0::

    %YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_common-1.0.0

    title: Common Reference File Metadata Properties

    type: object
    properties:
      reftype:
        title: Reference File Type
        description: |
          The capitalized string of the reference file type (e.g., DARK).
        type: string
      pedigree:
        title: Pedigree
        description: |
          The pedigree of the reference file (e.g., GROUND).
        type: string
        enum: [GROUND, MODEL, DUMMY, SIMULATION]
      description:
        title: Description
        description: |
          A string describing the reference file, its intended usage, etc.
        type: string
      author:
        title: Author
        description: |
          The author of who or what created the reference file.
        type: string
      useafter:
        title: Use After Date
        description: |
          The use after date of the reference file for CRDS best references
          matching.
        tag: tag:stsci.edu:asdf/time/time-1.*
      telescope:
        title: Telescope
        description: |
          The telescope data used to select reference files, e.g. ROMAN for the
          Nancy Grace Roman Space Telescope.
        anyOf:
          - tag: asdf://stsci.edu/datamodels/roman/tags/telescope-1.0.0
          - type: string
            enum: [ROMAN]
      origin:
        title: Organization
        description: |
          The organization responsible for creating the file, e.g. STSCI for the
          Space Telescope Science Institute.
        type: string
      instrument:
        type: object
        properties:
          name:
            title: Instrument
            description: |
              The Wide Field Instrument (WFI).
            type: string
            enum: [WFI]
          detector:
            title: Detector
            description: |
              The numbered WFI detector in the focal plane (e.g., WFI01 for SCA 01).
            $ref: ../wfi_detector-1.0.0
        required: [name, detector]
    required: [reftype, author, description, pedigree, useafter, telescope, origin, instrument]
    ...


ref_exposure_type-1.0.0::


    %YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type-1.0.0

    title: Exposure Type Reference Schema

    type: object
    properties:
      exposure:
        type: object
        properties:
          type:
            title: WFI Mode
            description: |
              The type of data taken with the WFI. Allowed values are WFI_IMAGE for
              imaging mode, WFI_GRISM and WFI_PRISM for spectral mode, WFI_DARK for
              dark exposures, WFI_FLAT for flat fields, and WFI_WFSC.
            $ref: ../exposure_type-1.0.0
          p_exptype:
            title: WFI Mode for CRDS
            description: |
              The potentially multiple mode strings applied to data for reference
              file matching in CRDS. Modes are separated by "|".
            type: string
            pattern: "^((WFI_IMAGE|WFI_GRISM|WFI_PRISM|WFI_DARK|WFI_FLAT|WFI_WFSC)\\s*\\|\\s*)+$"
        required: [type,p_exptype]
    required: [exposure]
    ...


ref_optical_element-1.0.0::


  %YAML 1.1
  ---
  $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
  id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_optical_element-1.0.0

  title: Optical Element Reference Schema

  type: object
  properties:
    instrument:
      type: object
      properties:
        optical_element:
          title: Optical Element
          description: |
            The optical element filter name.
          $ref: ../wfi_optical_element-1.0.0
      required: [optical_element]
  required: [instrument]
  ...

If one tries to modify the datamodel contents with a value inconsistent with
what a schema requires, validation will raise an error when the datamodel is
validated.

Level 1 Example
...............

The following displays the output of the info method on Level 1 data file and will be
used as a basis of discussion of the structure of the data model. Essentially, the contents
of meta will consist of the same attributes with few variations between data files::


  root (AsdfObject)
  ├─asdf_library (Software)
  │ ├─author (str): The ASDF Developers
  │ ├─homepage (str): http://github.com/asdf-format/asdf
  │ ├─name (str): asdf
  │ └─version (str): 3.4.0
  ├─history (dict)
  │ └─extensions (list)
  │   ├─[0] (ExtensionMetadata)
  │   │ ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │   │ ├─extension_uri (str): asdf://asdf-format.org/core/extensions/core-1.5.0
  │   │ ├─manifest_software (Software)
  │   │ │ ├─name (str): asdf_standard
  │   │ │ └─version (str): 1.1.1
  │   │ └─software (Software)
  │   │   ├─name (str): asdf-astropy
  │   │   └─version (str): 0.6.1
  │   └─[1] (ExtensionMetadata)
  │     ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │     ├─extension_uri (str): asdf://stsci.edu/datamodels/roman/extensions/datamodels-1.0
  │     ├─manifest_software (Software)
  │     │ ├─name (str): rad
  │     │ └─version (str): 0.22.1.dev4+gdf2aa07.d20241122
  │     └─software (Software)
  │       ├─name (str): roman_datamodels
  │       └─version (str): 0.22.1.dev9+g6580f18.d20241120
  └─roman (WfiScienceRaw) # Level 1 (L1) Uncalibrated Roman Wide Field
  Instrument (WFI) Ramp Cube

    ├─meta (dict)
    │ ├─calibration_software_name (CalibrationSoftwareName): RomanCAL # Calibration Software Name
    │ ├─calibration_software_version (CalibrationSoftwareVersion): 9.9.0 # Calibration Software Version Number
    │ ├─coordinates (Coordinates) # Name Of The Coordinate Reference Frame
    │ │ └─reference_frame (str): ICRS # Name of the Celestial Coordinate Reference Frame
    │ ├─ephemeris (Ephemeris) # Ephemeris Data Information
    │ │ ├─earth_angle (int): -999999 # Earth Angle (radians)
    │ │ ├─moon_angle (int): -999999 # Moon Angle (radians)
    │ │ ├─sun_angle (int): -999999 # Sun Angle (radians)
    │ │ ├─type (str): DEFINITIVE # Ephemeris Type
    │ │ ├─time (int): -999999 # UTC Time of Ephemeris Information (MJD)
    │ │ ├─ephemeris_reference_frame (str): ? # Ephemeris Reference Frame
    │ │ ├─spatial_x (int): -999999 # X Spatial Coordinate of Roman (km)
    │ │ ├─spatial_y (int): -999999 # Y Spatial Coordinate of Roman (km)
    │ │ ├─spatial_z (int): -999999 # Z Spatial Coordinate of Roman (km)
    │ │ ├─velocity_x (int): -999999 # X Component of Roman Velocity (km/s)
    │ │ ├─velocity_y (int): -999999 # Y Component of Roman Velocity (km/s)
    │ │ └─velocity_z (int): -999999 # Z Component of Roman Velocity (km/s)
    │ ├─exposure (Exposure) # Exposure Information

    │ │ ├─type (str): WFI_IMAGE
    │ │ ├─start_time (Time): 2020-01-01T00:00:00.000 # Exposure Start Time (UTC)
    │ │ ├─mid_time (Time): 2020-01-01T01:00:00.000 # Exposure Mid Time (UTC)
    │ │ ├─end_time (Time): 2020-01-01T02:00:00.000 # Exposure End Time (UTC)
    │ │ ├─nresultants (int): 6 # Number of Resultants
    │ │ ├─data_problem (bool): False # Data Problem
    │ │ ├─frame_time (int): -999999 # Detector Readout Time (s)
    │ │ ├─exposure_time (int): -999999 # Exposure Time (s)
    │ │ ├─effective_exposure_time (int): -999999 # Effective Exposure Time (s)
    │ │ ├─ma_table_name (str): ? # Name of the Multi-Accumulation Table
    │ │ ├─ma_table_number (int): -999999 # Multi-Accumulation Table Identification Number
    │ │ ├─read_pattern (list) # Read Pattern
    │ │ │ ├─[0] (list)
    │ │ │ │ └─[0] (int): 1
    │ │ │ ├─[1] (list)
    │ │ │ │ ├─[0] (int): 2
    │ │ │ │ └─[1] (int): 3
    │ │ │ ├─[2] (list)
    │ │ │ │ └─[0] (int): 4
    │ │ │ ├─[3] (list)
    │ │ │ │ ├─[0] (int): 5
    │ │ │ │ ├─[1] (int): 6
    │ │ │ │ ├─[2] (int): 7
    │ │ │ │ └─[3] (int): 8
    │ │ │ ├─[4] (list)
    │ │ │ │ ├─[0] (int): 9
    │ │ │ │ └─[1] (int): 10
    │ │ │ └─[5] (list)
    │ │ │   └─[0] (int): 11
    │ │ └─truncated (bool): False # Truncated MA Table
    │ ├─file_date (FileDate): 2020-01-01T00:00:00.000 # File Creation Date
    │ ├─filename (Filename): l1_doc.asdf # File Name
    │ ├─guide_star (Guidestar) # Guide Star and Guide Window Information
    │ │ ├─guide_window_id (str): ? # Guide Window Identifier
    │ │ ├─guide_mode (str): WSM-ACQ-2
    │ │ ├─data_start (Time): 2020-01-01T00:00:00.000 # Guide Data Start Time (UTC)
    │ │ ├─data_end (Time): 2020-01-01T01:00:00.000 # Guide Data End Time (UTC)
    │ │ ├─window_xstart (int): -999999 # Guide Window X Start Position (pixels)
    │ │ ├─window_ystart (int): -999999 # Guide Window Y Start Position (pixels)
    │ │ ├─window_xstop (int): -999829 # Guide Window X Stop Position (pixels)
    │ │ ├─window_ystop (int): -999975 # Guide Window Y Start Position (pixels)
    │ │ ├─window_xsize (int): 170 # Guide Window Size in the X Direction (pixels)
    │ │ ├─window_ysize (int): 24 # Guide Window Size in the Y Direction (pixels)
    │ │ ├─guide_star_id (str): ? # Guide Star Identifier
    │ │ ├─gsc_version (str): ? # Guide Star Catalog Version
    │ │ ├─ra (int): -999999 # Guide Star Right Ascension (deg)
    │ │ ├─dec (int): -999999 # Guide Star Declination (deg)
    │ │ ├─ra_uncertainty (int): -999999 # Guide Star Right Ascension Uncertainty (deg)
    │ │ ├─dec_uncertainty (int): -999999 # Guide Star Declination Uncertainty (deg)
    │ │ ├─fgs_magnitude (int): -999999 # Guide Star Instrumental Magnitude
    │ │ ├─fgs_magnitude_uncertainty (int): -999999 # Guide Star Instrumental Magnitude Uncertainty
    │ │ ├─centroid_x (int): -999999 # Guide Star Centroid X Position (pixels)
    │ │ ├─centroid_y (int): -999999 # Guide Star Centroid Y Position (pixels)
    │ │ ├─centroid_x_uncertainty (int): -999999 # Guide Star Centroid X Position Uncertainty (pixels)
    │ │ ├─centroid_y_uncertainty (int): -999999 # Guide Star Centroid Y Position Uncertainty (pixels)
    │ │ ├─epoch (str): ? # Guide Star Coordinates Epoch
    │ │ ├─proper_motion_ra (int): -999999 # Proper Motion of the Guide Star Right Ascension (mas / yr)
    │ │ ├─proper_motion_dec (int): -999999 # Proper Motion of the Guide Star Declination (mas / yr)
    │ │ ├─parallax (int): -999999 # Guide Star Parallax (mas)
    │ │ └─centroid_rms (int): -999999 # Guide Star Centroid RMS
    │ ├─instrument (WfiMode) # Wide Field Instrument (WFI) Configuration Information
    │ │ ├─detector (str): WFI01 # Wide Field Instrument (WFI) Detector Identifier
    │ │ ├─optical_element (str): F158 # Wide Field Instrument (WFI) Optical Element
    │ │ └─name (str): WFI # Instrument Name
    │ ├─model_type (ModelType): ScienceRawModel # Data Model Type
    │ ├─observation (Observation) # Observation Identifiers
    │ │ ├─observation_id (str): ? # Programmatic Observation Identifier
    │ │ ├─visit_id (str): ? # Visit Identifier
    │ │ ├─program (int): 1 # Program Number
    │ │ ├─execution_plan (int): 1 # Execution Plan Number
    │ │ ├─pass (int): 1 # Pass Number
    │ │ ├─segment (int): 1 # Segment Number
    │ │ ├─observation (int): 1 # Observation Number
    │ │ ├─visit (int): 1 # Visit Number
    │ │ ├─visit_file_group (int): 1 # Visit File Group
    │ │ ├─visit_file_sequence (int): 1 # Visit File Sequence
    │ │ ├─visit_file_activity (str): 01 # Visit File Activity
    │ │ └─exposure (int): 1 # Exposure Number
    │ ├─origin (Origin): STSCI/SOC # Institution / Organization Name
    │ ├─pointing (Pointing) # Spacecraft Pointing Information
    │ │ ├─ra_v1 (int): -999999 # Right Ascension of the Telescope V1 Axis (deg)
    │ │ ├─dec_v1 (int): -999999 # Declination of the Telescope V1 Axis (deg)
    │ │ ├─pa_v3 (int): -999999 # Position Angle of the Telescope V3 Axis (deg)
    │ │ ├─target_aperture (str): ? # Aperture Name Used for Pointing
    │ │ ├─target_ra (int): -999999 # Right Ascension of the Target Aperture (deg)
    │ │ └─target_dec (int): -999999 # Declination of the Target Aperture
    │ ├─prd_version (PrdVersion): 8.8.8 # SOC PRD Version Number
    │ ├─product_type (ProductType): l2 # Product Type Descriptor
    │ ├─program (Program) # Program Information
    │ │ ├─title (str): ? # Proposal Title
    │ │ ├─investigator_name (str): ? # Principal Investigator Name
    │ │ ├─category (str): ? # Program Category
    │ │ ├─subcategory (str): None # Program Subcategory
    │ │ ├─science_category (str): ? # Science Category
    │ │ └─continuation_id (int): -999999 # Program Continuation Identifier
    │ ├─rcs (Rcs) # Relative Calibration System Information
    │ │ ├─active (bool): False # Status of the Relative Calibration System (RCS)
    │ │ ├─electronics (str): A # Relative Calibration System (RCS) Electronics Side
    │ │ ├─bank (str): 1 # Light Emitting Diode (LED) Bank Selection
    │ │ ├─led (str): 1 # Light Emitting Diode (LED) Passband
    │ │ └─counts (int): -999999 # Light Emitting Diode (LED) Flux (DN)
    │ ├─ref_file (RefFile) # Reference File Information
    │ │ ├─area (str): N/A # Pixel Area Reference File Information
    │ │ ├─crds (dict) # Calibration Reference Data System (CRDS) Information
    │ │ │ ├─context (str): roman_0815.pmap # CRDS Context
    │ │ │ └─version (str): 12.3.1 # CRDS Software Version
    │ │ ├─dark (str): N/A # Dark Reference File Information
    │ │ ├─distortion (str): N/A # Distortion Reference File Information
    │ │ ├─flat (str): N/A # Flat Reference File Information
    │ │ ├─gain (str): N/A # Gain Reference Rile Information
    │ │ ├─inverse_linearity (str): N/A # Inverse Linearity Reference File Information
    │ │ ├─linearity (str): N/A # Linearity Reference File Information
    │ │ ├─mask (str): N/A # Bad Pixel Mask Reference File Information
    │ │ ├─photom (str): N/A # Photometry Reference File Information
    │ │ ├─readnoise (str): N/A # Read Noise Reference File Information
    │ │ ├─refpix (str): N/A # Reference Pixel Reference File Information
    │ │ └─saturation (str): N/A # Saturation Reference File Information
    │ ├─sdf_software_version (SdfSoftwareVersion): 7.7.7 # SDF Version Number
    │ ├─telescope (Telescope): ROMAN # Telescope Name
    │ ├─velocity_aberration (VelocityAberration) # Velocity Aberration Correction Information
    │ │ ├─ra_reference (int): -999999 # Velocity Aberrated Reference Right Ascension (deg)
    │ │ ├─dec_reference (int): -999999 # Velocity Aberrated Reference Declination (deg)
    │ │ └─scale_factor (int): -999999 # Velocity Aberration Correction Scale Factor
    │ ├─visit (Visit) # Visit Information
    │ │ ├─dither (dict) # Dither Pattern Information
    │ │ │ ├─executed_pattern (list) # Executed Dither Pattern Offsets (arcsec)
    │ │ │ │ ├─[0] (int): 1
    │ │ │ │ ├─[1] (int): 2
    │ │ │ │ ├─[2] (int): 3
    │ │ │ │ ├─[3] (int): 4
    │ │ │ │ ├─[4] (int): 5
    │ │ │ │ ├─[5] (int): 6
    │ │ │ │ ├─[6] (int): 7
    │ │ │ │ ├─[7] (int): 8
    │ │ │ │ └─[8] (int): 9
    │ │ │ ├─primary_name (NoneType): None # Primary Dither Pattern Name
    │ │ │ └─subpixel_name (NoneType): None # Subpixel Dither Pattern Name
    │ │ ├─engineering_quality (str): OK # Engineering Data Quality
    │ │ ├─pointing_engineering_source (str): CALCULATED # Pointing Engineering Source
    │ │ ├─type (str): PRIME_TARGETED_FIXED # Visit Type
    │ │ ├─start_time (Time): 2020-01-01T00:00:00.000 # Visit Start Time (UTC)
    │ │ ├─end_time (Time): 2020-01-01T00:00:00.000 # Visit End Time (UTC)
    │ │ ├─status (str): UNSUCCESSFUL # Visit Status
    │ │ ├─nexposures (int): -999999 # Number of Planned Exposures
    │ │ └─internal_target (bool): False # Internal Target
    │ └─wcsinfo (Wcsinfo) # World Coordinate System (WCS) Information
    │   ├─aperture_name (str): WFI01_FULL # Aperture Name
    │   ├─pa_aperture (int): -999999 # Aperture Position Angle (deg)
    │   ├─v2_ref (int): -999999 # V2 Reference Position (arcsec)
    │   ├─v3_ref (int): -999999 # V3 Reference Position (arcsec)
    │   ├─vparity (int): -1 # Relative Rotation Between the Ideal and Telescope Axes
    │   ├─v3yangle (int): -999999 # Angle Between the V3 and Ideal Y Axes (deg)
    │   ├─ra_ref (int): -999999 # Right Ascension of the Reference Position (deg)
    │   ├─dec_ref (int): -999999 # Declination of the Reference Position (deg)
    │   ├─roll_ref (int): -999999 # V3 Position Angle at the Reference Position
    │   └─s_region (str): ? # Spatial Extent of the Exposure
    ├─data (NDArrayType): shape=(8, 4096, 4096), dtype=uint16 # Science Data (DN)
    └─amp33 (NDArrayType): shape=(8, 4096, 128), dtype=uint16 # Amplifier 33 Reference Pixel Data (DN)



The corresponding schemas for this dataset are:

wfi_science_raw-1.0.0.yaml::


  %YAML 1.1
  ---
  $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
  id: asdf://stsci.edu/datamodels/roman/schemas/wfi_science_raw-1.0.0

  title: |
    Level 1 (L1) Uncalibrated Roman Wide Field
    Instrument (WFI) Ramp Cube

  datamodel_name: ScienceRawModel

  archive_meta: None

  type: object
  properties:
    meta:
      $ref: common-1.0.0
    data:
      title: Science Data (DN)
      description: |
        Uncalibrated science ramp cube in units of data
        numbers (DNs)
      tag: tag:stsci.edu:asdf/core/ndarray-1.*
      ndim: 3
      datatype: uint16
      unit: "DN"
      exact_datatype: true
    amp33:
      title: Amplifier 33 Reference Pixel Data (DN)
      description: |
        Reference pixel data from amplifier 33 in units of
        data numbers (DNs)
      tag: tag:stsci.edu:asdf/core/ndarray-1.*
      ndim: 3
      datatype: uint16
      unit: "DN"
      exact_datatype: true
    resultantdq:
      title: Resultant Data Quality Array
      description: |
        Optional, 3-D data quality array with a plane for each
        resultant.
      tag: tag:stsci.edu:asdf/core/ndarray-1.*
      ndim: 3
      datatype: uint8
      exact_datatype: true
  propertyOrder: [meta, data, amp33, resultantdq]
  flowStyle: block
  required: [meta, data, amp33]
  ...



common-1.0.0.yaml::


  %YAML 1.1
  ---
  $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
  id: asdf://stsci.edu/datamodels/roman/schemas/common-1.0.0

  title: Common metadata properties

  allOf:
  # Meta Variables
  - $ref: asdf://stsci.edu/datamodels/roman/schemas/basic-1.0.0
  - type: object
    properties:
      # Meta Objects
      coordinates:
        title: Name Of The Coordinate Reference Frame
        tag: asdf://stsci.edu/datamodels/roman/tags/coordinates-1.0.0
      ephemeris:
        title: Ephemeris Data Information
        tag: asdf://stsci.edu/datamodels/roman/tags/ephemeris-1.0.0
      exposure:
        title: Exposure Information
        tag: asdf://stsci.edu/datamodels/roman/tags/exposure-1.0.0
      guide_star:
        title: Guide Star Window Information
        tag: asdf://stsci.edu/datamodels/roman/tags/guidestar-1.0.0
      instrument:
        title: WFI Observing Configuration
        tag: asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.0.0
      observation:
        title: Observation Identifiers
        tag: asdf://stsci.edu/datamodels/roman/tags/observation-1.0.0
      pointing:
        title: Spacecraft Pointing Information
        tag: asdf://stsci.edu/datamodels/roman/tags/pointing-1.0.0
      program:
        title: Program Information
        tag: asdf://stsci.edu/datamodels/roman/tags/program-1.0.0
      ref_file:
        title: Reference File Information
        tag: asdf://stsci.edu/datamodels/roman/tags/ref_file-1.0.0
      rcs:
        title: Relative Calibration System Information
        tag: asdf://stsci.edu/datamodels/roman/tags/rcs-1.0.0
      velocity_aberration:
        title: Velocity Aberration Correction Information
        tag: asdf://stsci.edu/datamodels/roman/tags/velocity_aberration-1.0.0
      visit:
        title: Visit Information
        tag: asdf://stsci.edu/datamodels/roman/tags/visit-1.0.0
      wcsinfo:
        title: World Coordinate System (WCS) Parameters
        tag: asdf://stsci.edu/datamodels/roman/tags/wcsinfo-1.0.0
    required: [coordinates, ephemeris, exposure, guide_star,
               instrument, observation, pointing, program, ref_file,
               rcs, velocity_aberration, visit, wcsinfo]
  ...



The rest of the included schemas are not shown to save space.

Level 2 Example
...............

The calibrated data has very much the same structure in the meta content.
The following example of Level 2 dataset is displayed to show that it now
contains logging messages, and noticeably different data content. Most
of the content has been removed to keep it reasonably short, as well as
not showing the associated schemas::


  root (AsdfObject)
  ├─asdf_library (Software)
  <<<<<<general asdf header elided>>>>>>
  └─roman (WfiImage) # Level 2 (L2) Calibrated Roman Wide Field Instrument (WFI) Rate Image.
    ├─meta (dict)
    │ ├─background (SkyBackground) # Sky Background Information
    │ │ ├─level (int): -999999 # Sky Background Level
    │ │ ├─method (str): None # Sky Background Method
    │ │ └─subtracted (bool): False # Sky Background Subtraction Flag
    │ ├─cal_logs (CalLogs) # Calibration Log Messages
    │ │ ├─0 (str): 2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed
    │ │ └─1 (str): 2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected
    │ ├─cal_step (L2CalStep) # Level 2 Calibration Status
    │ │ ├─dq_init (str): INCOMPLETE # Data Quality Initialization Step
    │ │ ├─saturation (str): INCOMPLETE # Saturation Identification Step
    │ │ ├─refpix (str): INCOMPLETE # Reference Pixel Correction Step
    │ │ ├─linearity (str): INCOMPLETE # Classical Linearity Correction Step
    │ │ ├─dark (str): INCOMPLETE # Dark Current Subtraction Step
    │ │ ├─ramp_fit (str): INCOMPLETE # Ramp Fitting Step
    │ │ ├─assign_wcs (str): INCOMPLETE # Assign World Coordinate System (WCS) Step
    │ │ ├─flat_field (str): INCOMPLETE # Flat Field Correction Step
    │ │ ├─photom (str): INCOMPLETE # Populate Photometric Keywords Step
    │ │ ├─source_detection (str): INCOMPLETE # Source Detection Step
    │ │ ├─tweakreg (str): INCOMPLETE # Tweakreg step
    │ │ ├─flux (str): INCOMPLETE # Flux Scale Application Step
    │ │ ├─skymatch (str): INCOMPLETE # Sky Matching for Combining Overlapping Images Step
    │ │ └─outlier_detection (str): INCOMPLETE # Outlier Detection Step
    │ ├─calibration_software_name (CalibrationSoftwareName): RomanCAL # Calibration Software Name
    <<<<<<most of meta content elided>>>>>>
    │ ├─wcs (WCS)
    │ └─wcsinfo (Wcsinfo) # World Coordinate System (WCS) Information
    │   ├─aperture_name (str): WFI01_FULL # Aperture Name
    │   ├─pa_aperture (int): -999999 # Aperture Position Angle (deg)
    │   ├─v2_ref (int): -999999 # V2 Reference Position (arcsec)
    │   ├─v3_ref (int): -999999 # V3 Reference Position (arcsec)
    │   ├─vparity (int): -1 # Relative Rotation Between the Ideal and Telescope Axes
    │   ├─v3yangle (int): -999999 # Angle Between the V3 and Ideal Y Axes (deg)
    │   ├─ra_ref (int): -999999 # Right Ascension of the Reference Position (deg)
    │   ├─dec_ref (int): -999999 # Declination of the Reference Position (deg)
    │   ├─roll_ref (int): -999999 # V3 Position Angle at the Reference Position
    │   └─s_region (str): ? # Spatial Extent of the Exposure
    ├─data (NDArrayType): shape=(4088, 4088), dtype=float32 # Science Data (DN/s) or (MJy/sr)
    ├─dq (NDArrayType): shape=(4088, 4088), dtype=uint32 # Data Quality
    ├─err (NDArrayType): shape=(4088, 4088), dtype=float32 # Error (DN / s) or (MJy / sr)
    ├─var_poisson (NDArrayType): shape=(4088, 4088), dtype=float32 # Poisson Variance (DN^2/s^2) or (MJy^2/sr^2)
    ├─var_rnoise (NDArrayType): shape=(4088, 4088), dtype=float32 # Read Noise Variance (DN^2/s^2) or (MJy^2/sr^2)
    ├─var_flat (NDArrayType): shape=(4088, 4088), dtype=float32 # Flat Field Variance (DN^2/s^2) or (MJy^2/sr^2)
    ├─amp33 (NDArrayType): shape=(8, 4096, 128), dtype=uint16 # Amplifier 33 Reference Pixel Data (DN)
    ├─border_ref_pix_left (NDArrayType): shape=(8, 4096, 4), dtype=float32 # Left-Edge Border Reference Pixels (DN)
    ├─border_ref_pix_right (NDArrayType): shape=(8, 4096, 4), dtype=float32 # Right-Edge Border Reference Pixels (DN)
    ├─border_ref_pix_top (NDArrayType): shape=(8, 4096, 4), dtype=float32 # Border Reference Pixels on the Top of the Detector (DN)
    ├─border_ref_pix_bottom (NDArrayType): shape=(8, 4096, 4), dtype=float32 # Bottom-Edge Border Reference Pixels (DN)
    ├─dq_border_ref_pix_left (NDArrayType): shape=(4096, 4), dtype=uint32 # Left-Edge Border Reference Pixel Data Quality (DN)
    ├─dq_border_ref_pix_right (NDArrayType): shape=(4096, 4), dtype=uint32 # Right-Edge Border Reference Pixel Data Quality (DN)
    ├─dq_border_ref_pix_top (NDArrayType): shape=(4, 4096), dtype=uint32 # Border Reference Pixel Data Quality on the Top of the Detector (DN)
    └─dq_border_ref_pix_bottom (NDArrayType): shape=(4, 4096), dtype=uint32 # Bottom-Edge Border Reference Pixel Data Quality (DN)
