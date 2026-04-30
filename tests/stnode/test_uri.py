from typing import Any

import pytest
from asdf.schema import load_schema
from semantic_version import Version

from roman_datamodels._stnode import UriInfo, get_latest_schema


@pytest.fixture(
    scope="module",
    params=(
        "asdf://example.com/uri/",
        "asdf://example.com/uri/fps/",
        "asdf://example.com/uri/tvac/",
        "asdf://example.com/uri/reference_files/",
    ),
)
def base_uri(request) -> str:
    """Fixture to provide a base of a URI for testing"""
    return request.param


@pytest.fixture(scope="module", params=("example", "example_other"))
def uri_name(request) -> str:
    """Fixture to provide a URI name for testing"""
    return request.param


@pytest.fixture(scope="module")
def prefix(base_uri: str, uri_name: str) -> str:
    """Fixture to provide a URI prefix for testing"""
    return f"{base_uri}{uri_name}"


@pytest.fixture(scope="module")
def snake_case(base_uri: str, uri_name: str) -> str:
    """Fixture to provide a snake_case representation of the URI for testing"""
    match base_uri:
        case "asdf://example.com/uri/":
            return uri_name
        case "asdf://example.com/uri/fps/":
            return f"fps_{uri_name}"
        case "asdf://example.com/uri/tvac/":
            return f"tvac_{uri_name}"
        case "asdf://example.com/uri/reference_files/":
            return f"{uri_name}_ref"
        case _:
            raise ValueError(f"Invalid base URI '{base_uri}' for testing")


@pytest.fixture(scope="module")
def camel_case_name(uri_name: str) -> str:
    """Fixture to provide a CamelCase name for testing"""
    match uri_name:
        case "example":
            return "Example"
        case "example_other":
            return "ExampleOther"
        case _:
            raise ValueError(f"Invalid URI name '{uri_name}' for testing")


@pytest.fixture(scope="module")
def camel_case(base_uri: str, camel_case_name: str) -> str:
    """Fixture to provide a CamelCase representation of the URI for testing"""
    match base_uri:
        case "asdf://example.com/uri/":
            return camel_case_name
        case "asdf://example.com/uri/fps/":
            return f"Fps{camel_case_name}"
        case "asdf://example.com/uri/tvac/":
            return f"Tvac{camel_case_name}"
        case "asdf://example.com/uri/reference_files/":
            return f"{camel_case_name}Ref"
        case _:
            raise ValueError(f"Invalid base URI '{base_uri}' for testing")


@pytest.fixture(
    scope="module",
    params=(None, "", "1", "37.", "3.14", "170.27.", "14.619.4", "*", "*.", "*.*", "*.*.", "*.*.*"),
)
def uri_input_version(request) -> str | None:
    """Fixture to provide a URI version for testing"""
    return request.param


@pytest.fixture(scope="module")
def uri_version(uri_input_version: str | None) -> str:
    """Fixture to provide a URI version based on the input version"""
    match uri_input_version:
        case None | "" | "*" | "*." | "*.*" | "*.*." | "*.*.*":
            return "0.0.0"
        case "1":
            return "1.0.0"
        case "37.":
            return "37.0.0"
        case "3.14":
            return "3.14.0"
        case "170.27.":
            return "170.27.0"
        case "14.619.4":
            return "14.619.4"
        case _:
            raise ValueError(f"Invalid input version '{uri_input_version}' for testing")


@pytest.fixture(scope="module")
def input_uri(prefix: str, uri_input_version: str | None) -> str:
    """Fixture to provide a full URI for testing"""
    if uri_input_version is None:
        return prefix

    return f"{prefix}-{uri_input_version}"


@pytest.fixture(scope="module")
def uri(prefix: str, uri_version: str) -> str:
    """Fixture to provide a full URI with version for testing"""
    return f"{prefix}-{uri_version}"


@pytest.fixture(scope="module")
def version(uri_version: str) -> Version:
    """Fixture to provide a URI version for testing"""
    return Version(uri_version)


@pytest.fixture(scope="module")
def latest_schema(latest_schema_uri: str) -> Any:
    """Fixture to provide the latest schema corresponding to a given tag URI for testing"""
    return load_schema(latest_schema_uri, resolve_references=True)


@pytest.fixture(scope="module")
def latest_manifest_schema(latest_manifest_uri: str) -> Any:
    """Fixture to provide the latest manifest schema for testing"""
    return load_schema(latest_manifest_uri, resolve_references=True)


@pytest.fixture(scope="module", params=(None, "", "-", "-*", "-*.", "-*.*", "-*.*.", "-*.*.*"))
def uri_suffix(request) -> None:
    """Fixture to provide suffixes to test that the class correctly identifies all versions of a tag URI"""
    return request.param


