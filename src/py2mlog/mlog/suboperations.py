"""
Enums for suboperations. e.g.
In `op add result a b`, `add` is the suboperation.
In `ucontrol move 0 0`, `move` is the suboperation.
In `control enabled block1 0`, `enabled` is the suboperation.
"""

from enum import Enum

from .instruction_types import InstructionType


class Suboperation(Enum):
    pass


class DrawSuboperation(Suboperation):
    CLEAR = "clear"
    COLOR = "color"
    COL = "col"
    STROKE = "stroke"
    LINE = "line"
    RECT = "rect"
    LINE_RECT = "lineRect"
    POLY = "poly"
    LINE_POLY = "linePoly"
    TRIANGLE = "triangle"
    IMAGE = "image"
    PRINT = "print"
    TRANSLATE = "translate"
    SCALE = "scale"
    ROTATE = "rotate"
    RESET = "reset"


class ControlSuboperation(Suboperation):
    ENABLED = "enabled"
    SHOOT = "shoot"
    SHOOTP = "shootp"
    CONFIG = "config"
    COLOR = "color"


class OperationSuboperation(Suboperation):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    INTEGER_DIV = "idiv"
    MOD = "mod"
    TRUE_MOD = "emod"
    POW = "pow"

    EQUAL = "equal"
    NOT_EQUAL = "notEqual"
    LOGICAL_AND = "land"
    LESS_THAN = "lessThan"
    LESS_THAN_OR_EQ = "lessThanEq"
    GREATER_THAN = "greaterThan"
    GREATER_THAN_OR_EQ = "greaterThanEq"
    STRICT_EQUAL = "strictEqual"

    BITSHIFT_LEFT = "shl"
    BITSHIFT_RIGHT = "shr"
    UNSIGNED_BITSHIFT_RIGHT = "ushr"
    BITWISE_OR = "or"
    BITWISE_AND = "and"
    BITWISE_XOR = "xor"
    BITWISE_NOT = "not"

    MAX = "max"
    MIN = "min"
    ANGLE = "angle"
    ANGLE_DIFF = "angleDiff"
    LEN = "len"
    NOISE = "noise"
    ABS = "abs"
    SIGN = "sign"
    LOG = "log"
    LOGN = "logn"
    LOG10 = "log10"
    FLOOR = "floor"
    CEIL = "ceil"
    ROUND = "round"
    SQRT = "sqrt"
    RAND = "rand"
    SIN = "sin"
    COS = "cos"
    TAN = "tan"
    ASIN = "asin"
    ACOS = "acos"
    ATAN = "atan"


class ConditionOpSuboperation(Suboperation):
    EQUAL = "equal"
    NOT_EQUAL = "notEqual"
    LESS_THAN = "lessThan"
    LESS_THAN_OR_EQ = "lessThanEq"
    GREATER_THAN = "greaterThan"
    GREATER_THAN_OR_EQ = "greaterThanEq"
    STRICT_EQUAL = "strictEqual"
    ALWAYS = "always"


class UnitControlSuboperation(Suboperation):
    IDLE = "idle"
    STOP = "stop"
    MOVE = "move"
    APPROACH = "approach"
    PATHFIND = "pathfind"
    AUTO_PATHFIND = "autoPathfind"
    BOOST = "boost"
    TARGET = "target"
    TARGETP = "targetp"
    ITEM_DROP = "itemDrop"
    ITEM_TAKE = "itemTake"
    PAY_DROP = "payDrop"
    PAY_TAKE = "payTake"
    PAY_ENTER = "payEnter"
    MINE = "mine"
    FLAG = "flag"
    BUILD = "build"
    DECONSTRUCT = "deconstruct"
    GET_BLOCK = "getBlock"
    WITHIN = "within"
    UNBIND = "unbind"


class UnitLocateSuboperation(Suboperation):
    ORE = "ore"
    BUILDING = "building"
    SPAWN = "spawn"
    DAMAGED = "damaged"


class QuerySuboperation(Suboperation):
    CIRCLE = "circle"
    RECT = "rect"


class SetBlockSuboperation(Suboperation):
    FLOOR = "floor"
    ORE = "ore"
    BLOCK = "block"


class ApplyStatusSuboperation(Suboperation):
    APPLY = "false"
    CLEAR = "true"


class SetRuleSuboperation(Suboperation):
    CURRENT_WAVE_TIME = "currentWaveTime"
    WAVE_TIMER = "waveTimer"
    WAVES = "waves"
    WAVE = "wave"
    WAVE_SPACING = "waveSpacing"
    WAVE_SENDING = "waveSending"
    ATTACK_MODE = "attackMode"
    ENEMY_CORE_BUILD_RADIUS = "enemyCoreBuildRadius"
    DROP_ZONE_RADIUS = "dropZoneRadius"
    UNIT_CAP = "unitCap"

    MAP_AREA = "mapArea"

    LIGHTING = "lighting"
    CAN_GAME_OVER = "canGameOver"
    AMBIENT_LIGHT = "ambientLight"
    SOLAR_MULTIPLIER = "solarMultiplier"
    DRAG_MULTIPLIER = "dragMultiplier"
    BAN = "ban"
    UNBAN = "unban"
    PAUSE_DISABLED = "pauseDisabled"
    MUSIC_VOLUME = "musicVolume"

    BUILD_SPEED = "buildSpeed"
    UNIT_HEALTH = "unitHealth"
    UNIT_BUILD_SPEED = "unitBuildSpeed"
    UNIT_MINE_SPEED = "unitMineSpeed"
    UNIT_COST = "unitCost"
    UNIT_DAMAGE = "unitDamage"
    BLOCK_HEALTH = "blockHealth"
    BLOCK_DAMAGE = "blockDamage"
    RTS_MIN_WEIGHT = "rtsMinWeight"
    RTS_MIN_SQUAD = "rtsMinSquad"


