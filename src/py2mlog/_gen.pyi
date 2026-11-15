from abc import ABC
from collections.abc import Iterator
from typing import Any, Literal, overload

from py2mlog._types import ColorType, Content

class Item(Content): ...
class Liquid(Content): ...

class Block(Content):
    """
    Includes terrain blocks, not just building types.
    """

class UnitType(Content): ...

class Senseable(ABC):
    def __getitem__(self, i: Item | Liquid | str | Any) -> Any: ...
    exponential_reconstructor: int
    gamma: int
    plated_conduit: int
    payload_loader: int
    shockwave_tower: int
    armored_duct: int
    sei: int
    payload_conveyor: int
    battery: int
    unloader: int
    silicon_smelter: int
    unit_cargo_loader: int
    meltdown: int
    vela: int
    conduit: int
    logic_processor: int
    scrap_wall: int
    salvo: int
    force_projector: int
    small_deconstructor: int
    arkyid: int
    pyrolysis_generator: int
    reinforced_liquid_container: int
    wave: int
    phase_heater: int
    mech_fabricator: int
    dormant_cyst: int
    cryofluid: int
    reinforced_conduit: int
    mech_refabricator: int
    cleroi: int
    navanax: int
    conveyor: int
    tsunami: int
    phase_conduit: int
    dagger: int
    incite: int
    rotary_pump: int
    hydrogen: int
    tank_refabricator: int
    underflow_duct: int
    large_plasma_bore: int
    locus: int
    toxopid: int
    differential_generator: int
    retusa: int
    vent_condenser: int
    ship_fabricator: int
    laser_drill: int
    repair_point: int
    pulse_conduit: int
    titanium_wall_large: int
    reinforced_vault: int
    plastanium_wall_large: int
    pyratite_mixer: int
    tungsten_wall_large: int
    build_tower: int
    phase_synthesizer: int
    collaris: int
    segment: int
    basic_assembler_module: int
    swarmer: int
    plasma_bore: int
    silicon: int
    phase_wall: int
    constructor: int
    electrolyzer: int
    solar_panel: int
    lustre: int
    renale: int
    oil_extractor: int
    message: int
    impact_drill: int
    large_logic_display: int
    scathe_missile_surge: int
    alpha: int
    reinforced_surge_wall: int
    ship_refabricator: int
    thermal_generator: int
    deconstructor: int
    risso: int
    diffuse: int
    core_nucleus: int
    beam_tower: int
    mega: int
    incinerator: int
    overflow_gate: int
    naval_factory: int
    air_factory: int
    plastanium: int
    disassembler: int
    blast_compound: int
    titan: int
    surge_router: int
    silicon_arc_furnace: int
    tecta: int
    heat_redirector: int
    beam_node: int
    cryofluid_mixer: int
    titanium_wall: int
    minke: int
    logic_display: int
    mech_assembler: int
    obviate: int
    surge_conveyor: int
    copper: int
    chemical_combustion_chamber: int
    overdrive_dome: int
    ground_factory: int
    duct_unloader: int
    silicon_crucible: int
    combustion_generator: int
    cyanogen: int
    distributor: int
    flare: int
    pneumatic_drill: int
    lancer: int
    phase_wall_large: int
    breach: int
    melter: int
    scatter: int
    neoplasm: int
    beryllium_wall_large: int
    surge_tower: int
    disperse: int
    antumbra: int
    scepter: int
    switch: int
    battery_large: int
    tetrative_reconstructor: int
    horizon: int
    omura: int
    zenith: int
    bridge_conduit: int
    thorium_wall_large: int
    surge_crucible: int
    mechanical_pump: int
    container: int
    pulsar: int
    anthicus: int
    cyanogen_synthesizer: int
    core_citadel: int
    fuse: int
    shielded_wall: int
    thorium_reactor: int
    tungsten_wall: int
    aegires: int
    scrap_wall_gigantic: int
    turbine_condenser: int
    assembly_drone: int
    flux_reactor: int
    arc: int
    quasar: int
    core_acropolis: int
    slag: int
    ozone: int
    electric_heater: int
    ripple: int
    liquid_junction: int
    merui: int
    surge_smelter: int
    reinforced_pump: int
    duo: int
    quad: int
    coal: int
    scathe_missile_surge_split: int
    slag_incinerator: int
    spiroct: int
    liquid_container: int
    multiplicative_reconstructor: int
    carbide_wall_large: int
    blast_drill: int
    quell_missile: int
    tank_fabricator: int
    sublimate: int
    reinforced_container: int
    spectre: int
    vanquish: int
    door_large: int
    disrupt_missile: int
    scrap_wall_large: int
    mender: int
    repair_turret: int
    manifold: int
    plastanium_conveyor: int
    plastanium_compressor: int
    sorter: int
    carbide: int
    blast_mixer: int
    large_constructor: int
    tank_assembler: int
    micro_processor: int
    latum: int
    spore_pod: int
    large_canvas: int
    conquer: int
    duct: int
    multi_press: int
    junction: int
    plastanium_wall: int
    regen_projector: int
    foreshadow: int
    prime_refabricator: int
    solar_panel_large: int
    neoplasia_reactor: int
    core_foundation: int
    tile_logic_display: int
    carbide_crucible: int
    duct_router: int
    phase_fabric: int
    thorium: int
    block: int
    atmospheric_concentrator: int
    sand: int
    blast_door: int
    bridge_conveyor: int
    surge_alloy: int
    unit_cargo_unload_point: int
    overdrive_projector: int
    duct_bridge: int
    emanate: int
    avert: int
    smite: int
    separator: int
    additive_reconstructor: int
    bryde: int
    scathe_missile: int
    hyper_processor: int
    reinforced_bridge_conduit: int
    malign: int
    crawler: int
    reinforced_liquid_router: int
    anthicus_missile: int
    beam_link: int
    corvus: int
    quell: int
    mace: int
    mass_driver: int
    reinforced_payload_router: int
    scathe: int
    heat_router: int
    stell: int
    nova: int
    arkycite: int
    slag_heater: int
    scathe_missile_phase: int
    shock_mine: int
    ship_assembler: int
    unit_repair_tower: int
    elude: int
    atrax: int
    power_node_large: int
    tungsten: int
    metaglass: int
    coal_centrifuge: int
    memory_cell: int
    copper_wall_large: int
    large_cliff_crusher: int
    gallium: int
    beryllium_wall: int
    cyclone: int
    canvas: int
    poly: int
    pyratite: int
    thorium_wall: int
    router: int
    dummy: int
    oxide: int
    reign: int
    impulse_pump: int
    carbide_wall: int
    fissile_matter: int
    door: int
    cliff_crusher: int
    eclipse: int
    rtg_generator: int
    mechanical_drill: int
    beta: int
    phase_weaver: int
    liquid_tank: int
    graphite: int
    steam_generator: int
    surge_wall_large: int
    impact_reactor: int
    mend_projector: int
    armored_conveyor: int
    water: int
    copper_wall: int
    kiln: int
    graphite_press: int
    fortress: int
    cyerce: int
    power_node: int
    payload_unloader: int
    oil: int
    evoke: int
    diode: int
    pulverizer: int
    large_payload_mass_driver: int
    core_bastion: int
    reinforced_liquid_tank: int
    reinforced_payload_conveyor: int
    phase_conveyor: int
    reinforced_message: int
    cultivator: int
    disrupt: int
    inverted_sorter: int
    reinforced_liquid_junction: int
    scorch: int
    liquid_router: int
    mono: int
    titanium: int
    parallax: int
    small_heat_redirector: int
    vault: int
    reinforced_surge_wall_large: int
    scrap: int
    titanium_conveyor: int
    scrap_wall_huge: int
    oxynoe: int
    surge_wall: int
    nitrogen: int
    precept: int
    memory_bank: int
    payload_mass_driver: int
    spore_press: int
    water_extractor: int
    oxidation_chamber: int
    lead: int
    eruption_drill: int
    overflow_duct: int
    payload_router: int
    underflow_gate: int
    beryllium: int
    hail: int
    turret_unit_build_tower: int
    afflict: int
    oct: int
    # TODO: manually type these attributes or something
    dead: Any
    heat: Any
    memorycapacity: Any
    building: Any
    payloadcount: Any
    powernetstored: Any
    bulletlifetime: Any
    buildx: Any
    shootx: Any
    shooting: Any
    totalpayload: Any
    name: Any
    powernetout: Any
    totalpower: Any
    itemcapacity: Any
    timescale: Any
    pingtext: Any
    payloadcapacity: Any
    color: Any
    ammo: Any
    pingy: Any
    efficiency: Any
    powernetcapacity: Any
    config: Any
    miney: Any
    totalliquids: Any
    powernetin: Any
    range: Any
    selectedrotation: Any
    speed: Any
    ammocapacity: Any
    x: Any
    buffersize: Any
    powercapacity: Any
    rotation: Any
    shooty: Any
    type: Any
    size: Any
    liquidcapacity: Any
    controller: Any
    flag: Any
    displayheight: Any
    team: Any
    totalitems: Any
    buildy: Any
    solid: Any
    flying: Any
    pingx: Any
    velocityy: Any
    currentammotype: Any
    id: Any
    operations: Any
    boosting: Any
    mining: Any
    payloadtype: Any
    maxunits: Any
    maxhealth: Any
    velocityx: Any
    shield: Any
    armor: Any
    progress: Any
    y: Any
    minex: Any
    controlled: Any
    selectedblock: Any
    enabled: Any
    health: Any
    displaywidth: Any
    breaking: Any
    firstitem: Any
    bullettime: Any

