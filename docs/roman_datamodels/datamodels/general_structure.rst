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
- **close:**
- **get_primary_array_name:** the attribute name of the primary array
- **shape**: shape of primary array
- **to_flat_dict:** return all items as a flat dictionary with keys as dotted
  attribute paths such as ``meta.observation.date``
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
returns, that permits using ``dm.meta.observation.date`` to obtain the value of that attribute
instead of ``dm.tree['roman']['meta']['observation']['date']``. The latter can still be used
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
  │ └─version (str): 2.11.1
  ├─history (dict)
  │ └─extensions (list)
  │   ├─[0] (ExtensionMetadata)
  │   │ ├─extension_class (str): asdf.extension.BuiltinExtension
  │   │ └─software (Software)
  │   │   ├─name (str): asdf
  │   │   └─version (str): 2.11.1
  │   ├─[1] (ExtensionMetadata)
  │   │ ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │   │ ├─extension_uri (str): asdf://stsci.edu/datamodels/roman/extensions/datamodels-1.0
  │   │ └─software (Software)
  │   │   ├─name (str): roman-datamodels
  │   │   └─version (str): 0.12.2
  │   └─[2] (ExtensionMetadata)
  │     ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │     ├─extension_uri (str): asdf://asdf-format.org/core/extensions/core-1.5.0
  │     └─software (Software)
  │       ├─name (str): asdf-astropy
  │       └─version (str): 0.2.1
  └─roman (DarkRef) # Dark reference schema
    ├─meta (dict)
    │ ├─author (str): WFI Reference File Pipeline version 0.0.1
    │ ├─description (str): Updated reference files for CRDS 20220615. For Build 22Q3_B6 testing.
    │ ├─exposure (dict)
    │ │ ├─groupgap (int): 0
    │ │ ├─ma_table_name (str): High Latitude Spec. Survey
    │ │ ├─ma_table_number (int): 1
    │ │ ├─nframes (int): 8
    │ │ ├─ngroups (int): 6
    │ │ ├─p_exptype (str): WFI_IMAGE|
    │ │ └─type (str): WFI_IMAGE
    │ ├─instrument (dict)
    │ │ ├─detector (str): WFI07
    │ │ ├─name (str): WFI
    │ │ └─optical_element (str): F158
    │ ├─origin (str): STScI
    │ ├─pedigree (str): DUMMY
    │ ├─reftype (str): DARK
    │ ├─telescope (str): ROMAN
    │ └─useafter (Time)
    ├─data (NDArrayType): shape=(6, 4096, 4096), dtype=float32 # Dark current array
    ├─dq (NDArrayType): shape=(4096, 4096), dtype=uint32 # 2-D data quality array for all planes
    └─err (NDArrayType): shape=(6, 4096, 4096), dtype=float32 # Error array

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

The corresponding schema is::

    %YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/dark-1.0.0

    title: Dark reference schema

    type: object
    properties:
      meta:
        allOf:
          - $ref: ref_common-1.0.0
          - type: object
            properties:
              reftype:
                enum: [DARK]
              observation:
                type: object
                properties:
                  ma_table_name:
                    title: Identifier for the multi-accumulation table used
                    type: string
                required: [ma_table_name]
            required: [observation]
          - $ref: ref_exposure_type-1.0.0
          - $ref: ref_optical_element-1.0.0
      data:
        title: Dark current array
        tag: tag:stsci.edu:asdf/core/ndarray-1.0.0
        datatype: float32
        ndim: 3
      dq:
        title: 2-D data quality array for all planes
        tag: tag:stsci.edu:asdf/core/ndarray-1.0.0
        datatype: uint32
        ndim: 2
      err:
        title: Error array
        tag: tag:stsci.edu:asdf/core/ndarray-1.0.0
        datatype: float32
        ndim: 3
    required: [meta, data, dq, err]
    flowStyle: block
    propertyOrder: [meta, data, dq, err]
    ...

