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
    additive_reconstructor: int
    aegires: int
    afflict: int
    air_factory: int
    alpha: int
    anthicus: int
    anthicus_missile: int
    antumbra: int
    arc: int
    arkycite: int
    arkyid: int
    armored_conveyor: int
    armored_duct: int
    assembly_drone: int
    atmospheric_concentrator: int
    atrax: int
    avert: int
    basic_assembler_module: int
    battery: int
    battery_large: int
    beam_link: int
    beam_node: int
    beam_tower: int
    beryllium: int
    beryllium_wall: int
    beryllium_wall_large: int
    beta: int
    blast_compound: int
    blast_door: int
    blast_drill: int
    blast_mixer: int
    block: int
    breach: int
    bridge_conduit: int
    bridge_conveyor: int
    bryde: int
    build_tower: int
    canvas: int
    carbide: int
    carbide_crucible: int
    carbide_wall: int
    carbide_wall_large: int
    chemical_combustion_chamber: int
    cleroi: int
    cliff_crusher: int
    coal: int
    coal_centrifuge: int
    collaris: int
    combustion_generator: int
    conduit: int
    conquer: int
    constructor: int
    container: int
    conveyor: int
    copper: int
    copper_wall: int
    copper_wall_large: int
    core_acropolis: int
    core_bastion: int
    core_citadel: int
    core_foundation: int
    core_nucleus: int
    corvus: int
    crawler: int
    cryofluid: int
    cryofluid_mixer: int
    cultivator: int
    cyanogen: int
    cyanogen_synthesizer: int
    cyclone: int
    cyerce: int
    dagger: int
    deconstructor: int
    differential_generator: int
    diffuse: int
    diode: int
    disassembler: int
    disperse: int
    disrupt: int
    disrupt_missile: int
    distributor: int
    door: int
    door_large: int
    dormant_cyst: int
    duct: int
    duct_bridge: int
    duct_router: int
    duct_unloader: int
    dummy: int
    duo: int
    eclipse: int
    electric_heater: int
    electrolyzer: int
    elude: int
    emanate: int
    eruption_drill: int
    evoke: int
    exponential_reconstructor: int
    fissile_matter: int
    flare: int
    flux_reactor: int
    force_projector: int
    foreshadow: int
    fortress: int
    fuse: int
    gallium: int
    gamma: int
    graphite: int
    graphite_press: int
    ground_factory: int
    hail: int
    heat_redirector: int
    heat_router: int
    horizon: int
    hydrogen: int
    hyper_processor: int
    impact_drill: int
    impact_reactor: int
    impulse_pump: int
    incinerator: int
    incite: int
    inverted_sorter: int
    junction: int
    kiln: int
    lancer: int
    large_canvas: int
    large_cliff_crusher: int
    large_constructor: int
    large_logic_display: int
    large_payload_mass_driver: int
    large_plasma_bore: int
    laser_drill: int
    latum: int
    lead: int
    liquid_container: int
    liquid_junction: int
    liquid_router: int
    liquid_tank: int
    locus: int
    logic_display: int
    logic_processor: int
    lustre: int
    mace: int
    malign: int
    manifold: int
    mass_driver: int
    mech_assembler: int
    mech_fabricator: int
    mech_refabricator: int
    mechanical_drill: int
    mechanical_pump: int
    mega: int
    meltdown: int
    melter: int
    memory_bank: int
    memory_cell: int
    mend_projector: int
    mender: int
    merui: int
    message: int
    metaglass: int
    micro_processor: int
    minke: int
    mono: int
    multi_press: int
    multiplicative_reconstructor: int
    naval_factory: int
    navanax: int
    neoplasia_reactor: int
    neoplasm: int
    nitrogen: int
    nova: int
    obviate: int
    oct: int
    oil: int
    oil_extractor: int
    omura: int
    overdrive_dome: int
    overdrive_projector: int
    overflow_duct: int
    overflow_gate: int
    oxidation_chamber: int
    oxide: int
    oxynoe: int
    ozone: int
    parallax: int
    payload_conveyor: int
    payload_loader: int
    payload_mass_driver: int
    payload_router: int
    payload_unloader: int
    phase_conduit: int
    phase_conveyor: int
    phase_fabric: int
    phase_heater: int
    phase_synthesizer: int
    phase_wall: int
    phase_wall_large: int
    phase_weaver: int
    plasma_bore: int
    plastanium: int
    plastanium_compressor: int
    plastanium_conveyor: int
    plastanium_wall: int
    plastanium_wall_large: int
    plated_conduit: int
    pneumatic_drill: int
    poly: int
    power_node: int
    power_node_large: int
    precept: int
    prime_refabricator: int
    pulsar: int
    pulse_conduit: int
    pulverizer: int
    pyratite: int
    pyratite_mixer: int
    pyrolysis_generator: int
    quad: int
    quasar: int
    quell: int
    quell_missile: int
    regen_projector: int
    reign: int
    reinforced_bridge_conduit: int
    reinforced_conduit: int
    reinforced_container: int
    reinforced_liquid_container: int
    reinforced_liquid_junction: int
    reinforced_liquid_router: int
    reinforced_liquid_tank: int
    reinforced_message: int
    reinforced_payload_conveyor: int
    reinforced_payload_router: int
    reinforced_pump: int
    reinforced_surge_wall: int
    reinforced_surge_wall_large: int
    reinforced_vault: int
    renale: int
    repair_point: int
    repair_turret: int
    retusa: int
    ripple: int
    risso: int
    rotary_pump: int
    router: int
    rtg_generator: int
    salvo: int
    sand: int
    scathe: int
    scathe_missile: int
    scathe_missile_phase: int
    scathe_missile_surge: int
    scathe_missile_surge_split: int
    scatter: int
    scepter: int
    scorch: int
    scrap: int
    scrap_wall: int
    scrap_wall_gigantic: int
    scrap_wall_huge: int
    scrap_wall_large: int
    segment: int
    sei: int
    separator: int
    shielded_wall: int
    ship_assembler: int
    ship_fabricator: int
    ship_refabricator: int
    shock_mine: int
    shockwave_tower: int
    silicon: int
    silicon_arc_furnace: int
    silicon_crucible: int
    silicon_smelter: int
    slag: int
    slag_heater: int
    slag_incinerator: int
    small_deconstructor: int
    small_heat_redirector: int
    smite: int
    solar_panel: int
    solar_panel_large: int
    sorter: int
    spectre: int
    spiroct: int
    spore_pod: int
    spore_press: int
    steam_generator: int
    stell: int
    sublimate: int
    surge_alloy: int
    surge_conveyor: int
    surge_crucible: int
    surge_router: int
    surge_smelter: int
    surge_tower: int
    surge_wall: int
    surge_wall_large: int
    swarmer: int
    switch: int
    tank_assembler: int
    tank_fabricator: int
    tank_refabricator: int
    tecta: int
    tetrative_reconstructor: int
    thermal_generator: int
    thorium: int
    thorium_reactor: int
    thorium_wall: int
    thorium_wall_large: int
    tile_logic_display: int
    titan: int
    titanium: int
    titanium_conveyor: int
    titanium_wall: int
    titanium_wall_large: int
    toxopid: int
    tsunami: int
    tungsten: int
    tungsten_wall: int
    tungsten_wall_large: int
    turbine_condenser: int
    turret_unit_build_tower: int
    underflow_duct: int
    underflow_gate: int
    unit_cargo_loader: int
    unit_cargo_unload_point: int
    unit_repair_tower: int
    unloader: int
    vanquish: int
    vault: int
    vela: int
    vent_condenser: int
    water: int
    water_extractor: int
    wave: int
    zenith: int
    # TODO: manually type these attributes or something
    ammo: Any
    ammocapacity: Any
    armor: Any
    boosting: Any
    breaking: Any
    buffersize: Any
    building: Any
    buildx: Any
    buildy: Any
    bulletlifetime: Any
    bullettime: Any
    color: Any
    config: Any
    controlled: Any
    controller: Any
    currentammotype: Any
    dead: Any
    displayheight: Any
    displaywidth: Any
    efficiency: Any
    enabled: Any
    firstitem: Any
    flag: Any
    flying: Any
    health: Any
    heat: Any
    id: Any
    itemcapacity: Any
    liquidcapacity: Any
    maxhealth: Any
    maxunits: Any
    memorycapacity: Any
    minex: Any
    miney: Any
    mining: Any
    name: Any
    operations: Any
    payloadcapacity: Any
    payloadcount: Any
    payloadtype: Any
    pingtext: Any
    pingx: Any
    pingy: Any
    powercapacity: Any
    powernetcapacity: Any
    powernetin: Any
    powernetout: Any
    powernetstored: Any
    progress: Any
    range: Any
    rotation: Any
    selectedblock: Any
    selectedrotation: Any
    shield: Any
    shooting: Any
    shootx: Any
    shooty: Any
    size: Any
    solid: Any
    speed: Any
    team: Any
    timescale: Any
    totalitems: Any
    totalliquids: Any
    totalpayload: Any
    totalpower: Any
    type: Any
    velocityx: Any
    velocityy: Any
    x: Any
    y: Any

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