class Controllable(ABC):
    def enabled(self, enabled: bool | int) -> None: ...
    def enable(self) -> None: ...
    def disable(self) -> None: ...
    def shoot(self, x: float, y: float, shoot: bool | int = True) -> None: ...
    def ceasefire(self) -> None: ...
    def shootp(self, unit: UnitObj, shoot: bool | int = True) -> None: ...
    def color(self, color: ColorType) -> None: ...
    def config(self, config: Any) -> None: ...

class Building(Senseable, Controllable): ...
class UnitObj(Senseable): ...

class Env:
    # Processor
    this: Building
    thisx: float
    thisy: float
    ipt: float

    # General
    pi: float
    e: float
    deg_to_rad: float
    rad_to_deg: float

    # Map
    time: float
    tick: float
    second: float
    minute: float
    wave_number: int
    wave_time: float
    mapw: float
    maph: float

    # Network/clientside (wproc only)
    # TODO: properly type these
    server: Any
    client: Any
    client_locale: Any
    client_unit: Any
    client_name: Any
    client_team: Any
    client_mobile: Any
    client_music_playing: Any
    client_current_music: Any

    # Lookup
    block_count: int
    unit_count: int
    item_count: int
    liquid_count: int

    # Misc
    counter: int
    unit: UnitObj

    # Special (manually defined)
    x: float
    y: float
    link_count: int
    null: None

    copper: Item
    lead: Item
    metaglass: Item
    graphite: Item
    sand: Item
    coal: Item
    titanium: Item
    thorium: Item
    scrap: Item
    silicon: Item
    plastanium: Item
    phase_fabric: Item
    surge_alloy: Item
    spore_pod: Item
    blast_compound: Item
    pyratite: Item
    beryllium: Item
    tungsten: Item
    oxide: Item
    carbide: Item
    fissile_matter: Item
    dormant_cyst: Item
    water: Liquid
    slag: Liquid
    oil: Liquid
    cryofluid: Liquid
    neoplasm: Liquid
    arkycite: Liquid
    gallium: Liquid
    ozone: Liquid
    hydrogen: Liquid
    nitrogen: Liquid
    cyanogen: Liquid
    air: Block
    spawn: Block
    remove_wall: Block
    remove_ore: Block
    cliff: Block
    build1: Block
    build2: Block
    build3: Block
    build4: Block
    build5: Block
    build6: Block
    build7: Block
    build8: Block
    build9: Block
    build10: Block
    build11: Block
    build12: Block
    build13: Block
    build14: Block
    build15: Block
    build16: Block
    deep_water: Block
    shallow_water: Block
    tainted_water: Block
    deep_tainted_water: Block
    darksand_tainted_water: Block
    sand_water: Block
    darksand_water: Block
    tar: Block
    pooled_cryofluid: Block
    molten_slag: Block
    space: Block
    empty: Block
    stone: Block
    crater_stone: Block
    char: Block
    basalt: Block
    hotrock: Block
    magmarock: Block
    sand_floor: Block
    darksand: Block
    dirt: Block
    mud: Block
    dacite: Block
    rhyolite: Block
    rhyolite_crater: Block
    rough_rhyolite: Block
    regolith: Block
    yellow_stone: Block
    carbon_stone: Block
    ferric_stone: Block
    ferric_craters: Block
    beryllic_stone: Block
    crystalline_stone: Block
    crystal_floor: Block
    yellow_stone_plates: Block
    red_stone: Block
    dense_red_stone: Block
    red_ice: Block
    arkycite_floor: Block
    arkyic_stone: Block
    rhyolite_vent: Block
    carbon_vent: Block
    arkyic_vent: Block
    yellow_stone_vent: Block
    red_stone_vent: Block
    crystalline_vent: Block
    stone_vent: Block
    basalt_vent: Block
    redmat: Block
    bluemat: Block
    grass: Block
    salt: Block
    snow: Block
    ice: Block
    ice_snow: Block
    shale: Block
    moss: Block
    core_zone: Block
    spore_moss: Block
    stone_wall: Block
    spore_wall: Block
    dirt_wall: Block
    dacite_wall: Block
    ice_wall: Block
    snow_wall: Block
    dune_wall: Block
    regolith_wall: Block
    yellow_stone_wall: Block
    rhyolite_wall: Block
    carbon_wall: Block
    ferric_stone_wall: Block
    beryllic_stone_wall: Block
    arkyic_wall: Block
    crystalline_stone_wall: Block
    red_ice_wall: Block
    red_stone_wall: Block
    red_diamond_wall: Block
    sand_wall: Block
    salt_wall: Block
    shrubs: Block
    shale_wall: Block
    spore_pine: Block
    snow_pine: Block
    pine: Block
    white_tree_dead: Block
    white_tree: Block
    spore_cluster: Block
    redweed: Block
    pur_bush: Block
    yellowcoral: Block
    boulder: Block
    snow_boulder: Block
    shale_boulder: Block
    sand_boulder: Block
    dacite_boulder: Block
    basalt_boulder: Block
    carbon_boulder: Block
    ferric_boulder: Block
    beryllic_boulder: Block
    yellow_stone_boulder: Block
    arkyic_boulder: Block
    crystal_cluster: Block
    vibrant_crystal_cluster: Block
    crystal_blocks: Block
    crystal_orbs: Block
    crystalline_boulder: Block
    red_ice_boulder: Block
    rhyolite_boulder: Block
    red_stone_boulder: Block
    metal_floor: Block
    metal_floor_damaged: Block
    metal_floor_2: Block
    metal_floor_3: Block
    metal_floor_4: Block
    metal_floor_5: Block
    dark_panel_1: Block
    dark_panel_2: Block
    dark_panel_3: Block
    dark_panel_4: Block
    dark_panel_5: Block
    dark_panel_6: Block
    dark_metal: Block
    metal_tiles_1: Block
    metal_tiles_2: Block
    metal_tiles_3: Block
    metal_tiles_4: Block
    metal_tiles_5: Block
    metal_tiles_6: Block
    metal_tiles_7: Block
    metal_tiles_8: Block
    metal_tiles_9: Block
    metal_tiles_10: Block
    metal_tiles_11: Block
    metal_tiles_12: Block
    metal_tiles_13: Block
    metal_wall_1: Block
    metal_wall_2: Block
    metal_wall_3: Block
    colored_floor: Block
    colored_wall: Block
    character_overlay: Block
    character_overlay_white: Block
    rune_overlay: Block
    rune_overlay_crux: Block
    pebbles: Block
    tendrils: Block
    ore_copper: Block
    ore_lead: Block
    ore_scrap: Block
    ore_coal: Block
    ore_titanium: Block
    ore_thorium: Block
    ore_beryllium: Block
    ore_tungsten: Block
    ore_crystal_thorium: Block
    ore_wall_thorium: Block
    ore_wall_beryllium: Block
    graphitic_wall: Block
    ore_wall_graphite: Block
    ore_wall_tungsten: Block
    graphite_press: Block
    multi_press: Block
    silicon_smelter: Block
    silicon_crucible: Block
    kiln: Block
    plastanium_compressor: Block
    phase_weaver: Block
    surge_smelter: Block
    cryofluid_mixer: Block
    pyratite_mixer: Block
    blast_mixer: Block
    melter: Block
    separator: Block
    disassembler: Block
    spore_press: Block
    pulverizer: Block
    coal_centrifuge: Block
    incinerator: Block
    silicon_arc_furnace: Block
    electrolyzer: Block
    atmospheric_concentrator: Block
    oxidation_chamber: Block
    electric_heater: Block
    slag_heater: Block
    phase_heater: Block
    heat_redirector: Block
    small_heat_redirector: Block
    heat_router: Block
    slag_incinerator: Block
    carbide_crucible: Block
    slag_centrifuge: Block
    surge_crucible: Block
    cyanogen_synthesizer: Block
    phase_synthesizer: Block
    heat_reactor: Block
    copper_wall: Block
    copper_wall_large: Block
    titanium_wall: Block
    titanium_wall_large: Block
    plastanium_wall: Block
    plastanium_wall_large: Block
    thorium_wall: Block
    thorium_wall_large: Block
    phase_wall: Block
    phase_wall_large: Block
    surge_wall: Block
    surge_wall_large: Block
    door: Block
    door_large: Block
    scrap_wall: Block
    scrap_wall_large: Block
    scrap_wall_huge: Block
    scrap_wall_gigantic: Block
    thruster: Block
    beryllium_wall: Block
    beryllium_wall_large: Block
    tungsten_wall: Block
    tungsten_wall_large: Block
    blast_door: Block
    reinforced_surge_wall: Block
    reinforced_surge_wall_large: Block
    carbide_wall: Block
    carbide_wall_large: Block
    shielded_wall: Block
    mender: Block
    mend_projector: Block
    overdrive_projector: Block
    overdrive_dome: Block
    force_projector: Block
    shock_mine: Block
    radar: Block
    build_tower: Block
    regen_projector: Block
    shockwave_tower: Block
    shield_projector: Block
    large_shield_projector: Block
    conveyor: Block
    titanium_conveyor: Block
    plastanium_conveyor: Block
    armored_conveyor: Block
    junction: Block
    bridge_conveyor: Block
    phase_conveyor: Block
    sorter: Block
    inverted_sorter: Block
    router: Block
    distributor: Block
    overflow_gate: Block
    underflow_gate: Block
    unloader: Block
    mass_driver: Block
    duct: Block
    armored_duct: Block
    duct_router: Block
    overflow_duct: Block
    underflow_duct: Block
    duct_bridge: Block
    duct_unloader: Block
    surge_conveyor: Block
    surge_router: Block
    unit_cargo_loader: Block
    unit_cargo_unload_point: Block
    mechanical_pump: Block
    rotary_pump: Block
    impulse_pump: Block
    conduit: Block
    pulse_conduit: Block
    plated_conduit: Block
    liquid_router: Block
    liquid_container: Block
    liquid_tank: Block
    liquid_junction: Block
    bridge_conduit: Block
    phase_conduit: Block
    reinforced_pump: Block
    reinforced_conduit: Block
    reinforced_liquid_junction: Block
    reinforced_bridge_conduit: Block
    reinforced_liquid_router: Block
    reinforced_liquid_container: Block
    reinforced_liquid_tank: Block
    power_node: Block
    power_node_large: Block
    surge_tower: Block
    diode: Block
    battery: Block
    battery_large: Block
    combustion_generator: Block
    thermal_generator: Block
    steam_generator: Block
    differential_generator: Block
    rtg_generator: Block
    solar_panel: Block
    solar_panel_large: Block
    thorium_reactor: Block
    impact_reactor: Block
    beam_node: Block
    beam_tower: Block
    beam_link: Block
    turbine_condenser: Block
    chemical_combustion_chamber: Block
    pyrolysis_generator: Block
    flux_reactor: Block
    neoplasia_reactor: Block
    mechanical_drill: Block
    pneumatic_drill: Block
    laser_drill: Block
    blast_drill: Block
    water_extractor: Block
    cultivator: Block
    oil_extractor: Block
    vent_condenser: Block
    cliff_crusher: Block
    large_cliff_crusher: Block
    plasma_bore: Block
    large_plasma_bore: Block
    impact_drill: Block
    eruption_drill: Block
    core_shard: Block
    core_foundation: Block
    core_nucleus: Block
    core_bastion: Block
    core_citadel: Block
    core_acropolis: Block
    container: Block
    vault: Block
    reinforced_container: Block
    reinforced_vault: Block
    duo: Block
    scatter: Block
    scorch: Block
    hail: Block
    wave: Block
    lancer: Block
    arc: Block
    parallax: Block
    swarmer: Block
    salvo: Block
    segment: Block
    tsunami: Block
    fuse: Block
    ripple: Block
    cyclone: Block
    foreshadow: Block
    spectre: Block
    meltdown: Block
    breach: Block
    diffuse: Block
    sublimate: Block
    titan: Block
    disperse: Block
    afflict: Block
    lustre: Block
    scathe: Block
    smite: Block
    malign: Block
    ground_factory: Block
    air_factory: Block
    naval_factory: Block
    additive_reconstructor: Block
    multiplicative_reconstructor: Block
    exponential_reconstructor: Block
    tetrative_reconstructor: Block
    repair_point: Block
    repair_turret: Block
    tank_fabricator: Block
    ship_fabricator: Block
    mech_fabricator: Block
    tank_refabricator: Block
    ship_refabricator: Block
    mech_refabricator: Block
    prime_refabricator: Block
    tank_assembler: Block
    ship_assembler: Block
    mech_assembler: Block
    basic_assembler_module: Block
    unit_repair_tower: Block
    payload_conveyor: Block
    payload_router: Block
    reinforced_payload_conveyor: Block
    reinforced_payload_router: Block
    payload_mass_driver: Block
    large_payload_mass_driver: Block
    small_deconstructor: Block
    deconstructor: Block
    constructor: Block
    large_constructor: Block
    payload_loader: Block
    payload_unloader: Block
    power_source: Block
    power_void: Block
    item_source: Block
    item_void: Block
    liquid_source: Block
    liquid_void: Block
    payload_source: Block
    payload_void: Block
    heat_source: Block
    target_dummy: Block
    illuminator: Block
    legacy_mech_pad: Block
    legacy_unit_factory: Block
    legacy_unit_factory_air: Block
    legacy_unit_factory_ground: Block
    command_center: Block
    launch_pad: Block
    advanced_launch_pad: Block
    landing_pad: Block
    interplanetary_accelerator: Block
    message: Block
    switch: Block
    micro_processor: Block
    logic_processor: Block
    hyper_processor: Block
    memory_cell: Block
    memory_bank: Block
    logic_display: Block
    large_logic_display: Block
    tile_logic_display: Block
    canvas: Block
    large_canvas: Block
    reinforced_message: Block
    world_processor: Block
    world_cell: Block
    world_message: Block
    world_switch: Block

    @staticmethod
    def links() -> Iterator[Building]:
        """
        Only available as iterable target in for loops.
        """