This won't go in to a great deal of detail about schemas but a few things will be
noted. The end of the schema lists the required attributes, and also specifies
the order they should appear in the YAML. The data array attributes specifies the
dimensionality of the arrays and their numeric type. The details of the ``meta``
are mostly specified in other schemas (done this way since these are shared
amongst many schemas), with exception of the ``reftype`` and ``observation``
attributes. For those one can see their type and sometimes their permissible
values are listed. The other schemas referenced are: ref_common-1.0.0,
ref_exposure_type-1.0.0, and ref_optical_element-1.0.0. These are displayed below.

ref_common-1.0.0::

    %YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_common-1.0.0

    title: Common reference metadata properties

    allOf:
    - type: object
      properties:
        reftype:
          title: Reference File type
          type: string
        pedigree:
          title: The pedigree of the reference file
          type: string
          enum: [GROUND, MODEL, DUMMY, SIMULATION]
        description:
          title: Description of the reference file
          type: string
        author:
          title: Author of the reference file
          type: string
        useafter:
          title: Use after date of the reference file
          tag: tag:stsci.edu:asdf/time/time-1.1.0
        telescope:
          title: Telescope data reference data is used to calibrate
          type: string
          enum: [ROMAN]
          type: string
        origin:
          title: Organization responsible for creating file
          type: string
      required: [reftype, author, description, pedigree, useafter, telescope, origin]
    ...

ref_exposure_type-1.0.0::

  %YAML 1.1
  ---
  $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
  id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type-1.0.0

  title: Type of data in the reference file exposure (viewing mode)

  type: object
  properties:
    exposure:
      type: object
      properties:
        type:
          allOf:
            - $ref: ../exposure_type-1.0.0
            - title: Type of data in the exposure (viewing mode)
      required: [type]
  required: [exposure]
  ...

ref_optical_element-1.0.0::

  %YAML 1.1
  ---
  $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
  id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_optical_element-1.0.0

  title: Name of the filter element used

  type: object
  properties:
    instrument:
      type: object
      properties:
        optical_element:
          allOf:
            - $ref: ../wfi_optical_element-1.0.0
      required: [optical_element]
  required: [instrument]
  ...

