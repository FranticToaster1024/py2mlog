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
    duct_bridge: int
    unit_repair_tower: int
    large_constructor: int
    liquid_container: int
    phase_wall_large: int
    thorium_reactor: int
    thorium: int
    memory_cell: int
    large_cliff_crusher: int
    ground_factory: int
    carbide_crucible: int
    reinforced_surge_wall_large: int
    carbide_wall: int
    mend_projector: int
    micro_processor: int
    surge_wall_large: int
    mass_driver: int
    poly: int
    renale: int
    scrap_wall_huge: int
    scathe_missile_phase: int
    plastanium_conveyor: int
    memory_bank: int
    phase_wall: int
    oxidation_chamber: int
    oct: int
    surge_router: int
    combustion_generator: int
    reinforced_pump: int
    lead: int
    overdrive_dome: int
    horizon: int
    additive_reconstructor: int
    mace: int
    assembly_drone: int
    air_factory: int
    duct_unloader: int
    quell_missile: int
    alpha: int
    core_citadel: int
    merui: int
    overflow_gate: int
    segment: int
    multi_press: int
    gamma: int
    risso: int
    door: int
    scrap_wall_large: int
    coal: int
    multiplicative_reconstructor: int
    flux_reactor: int
    obviate: int
    oil: int
    meltdown: int
    plasma_bore: int
    large_canvas: int
    cyerce: int
    reinforced_liquid_junction: int
    pulse_conduit: int
    sand: int
    mono: int
    flare: int
    thermal_generator: int
    disrupt: int
    phase_synthesizer: int
    water: int
    duct: int
    impulse_pump: int
    salvo: int
    plastanium_compressor: int
    surge_crucible: int
    scrap: int
    tsunami: int
    ship_fabricator: int
    build_tower: int
    impact_reactor: int
    impact_drill: int
    copper_wall: int
    solar_panel_large: int
    basic_assembler_module: int
    oxynoe: int
    duct_router: int
    force_projector: int
    underflow_duct: int
    payload_mass_driver: int
    battery: int
    phase_fabric: int
    electric_heater: int
    eruption_drill: int
    diffuse: int
    kiln: int
    core_foundation: int
    bridge_conveyor: int
    hydrogen: int
    disassembler: int
    metaglass: int
    neoplasia_reactor: int
    reinforced_payload_conveyor: int
    disrupt_missile: int
    titanium_wall: int
    silicon_smelter: int
    armored_duct: int
    repair_turret: int
    eclipse: int
    ripple: int
    surge_smelter: int
    breach: int
    carbide: int
    atmospheric_concentrator: int
    avert: int
    beryllium: int
    large_plasma_bore: int
    mech_refabricator: int
    titan: int
    quad: int
    minke: int
    pulverizer: int
    duo: int
    beryllium_wall_large: int
    surge_wall: int
    scorch: int
    oxide: int
    lustre: int
    mechanical_pump: int
    wave: int
    rtg_generator: int
    battery_large: int
    pyrolysis_generator: int
    reinforced_liquid_tank: int
    ship_refabricator: int
    surge_alloy: int
    oil_extractor: int
    quasar: int
    shockwave_tower: int
    fuse: int
    blast_mixer: int
    cryofluid: int
    tungsten_wall: int
    retusa: int
    inverted_sorter: int
    swarmer: int
    gallium: int
    carbide_wall_large: int
    plated_conduit: int
    anthicus_missile: int
    mech_fabricator: int
    logic_display: int
    diode: int
    cultivator: int
    logic_processor: int
    small_heat_redirector: int
    blast_compound: int
    nova: int
    block: int
    dagger: int
    plastanium_wall_large: int
    titanium: int
    pulsar: int
    phase_conveyor: int
    locus: int
    exponential_reconstructor: int
    parallax: int
    incinerator: int
    fissile_matter: int
    blast_door: int
    tank_refabricator: int
    switch: int
    cyanogen_synthesizer: int
    scrap_wall: int
    titanium_conveyor: int
    door_large: int
    elude: int
    evoke: int
    liquid_router: int
    vault: int
    scathe_missile: int
    toxopid: int
    omura: int
    dummy: int
    tile_logic_display: int
    slag_heater: int
    sublimate: int
    rotary_pump: int
    spectre: int
    deconstructor: int
    slag: int
    reinforced_payload_router: int
    differential_generator: int
    cliff_crusher: int
    ozone: int
    scathe_missile_surge_split: int
    shielded_wall: int
    router: int
    core_acropolis: int
    foreshadow: int
    payload_conveyor: int
    vela: int
    latum: int
    copper: int
    tank_fabricator: int
    spiroct: int
    blast_drill: int
    reinforced_liquid_router: int
    titanium_wall_large: int
    scatter: int
    reinforced_surge_wall: int
    pyratite_mixer: int
    cleroi: int
    spore_pod: int
    scathe_missile_surge: int
    beryllium_wall: int
    plastanium: int
    conquer: int
    unloader: int
    tetrative_reconstructor: int
    atrax: int
    silicon_crucible: int
    neoplasm: int
    spore_press: int
    graphite: int
    mechanical_drill: int
    silicon: int
    payload_loader: int
    constructor: int
    heat_redirector: int
    beam_link: int
    bridge_conduit: int
    tungsten: int
    overdrive_projector: int
    emanate: int
    incite: int
    payload_unloader: int
    plastanium_wall: int
    scathe: int
    pyratite: int
    tecta: int
    unit_cargo_loader: int
    precept: int
    liquid_tank: int
    mega: int
    unit_cargo_unload_point: int
    phase_weaver: int
    corvus: int
    separator: int
    aegires: int
    antumbra: int
    junction: int
    silicon_arc_furnace: int
    turret_unit_build_tower: int
    scepter: int
    graphite_press: int
    phase_conduit: int
    phase_heater: int
    naval_factory: int
    crawler: int
    reinforced_bridge_conduit: int
    surge_tower: int
    copper_wall_large: int
    prime_refabricator: int
    sorter: int
    beta: int
    beam_tower: int
    smite: int
    hail: int
    power_node: int
    water_extractor: int
    cyclone: int
    lancer: int
    quell: int
    tungsten_wall_large: int
    fortress: int
    repair_point: int
    arkyid: int
    conveyor: int
    afflict: int
    slag_incinerator: int
    chemical_combustion_chamber: int
    arc: int
    reinforced_conduit: int
    container: int
    scrap_wall_gigantic: int
    conduit: int
    mender: int
    malign: int
    turbine_condenser: int
    solar_panel: int
    steam_generator: int
    stell: int
    message: int
    tank_assembler: int
    beam_node: int
    arkycite: int
    thorium_wall_large: int
    melter: int
    zenith: int
    sei: int
    dormant_cyst: int
    reign: int
    reinforced_liquid_container: int
    vent_condenser: int
    vanquish: int
    thorium_wall: int
    armored_conveyor: int
    navanax: int
    electrolyzer: int
    surge_conveyor: int
    manifold: int
    nitrogen: int
    coal_centrifuge: int
    large_payload_mass_driver: int
    large_logic_display: int
    collaris: int
    pneumatic_drill: int
    ship_assembler: int
    canvas: int
    cryofluid_mixer: int
    distributor: int
    mech_assembler: int
    reinforced_vault: int
    reinforced_message: int
    regen_projector: int
    small_deconstructor: int
    core_nucleus: int
    reinforced_container: int
    heat_router: int
    cyanogen: int
    underflow_gate: int
    core_bastion: int
    laser_drill: int
    overflow_duct: int
    payload_router: int
    liquid_junction: int
    bryde: int
    power_node_large: int
    shock_mine: int
    disperse: int
    anthicus: int
    hyper_processor: int
    # TODO: manually type these attributes or something
    name: Any
    selectedblock: Any
    pingx: Any
    shield: Any
    size: Any
    displaywidth: Any
    memorycapacity: Any
    displayheight: Any
    pingtext: Any
    config: Any
    firstitem: Any
    shooting: Any
    payloadcount: Any
    payloadcapacity: Any
    buildx: Any
    powercapacity: Any
    building: Any
    velocityx: Any
    health: Any
    powernetin: Any
    currentammotype: Any
    armor: Any
    controller: Any
    shooty: Any
    breaking: Any
    liquidcapacity: Any
    pingy: Any
    progress: Any
    type: Any
    minex: Any
    timescale: Any
    boosting: Any
    miney: Any
    solid: Any
    payloadtype: Any
    bullettime: Any
    maxhealth: Any
    bulletlifetime: Any
    color: Any
    maxunits: Any
    team: Any
    x: Any
    id: Any
    selectedrotation: Any
    flag: Any
    itemcapacity: Any
    heat: Any
    totalliquids: Any
    powernetout: Any
    powernetcapacity: Any
    buffersize: Any
    mining: Any
    enabled: Any
    flying: Any
    dead: Any
    rotation: Any
    ammo: Any
    y: Any
    totalitems: Any
    totalpower: Any
    totalpayload: Any
    powernetstored: Any
    efficiency: Any
    range: Any
    controlled: Any
    operations: Any
    velocityy: Any
    shootx: Any
    ammocapacity: Any
    buildy: Any
    speed: Any

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
    targetunit = targetp
    target_unit = targetp

    @staticmethod
    def itemDrop(to: Building, amount: float) -> None: ...
    @staticmethod
    def item_drop(to: Building, amount: float) -> None: ...
    @staticmethod
    def itemdrop(to: Building, amount: float) -> None: ...

    store = item_drop

    @staticmethod
    def itemtake(from_: Building, item: Item, amount: float) -> None: ...
    @staticmethod
    def itemTake(from_: Building, item: Item, amount: float) -> None: ...
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
    def auto_pathfind() -> None: ...
    @staticmethod
    def autoPathfind() -> None: ...
    @staticmethod
    def boost(enabled: bool | float) -> None: ...
    @staticmethod
    def target(x: float, y: float, shoot: bool | float) -> None: ...
    @staticmethod
    def ceasefire() -> None: ...
    @staticmethod
    def pay_drop() -> None: ...
    @staticmethod
    def paydrop() -> None: ...
    @staticmethod
    def payDrop() -> None: ...
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
    def getblock(x: float, y: float) -> Any: ...
    @staticmethod
    def getBlock(x: float, y: float) -> Any: ...
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
    def fillrect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def fillRect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def fill_rect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def lineRect(x: float, y: float, width: float, height: float) -> None: ...
    @staticmethod
    def line_rect(x: float, y: float, width: float, height: float) -> None: ...
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
    def fillPoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def fillpoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def fill_poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def linePoly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def line_poly(
        x: float, y: float, sides: float, radius: float, rotation: float
    ) -> None: ...
    @staticmethod
    def linepoly(
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
    def hollow_poly(
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