class Units:
    dagger: UnitObj
    mace: UnitObj
    fortress: UnitObj
    scepter: UnitObj
    reign: UnitObj
    nova: UnitObj
    pulsar: UnitObj
    quasar: UnitObj
    vela: UnitObj
    corvus: UnitObj
    crawler: UnitObj
    atrax: UnitObj
    spiroct: UnitObj
    arkyid: UnitObj
    toxopid: UnitObj
    flare: UnitObj
    horizon: UnitObj
    zenith: UnitObj
    antumbra: UnitObj
    eclipse: UnitObj
    mono: UnitObj
    poly: UnitObj
    mega: UnitObj
    quad: UnitObj
    oct: UnitObj
    risso: UnitObj
    minke: UnitObj
    bryde: UnitObj
    sei: UnitObj
    omura: UnitObj
    retusa: UnitObj
    oxynoe: UnitObj
    cyerce: UnitObj
    aegires: UnitObj
    navanax: UnitObj
    alpha: UnitObj
    beta: UnitObj
    gamma: UnitObj
    stell: UnitObj
    locus: UnitObj
    precept: UnitObj
    vanquish: UnitObj
    conquer: UnitObj
    merui: UnitObj
    cleroi: UnitObj
    anthicus: UnitObj
    anthicus_missile: UnitObj
    tecta: UnitObj
    collaris: UnitObj
    elude: UnitObj
    avert: UnitObj
    obviate: UnitObj
    quell: UnitObj
    quell_missile: UnitObj
    disrupt: UnitObj
    disrupt_missile: UnitObj
    renale: UnitObj
    latum: UnitObj
    evoke: UnitObj
    incite: UnitObj
    emanate: UnitObj
    block: UnitObj
    manifold: UnitObj
    assembly_drone: UnitObj
    dummy: UnitObj
    scathe_missile: UnitObj
    scathe_missile_phase: UnitObj
    scathe_missile_surge: UnitObj
    scathe_missile_surge_split: UnitObj
    turret_unit_build_tower: UnitObj

