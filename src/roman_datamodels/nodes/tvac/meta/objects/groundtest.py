import numpy as np
import numpy.typing as npt
from astropy.time import Time
from astropy.units import A, K, Quantity, V, cm, ms, nm  # type: ignore[attr-defined]

from roman_datamodels.stnode import core, rad

__all__ = ["TvacGroundtest", "TvacGroundtestGsorcSdsDqPulseEntry", "TvacGroundtestWfiOptTargettypeEntry"]


class TvacGroundtestGsorcSdsDqPulseEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible values of the GSORC SDS DQ Pulse
    """

    PULSE = "pulse"
    CW = "cw"

    @classmethod
    def _asdf_container(cls) -> type:
        return TvacGroundtest

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "gsorc_sds_dq_pulse"


class TvacGroundtestWfiOptTargettypeEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible values of the WFI Optical Target Type
    """

    NONE = "NONE"
    FLAT_SRCS = "FLAT-sRCS"
    FLAT_SORC = "FLAT-SORC"
    POINT_SOURCE = "POINT SOURCE"
    SPECTRUM = "SPECTRUM"
    DARK = "DARK"
    DARK_DARKEL = "DARK-DARKEL"
    DARK_W146 = "DARK-W146"
    PHARET_GW = "PHARET-GW"
    PHARET_FF = "PHARET-FF"
    PHARET_FF_F158 = "PHARET-FF-F158"
    PHARET_FF_M3MM = "PHARET-FF-M3MM"
    PHARET_FF_M6MM = "PHARET-FF-M6MM"
    PHARET_FF_P3MM = "PHARET-FF-P3MM"
    PHARET_FF_P6MM = "PHARET-FF-P6MM"
    PHARET_FF_PRISM = "PHARET-FF-PRISM"
    PHARET_FF_W146 = "PHARET-FF-W146"
    POINT_SOURCE_GW = "POINT-SOURCE-GW"
    STRAY_LIGHT = "STRAY LIGHT"

    @classmethod
    def _asdf_container(cls) -> type:
        return TvacGroundtest

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "wfi_opt_targettype"


