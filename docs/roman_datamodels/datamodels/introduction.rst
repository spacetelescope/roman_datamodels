Introduction
============

This document provides documentation and examples for the roman datamodels package.

The use of datamodels for the calibration pipelines started with the JWST
calibration pipelines. The goal for the JWST pipelines was motivated primarily
by the need to support FITS data files, specifically with isolating the details
of where metadata and data were located in the FITS file from the representation
of the same items within the Python code. That is not a concern for Roman since
FITS format data files will not be used by the Roman calibration pipelines.

Nevertheless, there are other important benefits for using datamodels for the
Roman calibration pipeline. They essentially formalize both the expected
structure of the relevant data file and the corresponding Python object that
the pipeline will use. Since ASDF is being used, these correspond very closely.
Since the datamodels have corresponding schemas for the data files, these
schemas are used to validate the datafiles. Furthermore, these schemas also
include information used by the ground system to indicate where metadata and
data are obtained as well as their destination in the archive catalogs, and most
important, serve to keep the ground system definition of the data files and
the calibration pipeline definition in sync since both rely on the same schema
files.

The schema/datamodel system is also intrinsic to how the ASDF converter
machinery reads the ASDF file and converts the contents into Python objects.
In this usage, datamodel generally means the definition for a specific kind
of data file. It can apply to raw data (i.e., data from the ground system
that the calibration pipelines start with), intermediate data products, or
the final data products sent to observers or the archive.

While the roman_datamodels repository would seem like the location of the
Roman datamodels, it is the combination of the schemas in the rad repository
with the converter software in the roman_datamodels that form the totality
of the datamodels. The schemas are intentionally kept separate to remove
dependencies on Python as well as preventing extra notification noise to
the ground system when changes are only made to the Python code and not
the schemas.

The following documentation outlines the basic relationship between these
elements with links to some examples and a list of existing datamodels.

It should be noted that how datamodels are implemented for Roman has
significant difference from those used for JWST. These differences will
be explained at various points in the documentation.

Datamodel Outline
=================

To some extent, this is also a summary of how the ASDF converter
machinery works, as applied to Roman ASDF files.

As the ASDF file is read, each tag invokes the appropriate code to convert
the node contents to the corresponding Python object.

One important difference in the ASDF structure between JWST and Roman
is that the content starts at the top level of the ASDF tree. Unfortunately
there is no mechanism to tag the tree at the top level. For Roman, all the
content was placed as the value of the roman attribute at the top level, and
the content is then tagged as one of the permissible Roman datamodels.

Each Roman data file type corresponds to a specific Roman datamodel for which
there is a corresponding schema file for that datamodel. Any changes to the
structure of the data file must be accompanied by corresponding changes to the
schema. This ensures that the validation tools stay in sync with the file
contents.

Normally the validation is performed when the data are read from and written
to the ASDF file. This adds overhead to the processing and can be disabled if
the contents can be presumed to be correct, say as being used in normal
pipeline operations, but can also be used when diagnosing problems, or in
the development of pipeline code. It is particularly useful when receiving
possibly modified files from users who claim the pipeline isn't working with
the files they modified (knowingly or unknowingly).

Many pipeline steps rely on the use of datamodels that contain different types of
calibration data or information necessary for processing the data.