def print(
    *args: Any,
    sep: str = " ",
    end: str = r"\n",
    flush: Any = ...,
) -> None:
    """
    Param 'flush' defaults to 'message1'. Set 'flush' to False to omit 'printflush'.
    """

def ord(character: str, /) -> float: ...
def min(arg1: float, arg2: float) -> float: ...
def Color(x: float | ColorType | str, /) -> ColorType: ...
def sleep(t: float, /) -> None: ...
def wait(t: float, /) -> None: ...
def flip(x: float, /) -> float: ...
def abs(x: float, /) -> float: ...
def sign(x: float, /) -> float: ...
def log(x: float, /) -> float: ...
def log10(x: float, /) -> float: ...
def floor(x: float, /) -> float: ...
def ceil(x: float, /) -> float: ...
def round(x: float, /) -> float: ...
def sqrt(x: float, /) -> float: ...
def rand(x: float, /) -> float: ...
def sin(x: float, /) -> float: ...
def cos(x: float, /) -> float: ...
def tan(x: float, /) -> float: ...
def asin(x: float, /) -> float: ...
def acos(x: float, /) -> float: ...
def atan(x: float, /) -> float: ...

class Unit:
    @overload
    @staticmethod
    # Any here for var name as subop name (e.g. subop=ore instead of subop="ore")
    def locate(subop: Literal["ore"] | Any, /, *, ore_type: Item) -> None: ...
    @overload
    @staticmethod
    def locate(
        subop: Literal["building"] | Any,
        /,
        *,
        block_flag: str | Any,
        is_enemy_building: bool | int | str,
    ) -> None: ...
    @overload
    @staticmethod
    def locate(subop: Literal["spawn", "damaged"] | Any, /) -> None: ...
    @staticmethod
    def bind(type: str | UnitType, /) -> None: ...
    @overload
    @staticmethod
    def shoot() -> None: ...
    @overload
    @staticmethod
    def shoot(x: float, y: float) -> None: ...
    @staticmethod
    def targetp(unit: Unit, shoot: bool | int) -> None: ...

    targetUnit = targetp
    target_unit = targetp
    targetunit = targetp

    @staticmethod
    def itemdrop(to: Building, amount: float) -> None: ...
    @staticmethod
    def item_drop(to: Building, amount: float) -> None: ...
    @staticmethod
    def itemDrop(to: Building, amount: float) -> None: ...

    store = item_drop

    @staticmethod
    def itemTake(from_: Building, item: Item, amount: float) -> None: ...
    @staticmethod
    def itemtake(from_: Building, item: Item, amount: float) -> None: ...
    @staticmethod
    def item_take(from_: Building, item: Item, amount: float) -> None: ...

    fetch = item_take

    @staticmethod
    def build(
        x: float,
        y: float,
        block: Block,
        rotation: float = 0,
        config: Any = None,
    ) -> None: ...
    @staticmethod
    def radar(
        filter1: str | Any = "any",
        filter2: str | Any = "any",
        filter3: str | Any = "any",
        /,
        *,
        order: bool | float | str = True,
        key: str = "distance",
    ) -> Any: ...
    @staticmethod
    def idle() -> None: ...
    @staticmethod
    def stop() -> None: ...
    @staticmethod
    def move(x: float, y: float) -> None: ...
    @staticmethod
    def approach(x: float, y: float, radius: float) -> None: ...
    @staticmethod
    def pathfind(x: float, y: float) -> None: ...
    @staticmethod
    def autopathfind() -> None: ...
    @staticmethod
    def autoPathfind() -> None: ...
    @staticmethod
    def auto_pathfind() -> None: ...
    @staticmethod
    def boost(enabled: bool | float) -> None: ...
    @staticmethod
    def target(x: float, y: float, shoot: bool | float) -> None: ...
    @staticmethod
    def ceasefire() -> None: ...
    @staticmethod
    def payDrop() -> None: ...
    @staticmethod
    def pay_drop() -> None: ...
    @staticmethod
    def paydrop() -> None: ...
    @staticmethod
    def drop() -> None: ...
    @staticmethod
    def payTake(take_units: bool | float) -> None: ...
    @staticmethod
    def paytake(take_units: bool | float) -> None: ...
    @staticmethod
    def pay_take(take_units: bool | float) -> None: ...
    @staticmethod
    def lift() -> None: ...
    @staticmethod
    def carry() -> None: ...
    @staticmethod
    def payEnter() -> None: ...
    @staticmethod
    def pay_enter() -> None: ...
    @staticmethod
    def payenter() -> None: ...
    @staticmethod
    def mine(x: float, y: float) -> None: ...
    @staticmethod
    def flag(value: float, /) -> None: ...
    @staticmethod
    def deconstruct(x: float, y: float) -> None: ...
    @staticmethod
    def getblock(x: float, y: float) -> Any: ...
    @staticmethod
    def get_block(x: float, y: float) -> Any: ...
    @staticmethod
    def getBlock(x: float, y: float) -> Any: ...
    @staticmethod
    def within(x: float, y: float, radius: float) -> Any: ...
    @staticmethod
    def unbind() -> None: ...