class TestBasic:
    """Test the UriInfo helper class that does not need asdf information to be tested"""

    @staticmethod
    @pytest.mark.parametrize(
        "uri_type, truth",
        (
            ("asdf_tag", (True, False, True)),
            ("asdf_resource", (False, True, True)),
            ("not_asdf", (False, False, False)),
        ),
    )
    def test_uri_type_options(uri_type: str, truth: tuple[bool, bool, bool]):
        """
        Test that the `uri_type` option sets the flags correctly

            truth -> (is_tag_uri, is_resource_uri, is_asdf_uri) bools
        """
        input_uri = "asdf://example.com/uri/test-1.0.0"

        uri = UriInfo(input_uri, uri_type)
        assert uri.is_tag_uri is truth[0]
        assert uri.is_resource_uri is truth[1]
        assert uri.is_asdf_uri is truth[2]

        with pytest.raises(ValueError, match=r"Invalid uri_type .* given for URI.*!"):
            UriInfo(input_uri, "invalid_uri_type")

    @staticmethod
    def test_uri(input_uri: str, uri: str):
        """Test that the URI is correctly computed from the input URI"""
        assert UriInfo(input_uri, "not_asdf").uri == uri

    @staticmethod
    def test_prefix(input_uri: str, prefix: str):
        """Test that the prefix is correctly computed from the URI"""
        assert UriInfo(input_uri, "not_asdf").prefix == prefix

    @staticmethod
    def test_version(input_uri: str, version: Version):
        """Test that the version is correctly computed from the input URI"""
        assert UriInfo(input_uri, "not_asdf").version == version

    @staticmethod
    @pytest.mark.parametrize("bad_version", ("a", "1.a", "1.0.a", "foo.*", "foo.bar.baz"))
    def test_bad_version(prefix: str, bad_version: str):
        """Test that invalid versions raise a ValueError"""
        with pytest.raises(ValueError, match=f"Invalid version '{bad_version}' in URI!"):
            UriInfo(f"{prefix}-{bad_version}", "not_asdf")

    @staticmethod
    def test_pattern(input_uri: str, prefix: str):
        """Test that the pattern is correctly computed from the URI"""
        assert UriInfo(input_uri, "not_asdf").pattern == f"{prefix}-*"

    @staticmethod
    def test_snake_case(input_uri: str, snake_case: str):
        """Test that the snake_case representation is correctly computed from the URI"""
        assert UriInfo(input_uri, "not_asdf").snake_case == snake_case

    @staticmethod
    def test_camel_case(input_uri: str, camel_case: str):
        """Test that the camel_case representation is correctly computed from the URI"""
        assert UriInfo(input_uri, "not_asdf").camel_case == camel_case