class TvacGroundtest(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/groundtest-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/groundtest-1.0.0"
        }

    @rad.field
    def test_name(self) -> str:
        return rad.NOSTR

    @rad.field
    def test_phase(self) -> str:
        return rad.NOSTR

    @rad.field
    def test_environment(self) -> str:
        return rad.NOSTR

    @rad.field
    def test_script(self) -> str:
        return rad.NOSTR

    @rad.field
    def product_date(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def product_version(self) -> str:
        return rad.NOSTR

    @rad.field
    def conversion_date(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def conversion_version(self) -> str:
        return rad.NOSTR

    @rad.field
    def filename_pnt5(self) -> str:
        return rad.NOSTR

    @rad.field
    def filepath_level_pnt5(self) -> str:
        return rad.NOSTR

    @rad.field
    def filename_l1a(self) -> str:
        return rad.NOSTR

    @rad.field
    def detector_id(self) -> str:
        return rad.NOSTR

    @rad.field
    def detector_temp(self) -> float:
        return rad.NONUM

    @rad.field
    def frames_temp(self) -> npt.NDArray[np.float64]:
        return np.zeros(6, dtype=np.float64)

    @rad.field
    def ota_temp(self) -> float:
        return rad.NONUM

    @rad.field
    def rcs_on(self) -> bool:
        return False

    @rad.field
    def readout_col_num(self) -> int:
        return rad.NOINT

    @rad.field
    def detector_pixel_size(self) -> Quantity:
        return Quantity(np.zeros(6, dtype=np.float64), unit=cm, dtype=np.float64)

    @rad.field
    def sensor_error(self) -> npt.NDArray[np.float64]:
        return np.zeros(6, dtype=np.float64)

    @rad.field
    def activity_number(self) -> int:
        return rad.NOINT

    @rad.field
    def led_bank1_band_number_on(self) -> core.LNode[int]:
        return core.LNode([rad.NOINT])

    @rad.field
    def led_bank2_bank1_number_on(self) -> core.LNode[int]:
        return core.LNode([rad.NOINT])

    @rad.field
    def led_bank1_approx_wlen(self) -> Quantity:
        return Quantity(np.zeros(6, dtype=np.float64), unit=nm, dtype=np.float64)

    @rad.field
    def led_bank2_approx_wlen(self) -> Quantity:
        return Quantity(np.zeros(6, dtype=np.float64), unit=nm, dtype=np.float64)

    @rad.field
    def srcs_pd_voltage(self) -> float:
        return rad.NONUM

    @rad.field
    def srcs_led_flux(self) -> float:
        return rad.NONUM

    @rad.field
    def wfi_mce_srcs_bank1_led_i(self) -> Quantity:
        return Quantity(np.zeros(6, dtype=np.float64), unit=A, dtype=np.float64)

    @rad.field
    def wfi_mce_srcs_bank1_led_range(self) -> str:
        return rad.NOSTR

    @rad.field
    def wfi_mce_srcs_bank2_led_i(self) -> Quantity:
        return Quantity(np.zeros(6, dtype=np.float64), unit=A, dtype=np.float64)

    @rad.field
    def wfi_mce_srcs_bank2_led_range(self) -> str:
        return rad.NOSTR

    @rad.field
    def srcs_led_current(self) -> float:
        return rad.NONUM

    @rad.field
    def wfi_opt_targettype(self) -> TvacGroundtestWfiOptTargettypeEntry:
        return TvacGroundtestWfiOptTargettypeEntry.FLAT_SRCS

    @rad.field
    def analysis_tag(self) -> str:
        return rad.NOSTR

    @rad.field
    def gsorc_pose_mode(self) -> str:
        return rad.NOSTR

    @rad.field
    def gsorc_pose_target(self) -> str:
        return rad.NOSTR

    @rad.field
    def gsorc_sds_active_atten(self) -> float:
        return rad.NONUM

    @rad.field
    def gsorc_sds_lltfir_wave(self) -> float:
        return rad.NONUM

    @rad.field
    def gsorc_sds_sorc_on(self) -> bool:
        return False

    @rad.field
    def gsorc_sds_sorc_wlen(self) -> float:
        return rad.NONUM

    @rad.field
    def gsorc_sds_active_source(self) -> str:
        return rad.NOSTR

    @rad.field
    def gsorc_sds_dq_pulse(self) -> TvacGroundtestGsorcSdsDqPulseEntry:
        return TvacGroundtestGsorcSdsDqPulseEntry.PULSE

    @rad.field
    def gsorc_sds_daq_pw(self) -> Quantity:
        return Quantity(rad.NONUM, ms)

    @rad.field
    def gsorc_heater1_setpt(self) -> float:
        return rad.NONUM

    @rad.field
    def wfi_otp_wfi_ewa(self) -> str:
        return rad.NOSTR

    @rad.field
    def sca_temp(self) -> Quantity:
        return Quantity(rad.NONUM, K)

    @rad.field
    def mpa_temp(self) -> Quantity:
        return Quantity(rad.NONUM, K)

    @rad.field
    def ewa_temp(self) -> Quantity:
        return Quantity(rad.NONUM, K)

    @rad.field
    def ewta_outer_heater_temp(self) -> Quantity:
        return Quantity(rad.NONUM, K)

    @rad.field
    def ewta_inner_heater_temp(self) -> Quantity:
        return Quantity(rad.NONUM, K)

    @rad.field
    def coba_temp_near_ewta(self) -> Quantity:
        return Quantity(rad.NONUM, K)

    @rad.field
    def scea_temp(self) -> Quantity:
        return Quantity(rad.NONUM, K)

    @rad.field
    def wfi_sce_1_vbiasgate_v(self) -> Quantity:
        return Quantity(rad.NONUM, V)

    @rad.field
    def wfi_sce_1_vbiaspwr_i(self) -> Quantity:
        return Quantity(rad.NONUM, A)

    @rad.field
    def wfi_sce_1_vbiaspwr_v(self) -> Quantity:
        return Quantity(rad.NONUM, V)

    @rad.field
    def wfi_sce_1_vreset_v(self) -> Quantity:
        return Quantity(rad.NONUM, V)

    @rad.field
    def wfi_sce_1_vreset_i(self) -> Quantity:
        return Quantity(rad.NONUM, A)

    @rad.field
    def wfi_mcu_a_offs_csense_fpssen(self) -> Quantity:
        return Quantity(rad.NONUM, K)
