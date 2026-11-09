from collections.abc import Mapping

from py2mlog.mlog.selectable_params import (
    LookupSelectableParam,
    QuerySelectableParam,
    RadarSortSelectableParam,
    RadarTargetSelectableParam,
    SelectableParam,
    TileLayerSelectableParam,
    UnitLocateBuildingSelectableParam,
)
from py2mlog.mlog.suboperations import (
    ApplyStatusSuboperation,
    ConditionOpSuboperation,
    ControlSuboperation,
    CutsceneSuboperation,
    DrawSuboperation,
    FetchSuboperation,
    FlushMessageSuboperation,
    OperationSuboperation,
    PlaySoundSuboperation,
    QuerySuboperation,
    SetMarkerSuboperation,
    SetRuleSuboperation,
    Suboperation,
    UnitControlSuboperation,
    UnitLocateSuboperation,
)

MIMEX_VAR_ARG_NAMES = {"var", "int"}
MIMEX_SELECTABLE_PARAM_ARG_TYPE_MAP: Mapping[str, type[SelectableParam]] = {
    "RadarTarget": RadarTargetSelectableParam,
    "RadarSort": RadarSortSelectableParam,
    "ContentType": LookupSelectableParam,
    "BlockFlag": UnitLocateBuildingSelectableParam,
    "QueryType": QuerySelectableParam,
    "TileLayer": TileLayerSelectableParam,
}
MIMEX_SUBOP_ARG_TYPE_MAP: Mapping[
    str, type[Suboperation] | tuple[type[Suboperation], ...]
] = {
    "GraphicsType": DrawSuboperation,
    "LAccess": ControlSuboperation,
    "LogicOp": OperationSuboperation,
    "ConditionOp": ConditionOpSuboperation,
    "LUnitControl": UnitControlSuboperation,
    "LLocate": UnitLocateSuboperation,
    "QueryShape": QuerySuboperation,
    "boolean": (PlaySoundSuboperation, ApplyStatusSuboperation),
    "LogicRule": SetRuleSuboperation,
    "MessageType": FlushMessageSuboperation,
    "CutsceneAction": CutsceneSuboperation,
    "FetchType": FetchSuboperation,
    "LMarkerControl": SetMarkerSuboperation,
}