class Colors:
    accent: ColorType
    Accent: ColorType
    ACCENT: ColorType
    acid: ColorType
    Acid: ColorType
    ACID: ColorType
    black: ColorType
    Black: ColorType
    BLACK: ColorType
    blue: ColorType
    Blue: ColorType
    BLUE: ColorType
    brick: ColorType
    Brick: ColorType
    BRICK: ColorType
    brown: ColorType
    Brown: ColorType
    BROWN: ColorType
    clear: ColorType
    Clear: ColorType
    CLEAR: ColorType
    coral: ColorType
    Coral: ColorType
    CORAL: ColorType
    crimson: ColorType
    Crimson: ColorType
    CRIMSON: ColorType
    cyan: ColorType
    Cyan: ColorType
    CYAN: ColorType
    darkgray: ColorType
    Darkgray: ColorType
    DARKGRAY: ColorType
    darkgrey: ColorType
    Darkgrey: ColorType
    DARKGREY: ColorType
    forest: ColorType
    Forest: ColorType
    FOREST: ColorType
    gold: ColorType
    Gold: ColorType
    GOLD: ColorType
    goldenrod: ColorType
    Goldenrod: ColorType
    GOLDENROD: ColorType
    gray: ColorType
    Gray: ColorType
    GRAY: ColorType
    green: ColorType
    Green: ColorType
    GREEN: ColorType
    grey: ColorType
    Grey: ColorType
    GREY: ColorType
    highlight: ColorType
    Highlight: ColorType
    HIGHLIGHT: ColorType
    lightgray: ColorType
    Lightgray: ColorType
    LIGHTGRAY: ColorType
    lightgrey: ColorType
    Lightgrey: ColorType
    LIGHTGREY: ColorType
    lime: ColorType
    Lime: ColorType
    LIME: ColorType
    magenta: ColorType
    Magenta: ColorType
    MAGENTA: ColorType
    maroon: ColorType
    Maroon: ColorType
    MAROON: ColorType
    navy: ColorType
    Navy: ColorType
    NAVY: ColorType
    negstat: ColorType
    Negstat: ColorType
    NEGSTAT: ColorType
    olive: ColorType
    Olive: ColorType
    OLIVE: ColorType
    orange: ColorType
    Orange: ColorType
    ORANGE: ColorType
    pink: ColorType
    Pink: ColorType
    PINK: ColorType
    purple: ColorType
    Purple: ColorType
    PURPLE: ColorType
    red: ColorType
    Red: ColorType
    RED: ColorType
    royal: ColorType
    Royal: ColorType
    ROYAL: ColorType
    salmon: ColorType
    Salmon: ColorType
    SALMON: ColorType
    scarlet: ColorType
    Scarlet: ColorType
    SCARLET: ColorType
    sky: ColorType
    Sky: ColorType
    SKY: ColorType
    slate: ColorType
    Slate: ColorType
    SLATE: ColorType
    stat: ColorType
    Stat: ColorType
    STAT: ColorType
    tan: ColorType
    Tan: ColorType
    TAN: ColorType
    teal: ColorType
    Teal: ColorType
    TEAL: ColorType
    unlaunched: ColorType
    Unlaunched: ColorType
    UNLAUNCHED: ColorType
    violet: ColorType
    Violet: ColorType
    VIOLET: ColorType
    white: ColorType
    White: ColorType
    WHITE: ColorType
    yellow: ColorType
    Yellow: ColorType
    YELLOW: ColorType

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
def vec_angle(x: float, y: float, /) -> float:
    """
    Similar to atan2.
    Note that this function takes (x, y) and not (y, x).
    Returns 0 to 360 **degrees**.
    """

