from enum import Enum


class InstructionType(Enum):
    """An enum for all instruction types."""

    # I/O
    READ = "read"
    WRITE = "write"
    DRAW = "draw"
    PRINT = "print"
    PRINT_CHAR = "printchar"
    FORMAT = "format"

    # Block Control
    DRAW_FLUSH = "drawflush"
    PRINT_FLUSH = "printflush"
    GET_LINK = "getlink"
    CONTROL = "control"
    RADAR = "radar"
    SENSOR = "sensor"

    # Operations
    SET = "set"
    OPERATION = "op"
    SELECT = "select"
    LOOKUP = "lookup"
    PACK_COLOR = "packcolor"
    UNPACK_COLOR = "unpackcolor"

    # Flow Control
    WAIT = "wait"
    STOP = "stop"
    END = "end"
    JUMP = "jump"
    SET_RATE = "setrate"

    # Unit Control
    UNIT_BIND = "ubind"
    UNIT_CONTROL = "ucontrol"
    UNIT_RADAR = "uradar"
    UNIT_LOCATE = "ulocate"

    # World
    QUERY = "query"
    GET_BLOCK = "getblock"
    SET_BLOCK = "setblock"
    SPAWN_UNIT = "spawn"
    SPAWN_BULLET = "bullet"
    APPLY_STATUS = "status"
    WEATHER_SENSE = "weathersense"
    WEATHER_SET = "weatherset"
    SPAWN_WAVE = "spawnwave"
    SET_RULE = "setrule"
    FLUSH_MESSAGE = "message"
    CUTSCENE = "cutscene"
    EFFECT = "effect"
    EXPLOSION = "explosion"
    FETCH = "fetch"
    SYNC = "sync"
    # hidden instruction
    # CLIENT_DATA = "clientdata"
    GET_FLAG = "getflag"
    SET_FLAG = "setflag"
    SET_PROPERTY = "setprop"
    PLAY_SOUND = "playsound"
    PLAY_MUSIC = "playmusic"
    SET_MARKER = "setmarker"
    MAKE_MARKER = "makemarker"
    LOCALE_PRINT = "localeprint"

    # Misc
    NOOP = "noop"
