import pytest

from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.instruction import Instruction
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
                        MlogVar("this_is_a_filler_so_the_output_should_be_underscore"),
                        MlogVar("this_is_also_a_filler"),
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
                    (MlogVar("label"),),
                ),
            ],
            "\n".join(
                (
                    "wait 0",
                    "wait time",
                    "stop",
                    "end",
                    "jump 67 equal x @copper",
                    "jump label always",
                )
            ),
            id="flow-control-instructions",
        ),
    ],
)
def test_generate_mlog(script, expected):
    assert generate_mlog(script) == expected


# TODO: add tests for all instructions