def vec_len(a: float, b: float, /) -> float: ...
def logn(x: float, base: float) -> float: ...
def mod(a: float, b: float, /) -> float: ...
def ushr(a: float, b: float, /) -> float: ...
def angle_diff(a: float, b: float, /) -> float: ...
def noise(a: float, b: float, /) -> float: ...

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

    target_unit = targetp
    targetUnit = targetp
    targetunit = targetp

    @staticmethod
    def item_drop(to: Building, amount: float) -> None: ...
    @staticmethod
    def itemDrop(to: Building, amount: float) -> None: ...
    @staticmethod
    def itemdrop(to: Building, amount: float) -> None: ...

    store = item_drop

    @staticmethod
    def item_take(from_: Building, item: Item, amount: float) -> None: ...
    @staticmethod
    def itemTake(from_: Building, item: Item, amount: float) -> None: ...
    @staticmethod
    def itemtake(from_: Building, item: Item, amount: float) -> None: ...

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
    def auto_pathfind() -> None: ...
    @staticmethod
    def autoPathfind() -> None: ...
    @staticmethod
    def autopathfind() -> None: ...
    @staticmethod
    def boost(enabled: bool | float) -> None: ...
    @staticmethod
    def target(x: float, y: float, shoot: bool | float) -> None: ...
    @staticmethod
    def ceasefire() -> None: ...
    @staticmethod
    def pay_drop() -> None: ...
    @staticmethod
    def payDrop() -> None: ...
    @staticmethod
    def paydrop() -> None: ...
    @staticmethod
    def drop() -> None: ...
    @staticmethod
    def pay_take(take_units: bool | float) -> None: ...
    @staticmethod
    def payTake(take_units: bool | float) -> None: ...
    @staticmethod
    def paytake(take_units: bool | float) -> None: ...
    @staticmethod
    def lift() -> None: ...
    @staticmethod
    def carry() -> None: ...
    @staticmethod
    def pay_enter() -> None: ...
    @staticmethod
    def payEnter() -> None: ...
    @staticmethod
    def payenter() -> None: ...
    @staticmethod
    def mine(x: float, y: float) -> None: ...
    @staticmethod
    def flag(value: float, /) -> None: ...
    @staticmethod
    def deconstruct(x: float, y: float) -> None: ...
    @staticmethod
    def get_block(x: float, y: float) -> Any: ...
    @staticmethod
    def getBlock(x: float, y: float) -> Any: ...
    @staticmethod
    def getblock(x: float, y: float) -> Any: ...
    @staticmethod
    def within(x: float, y: float, radius: float) -> Any: ...
    @staticmethod
    def unbind() -> None: ...

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
    def line_rect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def lineRect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def linerect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def hollow_rect(
        x: float, y: float, width: float, height: float
    ) -> None: ...
    @staticmethod
    def hollowRect(x: float, y: float, width: float, height: float) -> None: ...
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
    def line_poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def linePoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def linepoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def hollow_poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def hollowPoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def hollowpoly(
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