class FlushMessageSuboperation(Suboperation):
    NOTIFY = "notify"
    ANNOUNCE = "announce"
    TOAST = "toast"
    MISSION = "mission"


class CutsceneSuboperation(Suboperation):
    ACTIVE = "active"
    PAN = "pan"
    ZOOM = "zoom"
    STOP = "stop"
    SHAKE = "shake"
    GET_HUD = "getHud"
    SET_HUD = "setHud"


class EffectSuboperation(Suboperation):
    WARN = "warn"
    CROSS = "cross"
    BLOCK_FALL = "blockFall"
    PLACE_BLOCK = "placeBlock"
    PLACE_BLOCK_SPARK = "placeBlockSpark"
    BREAK_BLOCK = "breakBlock"
    SPAWN = "spawn"
    TRAIL = "trail"
    BREAK_PROP = "breakProp"
    SMOKE_CLOUD = "smokeCloud"
    VAPOR = "vapor"
    HIT = "hit"
    HIT_SQUARE = "hitSquare"
    SHOOT_SMALL = "shootSmall"
    SHOOT_BIG = "shootBig"
    SMOKE_SMALL = "smokeSmall"
    SMOKE_BIG = "smokeBig"
    SMOKE_COLOR = "smokeColor"
    SMOKE_SQUARE = "smokeSquare"
    SMOKE_SQUARE_BIG = "smokeSquareBig"
    SPARK = "spark"
    SPARK_BIG = "sparkBig"
    SPARK_SHOOT = "sparkShoot"
    SPARK_SHOOT_BIG = "sparkShootBig"
    DRILL = "drill"
    DRILL_BIG = "drillBig"
    LIGHT_BLOCK = "lightBlock"
    EXPLOSION = "explosion"
    SMOKE_PUFF = "smokePuff"
    SPARK_EXPLOSION = "sparkExplosion"
    CROSS_EXPLOSION = "crossExplosion"
    WAVE = "wave"
    BUBBLE = "bubble"


class FetchSuboperation(Suboperation):
    UNIT = "unit"
    UNIT_COUNT = "unitCount"
    PLAYER = "player"
    PLAYER_COUNT = "playerCount"
    CORE = "core"
    CORE_COUNT = "coreCount"
    BUILD = "build"
    BUILD_COUNT = "buildCount"


class PlaySoundSuboperation(Suboperation):
    GLOBAL = "false"
    POSITIONAL = "true"


class SetMarkerSuboperation(Suboperation):
    REMOVE = "remove"
    WORLD = "world"
    MINIMAP = "minimap"
    AUTOSCALE = "autoscale"
    POS = "pos"
    END_POS = "endPos"
    DRAW_LAYER = "drawLayer"
    COLOR = "color"
    RADIUS = "radius"
    STROKE = "stroke"
    OUTLINE = "outline"
    ROTATION = "rotation"
    SHAPE = "shape"
    ARC = "arc"
    FLUSH_TEXT = "flushText"
    FONT_SIZE = "fontSize"
    TEXT_HEIGHT = "textHeight"
    TEXT_ALIGN = "textAlign"
    LINE_ALIGN = "lineAlign"
    LABEL_FLAGS = "labelFlags"
    TEXTURE = "texture"
    TEXTURE_SIZE = "textureSize"
    POSI = "posi"
    UVI = "uvi"
    COLORI = "colori"


suboperation_map: dict[InstructionType, type[Suboperation]] = {
    InstructionType.DRAW: DrawSuboperation,
    InstructionType.CONTROL: ControlSuboperation,
    InstructionType.OPERATION: OperationSuboperation,
    InstructionType.SELECT: ConditionOpSuboperation,
    InstructionType.JUMP: ConditionOpSuboperation,
    InstructionType.UNIT_CONTROL: UnitControlSuboperation,
    InstructionType.UNIT_LOCATE: UnitLocateSuboperation,
    InstructionType.QUERY: QuerySuboperation,
    InstructionType.SET_BLOCK: SetBlockSuboperation,
    InstructionType.APPLY_STATUS: ApplyStatusSuboperation,
    InstructionType.SET_RULE: SetRuleSuboperation,
    InstructionType.FLUSH_MESSAGE: FlushMessageSuboperation,
    InstructionType.CUTSCENE: CutsceneSuboperation,
    InstructionType.EFFECT: EffectSuboperation,
    InstructionType.FETCH: FetchSuboperation,
    InstructionType.PLAY_SOUND: PlaySoundSuboperation,
    InstructionType.SET_MARKER: SetMarkerSuboperation,
}
