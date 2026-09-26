import pytest

from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.instruction import Instruction, Label
from py2mlog.mlog.codegen import generate_mlog
from py2mlog.mlog.selectable_params import *
from py2mlog.mlog.mlog_expressions import *
from py2mlog.mlog.suboperations import *


@pytest.mark.parametrize(
    ("script", "expected"),
    [
        pytest.param(
            [
                Instruction(
                    InstructionType.READ,
                    None,
                    (),
                    (MlogVar("result1"), MlogVar("cell1"), MlogNumberLiteral(0)),
                ),
                Instruction(
                    InstructionType.WRITE,
                    None,
                    (),
                    (MlogVar("result2"), MlogVar("cell2"), MlogNumberLiteral(1)),
                ),
                Instruction(
                    InstructionType.DRAW,
                    DrawSuboperation.CLEAR,
                    (),
                    (
                        MlogNumberLiteral(255),
                        MlogNumberLiteral(255),
                        MlogNumberLiteral(255),
                    ),
                ),
                Instruction(
                    InstructionType.DRAW,
                    DrawSuboperation.LINE_RECT,
                    (),
                    (
                        MlogNumberLiteral(10),
                        MlogNumberLiteral(20),
                        MlogNumberLiteral(40),
                        MlogNumberLiteral(50),
                    ),
                ),
                Instruction(
                    InstructionType.PRINT, None, (), (MlogStringLiteral("frog"),)
                ),
                Instruction(
                    InstructionType.PRINT_CHAR, None, (), (MlogNumberLiteral(65),)
                ),
                Instruction(InstructionType.FORMAT, None, (), (MlogVar("frog2"),)),
            ],
            "\n".join(
                (
                    "read result1 cell1 0",
                    "write result2 cell2 1",
                    "draw clear 255 255 255",
                    "draw lineRect 10 20 40 50",
                    'print "frog"',
                    "printchar 65",
                    "format frog2",
                )
            ),
            id="io-instructions",
        ),
        pytest.param(
            [
                Instruction(
                    InstructionType.DRAW_FLUSH, None, (), (MlogVar("display1"),)
                ),
                Instruction(
                    InstructionType.PRINT_FLUSH, None, (), (MlogVar("message1"),)
                ),
                Instruction(
                    InstructionType.GET_LINK,
                    None,
                    (),
                    (MlogVar("result"), MlogNumberLiteral(0)),
                ),
                Instruction(
                    InstructionType.CONTROL,
                    ControlSuboperation.ENABLED,
                    (),
                    (MlogVar("block1"), MlogVar("enabled")),
                ),
                Instruction(
                    InstructionType.RADAR,
                    None,
                    (
                        RadarTargetSelectableParam.ENEMY,
                        RadarTargetSelectableParam.ATTACKER,
                        RadarTargetSelectableParam.FLYING,
                        RadarSortSelectableParam.MAX_HEALTH,
                    ),
                    (MlogVar("turret1"), MlogNumberLiteral(1), MlogVar("enemy")),
                ),
                Instruction(
                    InstructionType.SENSOR,
                    None,
                    (),
                    (MlogVar("count"), MlogVar("block2"), MlogBuiltin("copper")),
                ),
            ],
            "\n".join(
                (
                    "drawflush display1",
                    "printflush message1",
                    "getlink result 0",
                    "control enabled block1 enabled",
                    "radar enemy attacker flying maxHealth turret1 1 enemy",
                    "sensor count block2 @copper",
                )
            ),
            id="block-control-instructions",
        ),
        pytest.param(
            [
                Instruction(
                    InstructionType.SET,
                    None,
                    (),
                    (MlogVar("result1"), MlogNumberLiteral(0)),
                ),
                Instruction(
                    InstructionType.OPERATION,
                    OperationSuboperation.ADD,
                    (),
                    (MlogVar("result2"), MlogVar("a"), MlogVar("b")),
                ),
                Instruction(
                    InstructionType.OPERATION,
                    OperationSuboperation.LOGICAL_AND,
                    (),
                    (MlogVar("result3"), MlogVar("a"), MlogVar("b")),
                ),
                Instruction(
                    InstructionType.OPERATION,
                    OperationSuboperation.MIN,
                    (),
                    (MlogVar("result4"), MlogVar("a"), MlogVar("b")),
                ),
                Instruction(
                    InstructionType.OPERATION,
                    OperationSuboperation.COS,
                    (),
                    (MlogVar("result5"), MlogVar("a")),
                ),
                Instruction(
                    InstructionType.SELECT,
                    ConditionOpSuboperation.NOT_EQUAL,
                    (),
                    (
                        MlogVar("result6"),
                        MlogVar("x"),
                        MlogBoolLiteral(False),
                        MlogVar("a"),
                        MlogVar("b"),
                    ),
                ),
                Instruction(
                    InstructionType.SELECT,
                    ConditionOpSuboperation.ALWAYS,
                    (),
                    (
                        MlogVar("result7"),
                        MlogVar("c"),
                    ),
                ),
                Instruction(
                    InstructionType.LOOKUP,
                    None,
                    (LookupSelectableParam.ITEM,),
                    (MlogVar("result8"), MlogNumberLiteral(0)),
                ),
                Instruction(
                    InstructionType.LOOKUP,
                    None,
                    (LookupSelectableParam.BLOCK,),
                    (MlogVar("result9"), MlogVar("i")),
                ),
                Instruction(
                    InstructionType.PACK_COLOR,
                    None,
                    (),
                    (
                        MlogVar("result10"),
                        MlogNumberLiteral(1),
                        MlogVar("g"),
                        MlogVar("b"),
                        MlogNumberLiteral(0),
                    ),
                ),
                Instruction(
                    InstructionType.UNPACK_COLOR,
                    None,
                    (),
                    (
                        MlogVar("r"),
                        MlogVar("g"),
                        MlogVar("b"),
                        MlogVar("a"),
                        MlogVar("color"),
                    ),
                ),
            ],
            "\n".join(
                (
                    "set result1 0",
                    "op add result2 a b",
                    "op land result3 a b",
                    "op min result4 a b",
                    "op cos result5 a",
                    "select result6 notEqual x false a b",
                    "select result7 always _ _ c",
                    "lookup item result8 0",
                    "lookup block result9 i",
                    "packcolor result10 1 g b 0",
                    "unpackcolor r g b a color",
                )
            ),
            id="operation-instructions",
        ),
        pytest.param(
            [
                Instruction(InstructionType.WAIT, None, (), (MlogNumberLiteral(0),)),
                Instruction(InstructionType.WAIT, None, (), (MlogVar("time"),)),
                Instruction(InstructionType.STOP, None, (), ()),
                Instruction(InstructionType.END, None, (), ()),
                Instruction(
                    InstructionType.JUMP,
                    ConditionOpSuboperation.EQUAL,
                    (),
                    (MlogNumberLiteral(67), MlogVar("x"), MlogBuiltin("copper")),
                ),
                Instruction(
                    InstructionType.JUMP,
                    ConditionOpSuboperation.ALWAYS,
                    (),
                    (LabelRef("someLabel"),),
                ),
                Label("someLabel"),
                Instruction(
                    InstructionType.SET_RATE, None, (), (MlogNumberLiteral(10),)
                ),
            ],
            "\n".join(
                (
                    "wait 0",
                    "wait time",
                    "stop",
                    "end",
                    "jump 67 equal x @copper",
                    "jump someLabel always",
                    "someLabel:",
                    "setrate 10",
                )
            ),
            id="flow-control-instructions",
        ),
        pytest.param(
            [
                Instruction(
                    InstructionType.UNIT_BIND, None, (), (MlogVar("unitType"),)
                ),
                Instruction(
                    InstructionType.UNIT_CONTROL, UnitControlSuboperation.IDLE, (), ()
                ),
                Instruction(
                    InstructionType.UNIT_CONTROL,
                    UnitControlSuboperation.BOOST,
                    (),
                    (MlogBoolLiteral(True),),
                ),
                Instruction(
                    InstructionType.UNIT_CONTROL,
                    UnitControlSuboperation.ITEM_TAKE,
                    (),
                    (MlogVar("nucleus1"), MlogVar("itemType"), MlogNumberLiteral(99)),
                ),
                Instruction(
                    InstructionType.UNIT_RADAR,
                    None,
                    (
                        RadarTargetSelectableParam.FLYING,
                        RadarTargetSelectableParam.ENEMY,
                        RadarTargetSelectableParam.ANY,
                        RadarSortSelectableParam.ARMOR,
                    ),
                    (
                        MlogNumberLiteral(1),
                        MlogVar("enemy"),
                    ),
                ),
                Instruction(
                    InstructionType.UNIT_LOCATE,
                    UnitLocateSuboperation.ORE,
                    (),
                    (
                        MlogBuiltin("lead"),
                        MlogVar("oreX"),
                        MlogVar("oreY"),
                        MlogVar("oreFound"),
                    ),
                ),
                Instruction(
                    InstructionType.UNIT_LOCATE,
                    UnitLocateSuboperation.BUILDING,
                    (UnitLocateBuildingSelectableParam.CORE,),
                    (
                        MlogBoolLiteral(True),
                        MlogVar("coreX"),
                        MlogVar("coreY"),
                        MlogVar("coreFound"),
                        MlogVar("core"),
                    ),
                ),
            ],
            "\n".join(
                (
                    "ubind unitType",
                    "ucontrol idle",
                    "ucontrol boost true",
                    "ucontrol itemTake nucleus1 itemType 99",
                    "uradar flying enemy any armor _ 1 enemy",
                    "ulocate ore _ _ @lead oreX oreY oreFound",
                    "ulocate building core true _ coreX coreY coreFound core",
                )
            ),
            id="unit-control-instructions",
        ),
        pytest.param(
            [
                Instruction(
                    InstructionType.QUERY,
                    QuerySuboperation.CIRCLE,
                    (QuerySelectableParam.UNIT,),
                    (
                        MlogBuiltin("sharded"),
                        MlogNumberLiteral(67),
                        MlogNumberLiteral(42),
                        MlogNumberLiteral(5),
                    ),
                ),
                Instruction(
                    InstructionType.SET_BLOCK,
                    SetBlockSuboperation.ORE,
                    (),
                    (MlogBuiltin("air"), MlogNumberLiteral(6), MlogNumberLiteral(7)),
                ),
                Instruction(
                    InstructionType.GET_BLOCK,
                    None,
                    (TileLayerSelectableParam.FLOOR,),
                    (MlogVar("result1"), MlogNumberLiteral(0), MlogNumberLiteral(0)),
                ),
                Instruction(
                    InstructionType.SPAWN_UNIT,
                    None,
                    (),
                    (
                        MlogBuiltin("dagger"),
                        MlogNumberLiteral(42),
                        MlogNumberLiteral(67),
                        MlogNumberLiteral(90),
                        MlogBuiltin("sharded"),
                        MlogVar("result2"),
                        MlogBoolLiteral(True),
                    ),
                ),
                Instruction(
                    InstructionType.SPAWN_BULLET,
                    None,
                    (),
                    (
                        MlogVar("result3"),
                        MlogBuiltin("nova"),
                        MlogNumberLiteral(1),
                        MlogBuiltin("thisx"),
                        MlogBuiltin("thisy"),
                        MlogNumberLiteral(359),
                        MlogBuiltin("crux"),
                        MlogNullLiteral(),
                        MlogNumberLiteral(150),
                        MlogNumberLiteral(1),
                        MlogNumberLiteral(1),
                        MlogNumberLiteral(-1),
                        MlogNumberLiteral(-1),
                    ),
                ),
                Instruction(
                    InstructionType.APPLY_STATUS,
                    ApplyStatusSuboperation.APPLY,
                    (),
                    (
                        MlogBuiltin("status-wet"),
                        MlogBuiltin("unit"),
                        MlogNumberLiteral(67),
                    ),
                ),
                Instruction(
                    InstructionType.WEATHER_SENSE,
                    None,
                    (),
                    (MlogVar("result4"), MlogBuiltin("rain")),
                ),
                Instruction(
                    InstructionType.WEATHER_SET,
                    None,
                    (),
                    (MlogBuiltin("snowing"), MlogBoolLiteral(True)),
                ),
                Instruction(
                    InstructionType.SPAWN_WAVE,
                    None,
                    (),
                    (
                        MlogNumberLiteral(67),
                        MlogNumberLiteral(42),
                        MlogBoolLiteral(False),
                    ),
                ),
                Instruction(
                    InstructionType.SET_RULE,
                    SetRuleSuboperation.CURRENT_WAVE_TIME,
                    (),
                    (MlogNumberLiteral(67),),
                ),
                Instruction(
                    InstructionType.SET_RULE,
                    SetRuleSuboperation.MAP_AREA,
                    (),
                    (
                        MlogNumberLiteral(67),
                        MlogNumberLiteral(42),
                        MlogVar("width"),
                        MlogVar("height"),
                    ),
                ),
                Instruction(
                    InstructionType.FLUSH_MESSAGE,
                    FlushMessageSuboperation.NOTIFY,
                    (),
                    (MlogBuiltin("wait"),),
                ),
                Instruction(
                    InstructionType.FLUSH_MESSAGE,
                    FlushMessageSuboperation.TOAST,
                    (),
                    (MlogNumberLiteral(6), MlogBuiltin("wait")),
                ),
                Instruction(
                    InstructionType.CUTSCENE, CutsceneSuboperation.STOP, (), ()
                ),
                Instruction(
                    InstructionType.EFFECT,
                    EffectSuboperation.SPARK_BIG,
                    (),
                    (
                        MlogVar("sparkX"),
                        MlogVar("sparkY"),
                        MlogColorLiteral("008888"),
                    ),
                ),
                Instruction(
                    InstructionType.EXPLOSION,
                    None,
                    (),
                    (
                        MlogBuiltin("crux"),
                        MlogNumberLiteral(50),
                        MlogNumberLiteral(50),
                        MlogVar("radius"),
                        MlogNumberLiteral(100),
                        MlogBoolLiteral(True),
                        MlogBoolLiteral(False),
                        MlogVar("isPierce"),
                        MlogVar("effect"),
                    ),
                ),
                Instruction(
                    InstructionType.FETCH,
                    FetchSuboperation.UNIT,
                    (),
                    (
                        MlogVar("result5"),
                        MlogBuiltin("malis"),
                        MlogVar("index"),
                        MlogNullLiteral(),
                    ),
                ),
                Instruction(InstructionType.SYNC, None, (), (MlogVar("var"),)),
                Instruction(
                    InstructionType.GET_FLAG,
                    None,
                    (),
                    (MlogVar("result6"), MlogStringLiteral("flag")),
                ),
                Instruction(
                    InstructionType.SET_FLAG,
                    None,
                    (),
                    (MlogStringLiteral("flag"), MlogBoolLiteral(True)),
                ),
                Instruction(
                    InstructionType.SET_PROPERTY,
                    None,
                    (),
                    (
                        MlogBuiltin("titanium"),
                        MlogVar("nucleus1"),
                        MlogNumberLiteral(9999),
                    ),
                ),
                Instruction(
                    InstructionType.PLAY_SOUND,
                    PlaySoundSuboperation.GLOBAL,
                    (),
                    (
                        MlogBuiltin("sfx-shoot"),
                        MlogNumberLiteral(1),
                        MlogNumberLiteral(1),
                        MlogNumberLiteral(0),
                        MlogBoolLiteral(True),
                    ),
                ),
                Instruction(
                    InstructionType.PLAY_MUSIC,
                    None,
                    (),
                    (MlogStringLiteral("game1"), MlogBoolLiteral(True)),
                ),
                Instruction(
                    InstructionType.SET_MARKER,
                    SetMarkerSuboperation.POS,
                    (),
                    (
                        MlogNumberLiteral(0),
                        MlogNumberLiteral(0),
                        MlogNumberLiteral(0),
                        MlogNumberLiteral(0),
                    ),
                ),
                Instruction(
                    InstructionType.MAKE_MARKER,
                    None,
                    (MakeMarkerSelectableParam.SHAPE,),
                    (
                        MlogNumberLiteral(0),
                        MlogNumberLiteral(0),
                        MlogNumberLiteral(0),
                        MlogBoolLiteral(True),
                    ),
                ),
                Instruction(
                    InstructionType.LOCALE_PRINT, None, (), (MlogStringLiteral("name"),)
                ),
            ],
            "\n".join(
                (
                    "query circle unit @sharded 67 42 5",
                    "setblock ore @air 6 7",
                    "getblock floor result1 0 0",
                    "spawn @dagger 42 67 90 @sharded result2 true",
                    "bullet result3 @nova 1 @thisx @thisy 359 @crux null 150 1 1 -1 -1",
                    "status false @status-wet @unit 67",
                    "weathersense result4 @rain",
                    "weatherset @snowing true",
                    "spawnwave 67 42 false",
                    "setrule currentWaveTime 67",
                    "setrule mapArea _ 67 42 width height",
                    "message notify _ @wait",
                    "message toast 6 @wait",
                    "cutscene stop",
                    "effect sparkBig sparkX sparkY _ %008888",
                    "explosion @crux 50 50 radius 100 true false isPierce effect",
                    "fetch unit result5 @malis index null",
                    "sync var",
                    'getflag result6 "flag"',
                    'setflag "flag" true',
                    "setprop @titanium nucleus1 9999",
                    "playsound false @sfx-shoot 1 1 0 _ _ true",
                    'playmusic "game1" true',
                    "setmarker pos 0 0 0 0",
                    "makemarker shape 0 0 0 true",
                    'localeprint "name"',
                )
            ),
            id="world-instructions",
        ),
    ],
)
def test_generate_mlog(script, expected):
    assert generate_mlog(script) == expected