If one tries to modify the datamodel contents with a value inconsistent with
what a schema requires, validation will raise an error.

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
  │ └─version (str): 2.10.0
  ├─history (dict)
  │ └─extensions (list)
  │   ├─[0] (ExtensionMetadata)
  │   │ ├─extension_class (str): asdf.extension.BuiltinExtension
  │   │ └─software (Software)
  │   │   ├─name (str): asdf
  │   │   └─version (str): 2.10.0
  │   ├─[1] (ExtensionMetadata)
  │   │ ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │   │ ├─extension_uri (str): asdf://asdf-format.org/core/extensions/core-1.5.0
  │   │ └─software (Software)
  │   │   ├─name (str): asdf-astropy
  │   │   └─version (str): 0.2.1
  │   └─[2] (ExtensionMetadata)
  │     ├─extension_class (str): asdf.extension._manifest.ManifestExtension
  │     ├─extension_uri (str): asdf://stsci.edu/datamodels/roman/extensions/datamodels-1.0
  │     └─software (Software)
  │       ├─name (str): roman-datamodels
  │       └─version (str): 0.12.2
  └─roman (WfiScienceRaw) # The schema for Level 1 WFI science data (both imaging and spectrographic).

    ├─meta (dict)
    │ ├─aperture (Aperture) # Aperture information
    │ │ ├─name (str): WFI_CEN # PRD science aperture used
    │ │ └─position_angle (int): 120 # [deg] Position angle of aperture used
    │ ├─cal_step (L2CalStep) # Calibration Status
    │ │ ├─assign_wcs (str): INCOMPLETE # Assign World Coordinate System
    │ │ ├─flat_field (str): INCOMPLETE # Flat Field Step
    │ │ ├─dark (str): INCOMPLETE # Dark Subtraction
    │ │ ├─dq_init (str): INCOMPLETE # Data Quality Mask Step
    │ │ ├─jump (str): INCOMPLETE # Jump Detection Step
    │ │ ├─linearity (str): INCOMPLETE # Linearity Correction
    │ │ ├─photom (str): INCOMPLETE # Photometry Step
    │ │ ├─ramp_fit (str): INCOMPLETE # Ramp Fitting
    │ │ └─saturation (str): INCOMPLETE # Saturation Checking
    │ ├─calibration_software_version (str): 0.4.3.dev89+gca5771d
    │ ├─coordinates (Coordinates) # Information about the coordinates in the file
    │ │ └─reference_frame (str): ICRS # Name of the coordinate reference frame
    │ ├─crds_context_used (str): roman_0031.pmap
    │ ├─crds_software_version (str): 11.5.0
    │ ├─ephemeris (Ephemeris) # Ephemeris data information
    │ │ ├─earth_angle (float): 3.3161255787892263 # [radians] Earth Angle
    │ │ ├─moon_angle (float): 3.3196162372932148 # [radians] Moon Angle
    │ │ ├─sun_angle (float): 3.316474644639625 # [radians] Sun Angle
    │ │ ├─type (str): PREDICTED # Type of ephemeris
    │ │ ├─time (float): 59458.00172407407 # UTC time of position and velocity vectors in ephemeris (MJD)
    │ │ ├─ephemeris_reference_frame (str): EME2000 # Ephemeris reference frame
    │ │ ├─spatial_x (int): 100 # [km] X spatial coordinate of Roman
    │ │ ├─spatial_y (int): 20 # [km] Y spatial coordinate of Roman
    │ │ ├─spatial_z (int): 35 # [km] Z spatial coordinate of Roman
    │ │ ├─velocity_x (int): 10 # [km/s] X component of Roman velocity
    │ │ ├─velocity_y (int): 2 # [km/s] Y component of Roman velocity
    │ │ └─velocity_z (float): 3.5 # [km/s] Z component of Roman velocity
    │ ├─exposure (Exposure) # Exposure information

    │ │ ├─id (int): 1 # Exposure id number within visit
    │ │ ├─type (str): WFI_GRISM
    │ │ ├─start_time (Time) # UTC exposure start time
    │ │ ├─mid_time (Time) # UTC exposure mid time
    │ │ ├─end_time (Time) # UTC exposure end time
    │ │ ├─start_time_mjd (float): 59458.00172407407 # [d] exposure start time in MJD
    │ │ ├─mid_time_mjd (float): 59458.00258611111 # [d] exposure mid time in MJD
    │ │ ├─end_time_mjd (float): 59458.00344814815 # [d] exposure end time in MJD
    │ │ ├─start_time_tdb (float): 59458.00252479871 # [d] TDB time of exposure start in MJD
    │ │ ├─mid_time_tdb (float): 59458.00338683575 # [d] TDB time of exposure mid in MJD
    │ │ ├─end_time_tdb (float): 59458.004248872785 # [d] TDB time of exposure end in MJD
    │ │ ├─ngroups (int): 6 # Number of groups in integration
    │ │ ├─nframes (int): 8 # Number of frames per group
    │ │ ├─data_problem (bool): False # Science telemetry indicated a problem
    │ │ ├─sca_number (int): 1 # Sensor Chip Assembly number
    │ │ ├─gain_factor (int): 2 # Gain scale factor
    │ │ ├─integration_time (float): 197.47 # [s] Effective integration time
    │ │ ├─elapsed_exposure_time (float): 193.44 # [s] Total elapsed exposure time
    │ │ ├─frame_divisor (int): 6 # Divisor applied to frame-averaged groups
    │ │ ├─groupgap (int): 0 # Number of frames dropped between groups
    │ │ ├─frame_time (float): 4.03 # [s] Time between frames
    │ │ ├─group_time (float): 24.18 # [s] Time between groups
    │ │ ├─exposure_time (float): 145.92 # [s] exposure time
    │ │ ├─effective_exposure_time (float): 169.26 # [s] Effective exposure time
    │ │ ├─duration (float): 148.96 # [s] Total duration of exposure
    │ │ ├─ma_table_name (str): High Latitude Imaging Survey # Identifier for the multi-accumulation table used
    │ │ ├─ma_table_number (int): 1 # Numerical identifier for the multi-accumulation table used
    │ │ └─level0_compressed (bool): True # Level 0 data was compressed
    │ ├─file_date (Time)
    │ ├─filename (str): r0000201001001001002_01101_0001_WFI07_uncal.asdf
    │ ├─guidestar (Guidestar) # Guide star window information
    │ │ ├─gw_start_time (Time) # UTC time when guide star window activity started
    │ │ ├─gw_stop_time (Time) # UTC time when guide star window activity completed
    │ │ ├─gw_id (str): TEST # guide star window identifier
    │ │ ├─gs_ra (float): 83.87999291003202 # [deg] guide star right ascension
    │ │ ├─gs_dec (float): -69.32761623392035 # [deg] guide star declination
    │ │ ├─gs_ura (float): 0.0 # [deg] guide star right ascension uncertainty
    │ │ ├─gs_udec (float): 0.0 # [deg] guide star declination uncertainty
    │ │ ├─gs_mag (float): 17.0 # guide star magnitude in detector
    │ │ ├─gs_umag (float): 0.0 # guide star magnitude uncertainty
    │ │ ├─gw_fgs_mode (str): WIM-TRACK
    │ │ ├─gw_function_start_time (Time) # Observatory UTC time at guider function start
    │ │ ├─gw_function_end_time (Time) # Observatory UTC time at guider function end
    │ │ ├─data_start (float): 59458.00170671297 # MJD start time of guider data within this file
    │ │ ├─data_end (float): 59458.00172986111 # MJD end time of guider data within this file
    │ │ ├─gw_acq_exec_stat (str): SUCCESSFUL # Guide star window acquisition execution status
    │ │ ├─gs_ctd_x (float): 0.0 # [arcsec] guide star centroid x position in guider ideal frame
    │ │ ├─gs_ctd_y (float): 0.0 # [arcsec] guide star centroid y position in guider ideal frame
    │ │ ├─gs_ctd_ux (float): 0.0 # uncertainty in the x position of the centroid
    │ │ ├─gs_ctd_uy (float): 0.0 # uncertainty in the y position of the centroid
    │ │ ├─gs_epoch (str): J2000 # Epoch of guide star coordinates
    │ │ ├─gs_mura (float): 0.0 # [mas/yr] Guide star ICRS right ascension proper motion
    │ │ ├─gs_mudec (float): 0.0 # [mas/yr] Guide star ICRS declination proper motion
    │ │ ├─gs_para (float): 0.02 # Guide star annual parallax
    │ │ ├─gs_pattern_error (float): 0.0 # RMS of guide star position
    │ │ ├─gw_window_xsize (int): 16
    │ │ ├─gw_window_xstart (float): 2040.0
    │ │ ├─gw_window_ysize (int): 32
    │ │ └─gw_window_ystart (float): 2032.0
    │ ├─instrument (WfiMode) # WFI observing configuration

    │ │ ├─detector (str): WFI07
    │ │ ├─optical_element (str): GRISM
    │ │ └─name (str): WFI # Instrument used to acquire the data
    │ ├─model_type (str): WfiScienceRaw
    │ ├─observation (Observation) # Observation identifiers
    │ │ ├─obs_id (str): 0000201001001001002011010001 # Programmatic observation identifier. The format is 'PPPPPCCAAASSSOOOVVVggsaaeeee' where 'PPPPP' is the Program, 'CC' is the execution plan, 'AAA' is the pass, 'SSS' is the segment, 'OOO' is the Observation, 'VVV' is the Visit, 'gg' is the visit file group, 's' is the visit file sequence, 'aa' is the visit file activity, and 'eeee' is the exposure ID. The observation ID is the complete concatenation of visit_id + visit_file_statement (visit_file_group + visit_file_sequence + visit_file_activity) + exposure.
    │ │ ├─visit_id (str): 0000201001001001002 # A unique identifier for a visit. The format is 'PPPPPCCAAASSSOOOVVV' where 'PPPPP' is the Program, 'CC' is the execution plan, 'AAA' is the pass, 'SSS' is the segment number, 'OOO' is the Observation and 'VVV' is the Visit.
    │ │ ├─program (int): 2 # Program number, defined range is 1..18445; included in obs_id and visit_id as 'PPPPP'.
    │ │ ├─execution_plan (int): 1 # Execution plan within the program, defined range is 1..99; included in obs_id and visit_id as 'CC'.
    │ │ ├─pass (int): 1 # Pass number within execution plan, defined range is 1..999; included in obs_id and visit_id as 'AA'.
    │ │ ├─observation (int): 1 # Observation number within the segment, defined range is 1..999; included in obs_id and visit_id as 'OOO'.
    │ │ ├─segment (int): 1 # Segment Number within pass, defined range is 1..999; included in obs_id and visit_id as 'SSS'.
    │ │ ├─visit (int): 2 # Visit number within the observation, defined range of values is 1..999; included in obs_id and visit_id as 'VVV'.
    │ │ ├─visit_file_group (int): 1 # Sequence group within the visit file, defined range of values is 1..99; included in obs_id as 'gg'.
    │ │ ├─visit_file_sequence (int): 1 # Visit file sequence within the group, defined range of values is 1..5; included in obs_id as 's'.
    │ │ ├─visit_file_activity (str): 01 # Visit file activity within the sequence, defined range of values is 1..99; included in obs_id as 'aa'.
    │ │ ├─exposure (int): 1 # Exposure within the visit, defined range of values is 1..9999; included in obs_id as 'eeee'.
    │ │ ├─template (str): NONE # Observation template used
    │ │ ├─observation_label (str): TEST # Proposer label for the observation
    │ │ ├─survey (str): N/A # Observation Survey
    │ │ └─ma_table_name (str): High Latitude Spec. Survey
    │ ├─origin (str): STSCI
    │ ├─photometry (Photometry) # Photometry information
    │ │ ├─conversion_microjanskys (NoneType): None # Flux density (uJy/arcsec2) producing 1 cps
    │ │ ├─conversion_megajanskys (NoneType): None # Flux density (MJy/steradian) producing 1 cps
    │ │ ├─pixelarea_steradians (NoneType): None # Nominal pixel area in steradians
    │ │ ├─pixelarea_arcsecsq (NoneType): None # Nominal pixel area in arcsec^2
    │ │ ├─conversion_megajanskys_uncertainty (NoneType): None # Uncertainty in flux density conversion to MJy/steradians
    │ │ └─conversion_microjanskys_uncertainty (NoneType): None # Uncertainty in flux density conversion to uJy/steradians
    │ ├─pointing (Pointing) # Spacecraft pointing information
    │ │ ├─ra_v1 (float): 83.48452487142407 # [deg] RA of telescope V1 axis
    │ │ ├─dec_v1 (float): -68.84784021148778 # [deg] Dec of telescope V1 axis
    │ │ └─pa_v3 (float): 0.0 # [deg] Position angle of telescope V3 axis
    │ ├─prd_software_version (str): 0.0.1
    │ ├─program (Program) # Program information
    │ │ ├─title (str): TEST DATA # Proposal title
    │ │ ├─pi_name (str): DESJARDINS, TYLER # Principle Investigator name
    │ │ ├─category (str): GO # Program category
    │ │ ├─subcategory (str): NONE # Program subcategory
    │ │ ├─science_category (str): NONE # Science category assigned during TAC process
    │ │ └─continuation_id (int): 0 # Continuation of previous Program
    │ ├─ref_file (RefFile) # Reference file information
    │ │ └─crds (dict)
    │ │   ├─context_used (str): roman_0031.pmap
    │ │   └─sw_version (str): 11.5.0
    │ ├─sdf_software_version (str): 0.0.1
    │ ├─target (Target) # Target information
    │ │ ├─proposer_name (str): 30 Dor # Proposer's name for the target
    │ │ ├─catalog_name (str): NGC 2070 # Standard astronomical catalog name for target
    │ │ ├─type (str): FIXED # Type of target
    │ │ ├─ra (float): 84.675 # Target RA at mid time of exposure
    │ │ ├─dec (float): -69.1 # Target Dec at mid time of exposure
    │ │ ├─ra_uncertainty (float): 2.777777777777778e-05 # Target RA uncertainty
    │ │ ├─dec_uncertainty (float): 2.777777777777778e-05 # Target Dec uncertainty
    │ │ ├─proper_motion_ra (float): 0.0 # Target proper motion in RA
    │ │ ├─proper_motion_dec (float): 0.0 # Target proper motion in Dec
    │ │ ├─proper_motion_epoch (str): J2000 # Target proper motion epoch
    │ │ ├─proposer_ra (float): 84.675 # Proposer's target RA
    │ │ ├─proposer_dec (float): -69.1 # Proposer's target Dec
    │ │ └─source_type (str): EXTENDED # Source type used for calibration
    │ ├─telescope (str): ROMAN
    │ ├─velocity_aberration (VelocityAberration) # Velocity aberration correction information
    │ │ ├─ra_offset (float): -0.005234606668381048 # Velocity aberration right ascension offset
    │ │ ├─dec_offset (float): 0.0012031304993342928 # Velocity aberration declination offset
    │ │ └─scale_factor (float): 0.9999723133902021 # Velocity aberration scale factor
    │ ├─visit (Visit) # Visit information
    │ │ ├─engineering_quality (str): OK # Engineering data quality indicator from EngDB
    │ │ ├─pointing_engdb_quality (str): CALCULATED # Quality of pointing information from EngDB
    │ │ ├─type (str): None # Visit type
    │ │ ├─start_time (Time) # UTC visit start time
    │ │ ├─end_time (Time) # UTC visit end time
    │ │ ├─status (str): None # Status of a visit
    │ │ ├─total_exposures (int): 6 # Total number of planned exposures in visit
    │ │ ├─internal_target (bool): False # At least one exposure in visit is internal
    │ │ └─target_of_opportunity (bool): False # Visit scheduled as target of opportunity
    │ └─wcsinfo (Wcsinfo) # WCS parameters
    │   ├─v2_ref (float): 536.014439839392 # [arcsec] Telescope v2 coordinate of the reference point
    │   ├─v3_ref (float): -1718.747756607601 # [arcsec] Telescope v3 coordinate of the reference point
    │   ├─vparity (int): -1 # Relative sense of rotation between Ideal xy and V2V3
    │   ├─v3yangle (int): -60 # [deg] Angle from V3 axis to Ideal y axis
    │   ├─ra_ref (float): 83.87999291003202 # [deg] Right ascension of the reference point
    │   ├─dec_ref (float): -69.32761623392035 # [deg] Declination of the reference point
    │   ├─roll_ref (float): 0.0 # [deg] V3 roll angle at the ref point (N over E)
    │   └─s_region (str): NONE # spatial extent of the observation
    ├─data (NDArrayType): shape=(6, 4096, 4096), dtype=uint16 # Science data, including the border reference pixels.
    └─amp33 (NDArrayType): shape=(6, 4096, 128), dtype=uint16 # Amp 33 reference pixel data.