class Alignment: ...

class Align:
    topLeft: Alignment
    top_left: Alignment
    topleft: Alignment
    right: Alignment
    topRight: Alignment
    top_right: Alignment
    topright: Alignment
    bottomRight: Alignment
    bottom_right: Alignment
    bottomright: Alignment
    left: Alignment
    top: Alignment
    bottom: Alignment
    bottomLeft: Alignment
    bottom_left: Alignment
    bottomleft: Alignment
    center: Alignment

class Screen:
    @staticmethod
    def flush(target: Building) -> None: ...
    @staticmethod
    def print(x: float, y: float, alignment: Alignment) -> None: ...
    @staticmethod
    def clear(r: float | Any, g: float | Any, b: float | Any) -> None: ...
    @staticmethod
    def fill(r: float | Any, g: float | Any, b: float | Any) -> None: ...
    @staticmethod
    def color(
        r: float | Any, g: float | Any, b: float | Any, a: float | Any = 255
    ) -> None: ...
    @staticmethod
    def col(color: ColorType, /) -> None: ...
    @staticmethod
    def stroke(width: float) -> None: ...
    @staticmethod
    def line(x1: float, y1: float, x2: float, y2: float) -> None: ...
    @staticmethod
    def rect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def fill_rect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def fillRect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def fillrect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def linerect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def lineRect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def line_rect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def hollowRect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def hollow_rect(
        x: float, y: float, width: float, height: float
    ) -> None: ...
    @staticmethod
    def hollowrect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def fill_poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def fillPoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def fillpoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def linepoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def line_poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def linePoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def hollow_poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def hollowpoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def hollowPoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def triangle(
        x1: float, y1: float, x2: float, y2: float, x3: float, y3: float
    ) -> None: ...
    @staticmethod
    def image(
        x: float, y: float, image: Content, size: float, rotation: float
    ) -> None: ...
    @staticmethod
    def translate(x: float, y: float) -> None: ...
    @staticmethod
    def scale(x: float, y: float) -> None: ...
    @staticmethod
    def rotate(degrees: float) -> None: ...
    @staticmethod
    def reset() -> None: ...

