from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.codegen import generate_mlog
from py2mlog.mlog.selectable_params import *
from py2mlog.mlog.mlog_expressions import *
from py2mlog.mlog.suboperations import *


def test_io_instructions():
    script = [
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
            (MlogNumberLiteral(255), MlogNumberLiteral(255), MlogNumberLiteral(255)),
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
        Instruction(InstructionType.PRINT, None, (), (MlogStringLiteral("frog"),)),
        Instruction(InstructionType.PRINT_CHAR, None, (), (MlogNumberLiteral(65),)),
        Instruction(InstructionType.FORMAT, None, (), (MlogVar("frog2"),)),
    ]

    mlog = (
        "read result1 cell1 0",
        "write result2 cell2 1",
        "draw clear 255 255 255",
        "draw lineRect 10 20 40 50",
        'print "frog"',
        "printchar 65",
        "format frog2",
    )
    mlog = "\n".join(mlog)

    assert mlog == generate_mlog(script)


def test_block_control_instructions():
    script = [
        Instruction(InstructionType.DRAW_FLUSH, None, (), (MlogVar("display1"),)),
        Instruction(InstructionType.PRINT_FLUSH, None, (), (MlogVar("message1"),)),
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
    ]

    mlog = (
        "drawflush display1",
        "printflush message1",
        "getlink result 0",
        "control enabled block1 enabled",
        "radar enemy attacker flying maxHealth turret1 1 enemy",
        "sensor count block2 @copper",
    )
    mlog = "\n".join(mlog)

    assert mlog == generate_mlog(script)


# TODO: add tests for all instructions