The corresponding schemas for this dataset are:

wfi_science_raw-1.0.0.yaml::

  %YAML 1.1
  ---
  $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
  id: asdf://stsci.edu/datamodels/roman/schemas/wfi_science_raw-1.0.0

  title: |
    The schema for Level 1 WFI science data (both imaging and spectrographic).

  type: object
  properties:
    meta:
      allOf:
        - $ref: common-1.0.0
    data:
      title: Science data, including the border reference pixels.
      tag: tag:stsci.edu:asdf/core/ndarray-1.0.0
      datatype: uint16
      ndim: 3
    amp33:
      title: Amp 33 reference pixel data.
      tag: tag:stsci.edu:asdf/core/ndarray-1.0.0
      datatype: uint16
      ndim: 3
  propertyOrder: [meta, data, amp33]
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
      aperture:
        tag: asdf://stsci.edu/datamodels/roman/tags/aperture-1.0.0
      cal_step:
        tag: asdf://stsci.edu/datamodels/roman/tags/l2_cal_step-1.0.0
      coordinates:
        tag: asdf://stsci.edu/datamodels/roman/tags/coordinates-1.0.0
      ephemeris:
        tag: asdf://stsci.edu/datamodels/roman/tags/ephemeris-1.0.0
      exposure:
        tag: asdf://stsci.edu/datamodels/roman/tags/exposure-1.0.0
      guidestar:
        tag: asdf://stsci.edu/datamodels/roman/tags/guidestar-1.0.0
      instrument:
        tag: asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.0.0
      observation:
        tag: asdf://stsci.edu/datamodels/roman/tags/observation-1.0.0
      pointing:
        tag: asdf://stsci.edu/datamodels/roman/tags/pointing-1.0.0
      program:
        tag: asdf://stsci.edu/datamodels/roman/tags/program-1.0.0
      ref_file:
        tag: asdf://stsci.edu/datamodels/roman/tags/ref_file-1.0.0
      target:
        tag: asdf://stsci.edu/datamodels/roman/tags/target-1.0.0
      velocity_aberration:
        tag: asdf://stsci.edu/datamodels/roman/tags/velocity_aberration-1.0.0
      visit:
        tag: asdf://stsci.edu/datamodels/roman/tags/visit-1.0.0
      wcsinfo:
        tag: asdf://stsci.edu/datamodels/roman/tags/wcsinfo-1.0.0
    required: [aperture, cal_step, coordinates, ephemeris, exposure, guidestar,
               instrument, observation, pointing, program, ref_file,
               target, velocity_aberration, visit, wcsinfo]
  ...