class TestAsdf:
    """Test the UriInfo helper class that needs asdf information to be tested"""

    @staticmethod
    def test_flags_for_not_resources(input_uri: str):
        """
        Test that the flags are set correctly when we don't specify the uri_type
            and the URI is not registered with ASDF
        """
        uri = UriInfo(input_uri)
        assert uri.is_tag_uri is False
        assert uri.is_resource_uri is False
        assert uri.is_asdf_uri is False

    @staticmethod
    def test_flags_for_tag_uri(tag_uri: str, uri_suffix: str | None):
        """Test that the class correctly flags all the tag URIS for RAD as ASDF URIs"""
        # Note we purposely don't specify the uri_type here to test that the class
        #    correctly identifies the tag URIs based on the registry
        uri = UriInfo(tag_uri)
        if uri_suffix is not None:
            uri = UriInfo(f"{uri.prefix}{uri_suffix}")

        assert uri.is_tag_uri is True
        assert uri.is_resource_uri is False
        assert uri.is_asdf_uri is True

    @staticmethod
    def test_flags_for_schema_uri(schema_uri: str, uri_suffix: str | None):
        """Test that the class correctly flags all the schema URIS for RAD as ASDF URIs"""
        # Note we purposely don't specify the uri_type here to test that the class
        #    correctly identifies the tag URIs based on the registry
        uri = UriInfo(schema_uri)
        if uri_suffix is not None:
            uri = UriInfo(f"{uri.prefix}{uri_suffix}")

        assert uri.is_tag_uri is False
        assert uri.is_resource_uri is True
        assert uri.is_asdf_uri is True

    @staticmethod
    def test_flags_for_manifest_uri(manifest_uri: str, uri_suffix: str | None):
        """Test that the class correctly flags all the manifest URIS for RAD as ASDF URIs"""
        # Note we purposely don't specify the uri_type here to test that the class
        #    correctly identifies the tag URIs based on the registry
        uri = UriInfo(manifest_uri)
        if uri_suffix is not None:
            uri = UriInfo(f"{uri.prefix}{uri_suffix}")

        assert uri.is_tag_uri is False
        assert uri.is_resource_uri is True
        assert uri.is_asdf_uri is True

    @staticmethod
    def test_resource_uri_for_tag_uri(tag_uri: str, schema_uri: str):
        """Test that the resource URI is correctly computed for a tag URI"""
        assert UriInfo(tag_uri, "asdf_tag").resource_uri == UriInfo(schema_uri, "asdf_resource")

    @staticmethod
    def test_resource_uri_for_schema_uri(schema_uri: str):
        """Test that the resource URI is correctly computed for a schema URI"""
        assert (uri_info := UriInfo(schema_uri, "asdf_resource")).resource_uri is uri_info

    @staticmethod
    def test_resource_uri_for_manifest_uri(manifest_uri: str):
        """Test that the resource URI is correctly computed for a manifest URI"""
        assert (uri_info := UriInfo(manifest_uri, "asdf_resource")).resource_uri is uri_info

    @staticmethod
    def test_tag_uri_for_tag_uri(tag_uri: str):
        """Test that the tag URI is correctly computed for a tag URI"""
        assert (uri_info := UriInfo(tag_uri, "asdf_tag")).tag_uri is uri_info

    @staticmethod
    def test_tag_uri_for_schema_uri(tag_uri: str, schema_uri: str):
        """Test that the tag URI is correctly computed for a schema URI"""
        assert UriInfo(schema_uri, "asdf_resource").tag_uri == UriInfo(tag_uri, "asdf_tag")

    @staticmethod
    def test_tag_uri_for_manifest_uri(manifest_uri: str):
        """
        Test that the tag URI raises an error for the manifest URI since it
        doesn't have a corresponding tag URI
        """
        with pytest.raises(ValueError, match=r"ASDF resource URI .* is not associated with any tag URI in ASDF!"):
            _ = UriInfo(manifest_uri, "asdf_resource").tag_uri

    @staticmethod
    def test_schema_tag_uri(tag_uri: str, schema: Any):
        """Test that the schema is correctly loaded from the tag URI"""
        assert UriInfo(tag_uri, "asdf_tag").schema == schema

    @staticmethod
    def test_schema_schema_uri(schema_uri: str, schema: Any):
        """Test that the schema is correctly loaded from the schema URI"""
        assert UriInfo(schema_uri, "asdf_resource").schema == schema

    @staticmethod
    def test_schema_manifest_uri(manifest_uri: str, manifest_schema: Any):
        """Test that the schema is correctly loaded from the manifest URI"""
        assert UriInfo(manifest_uri, "asdf_resource").schema == manifest_schema

    @staticmethod
    def test_latest_uri_tag_uri(tag_uri: str, latest_tag_uri: str):
        """Test that the latest tag URI is correctly computed from the tag URI"""
        assert UriInfo(tag_uri, "asdf_tag").latest_uri == UriInfo(latest_tag_uri, "asdf_tag")

    @staticmethod
    def test_latest_uri_schema_uri(schema_uri: str, latest_schema_uri: str):
        """Test that the latest tag URI is correctly computed from the schema URI"""
        assert UriInfo(schema_uri, "asdf_resource").latest_uri == UriInfo(latest_schema_uri, "asdf_resource")

    @staticmethod
    def test_latest_uri_manifest_uri(manifest_uri: str, latest_manifest_uri: str):
        """Test that the latest tag URI is correctly computed from the manifest URI"""
        assert UriInfo(manifest_uri, "asdf_resource").latest_uri == UriInfo(latest_manifest_uri, "asdf_resource")

    @staticmethod
    def test_get_latest_schema_tag_uri(tag_uri: str, latest_schema_uri: str, latest_schema: Any, uri_suffix: str | None):
        """Test that the get_latest_schema function correctly gets the latest schema for a given URI"""
        uri_info = UriInfo(tag_uri, "asdf_tag")
        if uri_suffix is not None:
            uri_info = UriInfo(f"{uri_info.prefix}{uri_suffix}", "asdf_tag")

        uri, schema = get_latest_schema(uri_info.uri)

        assert uri == latest_schema_uri
        assert schema == latest_schema

    @staticmethod
    def test_get_latest_schema_schema_uri(schema_uri: str, latest_schema_uri: str, latest_schema: Any, uri_suffix: str | None):
        """Test that the get_latest_schema function correctly gets the latest schema for a given URI"""
        uri_info = UriInfo(schema_uri, "asdf_resource")
        if uri_suffix is not None:
            uri_info = UriInfo(f"{uri_info.prefix}{uri_suffix}", "asdf_resource")

        uri, schema = get_latest_schema(uri_info.uri)

        assert uri == latest_schema_uri
        assert schema == latest_schema

    @staticmethod
    def test_get_latest_schema_manifest_uri(
        manifest_uri: str, latest_manifest_uri: str, latest_manifest_schema: Any, uri_suffix: str | None
    ):
        """Test that the get_latest_schema function correctly gets the latest schema for a given URI"""
        uri_info = UriInfo(manifest_uri, "asdf_resource")
        if uri_suffix is not None:
            uri_info = UriInfo(f"{uri_info.prefix}{uri_suffix}", "asdf_resource")

        uri, schema = get_latest_schema(uri_info.uri)

        assert uri == latest_manifest_uri
        assert schema == latest_manifest_schema