class Control:
    # something something DRY
    @staticmethod
    def enabled(building: Building, enabled: bool | int) -> None: ...
    @staticmethod
    def enable(building: Building) -> None: ...
    @staticmethod
    def disable(building: Building) -> None: ...
    @staticmethod
    def shoot(
        building: Building, x: float, y: float, shoot: bool | int = True
    ) -> None: ...
    @staticmethod
    def ceasefire(building: Building) -> None: ...
    @staticmethod
    def shootp(
        building: Building, unit: UnitObj, shoot: bool | int = True
    ) -> None: ...
    @staticmethod
    def color(building: Building, color: ColorType) -> None: ...
    @staticmethod
    def config(building: Building, config: Any) -> None: ...

class _Links:
    def __getitem__(self, index: int) -> Building: ...

Links: _Links
Link: _Links

class MemBuilding(Building):
    # in compiler.py, Mem.foo[etc] gets its own branch
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        index: int,
    ) -> Any: ...
    def __setitem__(self, index: int, value: Any) -> None: ...

class _Mem:
    def __getattr__(self, name: str) -> MemBuilding: ...

    # can't really generate MemBuilding
    @staticmethod
    def read(cell: MemBuilding | str, index: int) -> Any: ...
    @staticmethod
    def write(value: int, cell: MemBuilding, index: int) -> Any: ...

# so that the __getattr__ actually works
# you can still access staticmethods from an instance
Mem: _Mem