The rest of the included schemas are not shown to save space.

Level 2 Example
...............

The calibrated data has very much the same structure in the meta content.
The following example of Level 2 dataset is shown to show that it now
contains logging messages, and a noticeably different data content. Most
of the content has been removed to keep it reasonably short, as well as
not showing the associated schemas::

  root (AsdfObject)
  ├─asdf_library (Software)
  <<<<<<general asdf header elided>>>>>>
  └─roman (WfiImage) # The schema for WFI Level 2 images.

    ├─meta (dict)
    │ ├─aperture (Aperture) # Aperture information
    │ │ ├─name (str): WFI_CEN # PRD science aperture used
    │ │ └─position_angle (int): 120 # [deg] Position angle of aperture used
    <<<<<<most of meta content elided>>>>>>
    │ ├─wcs (WCS)
    │ └─wcsinfo (Wcsinfo) # WCS parameters
    │   ├─v2_ref (float): 536.014439839392 # [arcsec] Telescope v2 coordinate of the reference point
    │   ├─v3_ref (float): -1718.747756607601 # [arcsec] Telescope v3 coordinate of the reference point
    │   ├─vparity (int): -1 # Relative sense of rotation between Ideal xy and V2V3
    │   ├─v3yangle (int): -60 # [deg] Angle from V3 axis to Ideal y axis
    │   ├─ra_ref (float): 83.87999291003202 # [deg] Right ascension of the reference point
    │   ├─dec_ref (float): -69.32761623392035 # [deg] Declination of the reference point
    │   ├─roll_ref (float): 0.0 # [deg] V3 roll angle at the ref point (N over E)
    │   └─s_region (str): NONE # spatial extent of the observation
    ├─data (NDArrayType): shape=(4088, 4088), dtype=float32 # Science data, excluding border reference pixels.
    ├─dq (NDArrayType): shape=(4088, 4088), dtype=uint32
    ├─err (NDArrayType): shape=(4088, 4088), dtype=float32
    ├─var_poisson (NDArrayType): shape=(4088, 4088), dtype=float32
    ├─var_rnoise (NDArrayType): shape=(4088, 4088), dtype=float32
    ├─amp33 (NDArrayType): shape=(6, 4096, 128), dtype=uint16 # Amp 33 reference pixel data
    ├─border_ref_pix_left (NDArrayType): shape=(6, 4096, 4), dtype=float32 # Original border reference pixels, on left (from viewers perspective).
    ├─border_ref_pix_right (NDArrayType): shape=(6, 4096, 4), dtype=float32 # Original border reference pixels, on right (from viewers perspective).
    ├─border_ref_pix_top (NDArrayType): shape=(6, 4, 4096), dtype=float32 # Original border reference pixels, on top.
    ├─border_ref_pix_bottom (NDArrayType): shape=(6, 4, 4096), dtype=float32 # Original border reference pixels, on bottom.
    ├─dq_border_ref_pix_left (NDArrayType): shape=(4096, 4), dtype=uint32 # DQ for border reference pixels, on left (from viewers perspective).
    ├─dq_border_ref_pix_right (NDArrayType): shape=(4096, 4), dtype=uint32 # DQ for border reference pixels, on right (from viewers perspective).
    ├─dq_border_ref_pix_top (NDArrayType): shape=(4, 4096), dtype=uint32 # DQ for border reference pixels, on top.
    ├─dq_border_ref_pix_bottom (NDArrayType): shape=(4, 4096), dtype=uint32 # DQ for border reference pixels, on bottom.
    ├─cal_logs (CalLogs) # Calibration log messages
    │ ├─0 (str): 2022-06-07T12:11:10.762Z :: stpipe.ExposurePipeline.rampfit :: INFO :: Step rampfit running with args (<roman_datamodels.datamodels.RampModel object at 0x7fd3492a38b0>,).
    │ ├─1 (str): 2022-06-07T12:11:10.763Z :: stpipe.ExposurePipeline.rampfit :: INFO :: Step rampfit parameters are: {'pre_hooks': [], 'post_hooks': [], 'output_file': None, 'output_dir': None, 'output_ext': '.asdf', 'output_use_model': False, 'output_use_index': True, 'save_results': False, 'skip': False, 'suffix': None, 'search_output_file': True, 'input_dir': '', 'opt_name': '', 'maximum_cores': 'none', 'save_opt': False}
    │ ├─2 (str): 2022-06-07T12:11:11.817Z :: stpipe.ExposurePipeline.rampfit :: INFO :: Using READNOISE reference file: /Users/dencheva/crds_cache/references/roman/wfi/roman_wfi_readnoise_0227.asdf
    │ ├─3 (str): 2022-06-07T12:11:11.844Z :: stpipe.ExposurePipeline.rampfit :: INFO :: Using GAIN reference file: /Users/dencheva/crds_cache/references/roman/wfi/roman_wfi_gain_0089.asdf
    │ ├─4 (str): 2022-06-07T12:11:11.866Z :: stpipe.ExposurePipeline.rampfit :: INFO :: Using algorithm = ols
    <<<<<<most of the calibration log messages elided>>>>>>
    │ ├─97 (str): 2022-06-07T12:13:51.075Z :: stpipe.ExposurePipeline.photom :: INFO :: Step photom done
    │ └─98 (str): 2022-06-07T12:13:51.075Z :: stpipe.ExposurePipeline :: INFO :: Roman exposure calibration pipeline ending...
    └─output_file (str): r0000201001001001002_01101_0001_WFI07.asdf
