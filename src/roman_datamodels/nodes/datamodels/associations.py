from roman_datamodels.stnode import core, rad

__all__ = [
    "Associations",
    "AssociationsExptypeEntry",
    "Associations_Products",
    "Associations_Products_Members",
]


class AssociationsExptypeEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for exptype in associations
    """

    SCIENCE = "SCIENCE"
    CALIBRATION = "CALIBRATION"
    ENGINEERING = "ENGINEERING"

    @classmethod
    def _asdf_container(cls) -> type:
        return Associations_Products_Members

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "exptype"


class Associations_Products_Members(rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return Associations_Products

    @rad.field
    def expname(self) -> str:
        return "file_0"

    @rad.field
    def exposerr(self) -> str:
        return "null"

    @rad.field
    def exptype(self) -> AssociationsExptypeEntry:
        return AssociationsExptypeEntry.SCIENCE


class Associations_Products(rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return Associations

    @rad.field
    def name(self) -> str:
        return "product0"

    @rad.field
    def members(self) -> core.LNode[Associations_Products_Members]:
        return core.LNode([])


class Associations(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/associations-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/associations-1.0.0",
        }

    @property
    def primary_array_shape(self) -> tuple[int] | None:
        """
        Override the default primary array shape as it does not have one
        """
        return None

    @property
    def default_array_shape(self) -> tuple[int, int, int]:
        return (2, 3, 1)

    @property
    def testing_array_shape(self) -> tuple[int, int, int, int]:
        return (3, 8, 5, 2)

    @rad.field
    def asn_id(self) -> str:
        return "o036"

    @rad.field
    def asn_pool(self) -> str:
        return "r00001_20200530t023154_pool"

    @rad.field
    def asn_type(self) -> str:
        return "image"

    @rad.field
    def asn_rule(self) -> str:
        return "candidate_Asn_Lv2Image_i2d"

    @rad.field
    def version_id(self) -> str:
        return "null"

    @rad.field
    def code_version(self) -> str:
        return "0.16.2.dev16+g640b0b7"

    @rad.field
    def degraded_status(self) -> str:
        return "No known degraded exposures in association."

    @rad.field
    def program(self) -> int:
        return 1

    @rad.field
    def target(self) -> int:
        return 16

    @rad.field
    def constraints(self) -> str:
        return (
            "DMSAttrConstraint({'name': 'program', 'sources': ['program'], "
            "'value': '001'})\nConstraint_TargetAcq({'name': 'target_acq', 'value': "
            "'target_acquisition'})\nDMSAttrConstraint({'name': 'science', "
            "'DMSAttrConstraint({'name': 'asn_candidate','sources': "
            "['asn_candidate'], 'value': \"\\\\('o036',\\\\ 'observation'\\\\)\"})"
        )

    # TODO: need to add a rule to extend typeguard to check the argument of the decorator
    #       currently this only checks that it is an LNode
    @rad.field
    def products(self) -> core.LNode[Associations_Products]:
        file_idx = 0
        products = []
        CHOICES = ["SCIENCE", "CALIBRATION", "ENGINEERING"]
        for product_idx, members in enumerate(self.array_shape):
            members_lst = []
            for member_idx in range(members):
                members_lst.append(
                    Associations_Products_Members(
                        {"expname": "file_" + str(file_idx) + ".asdf", "exposerr": "null", "exptype": CHOICES[member_idx % 3]}
                    )
                )
                file_idx += 1
            products.append(Associations_Products({"name": f"product{product_idx}", "members": core.LNode(members_lst)}))

        return core.LNode(products)
