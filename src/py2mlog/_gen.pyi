from abc import ABC
from collections.abc import Iterator
from typing import Any, Literal, LiteralString, overload

from py2mlog._types import ColorType, Content

class Item(Content): ...
class Liquid(Content): ...

class Block(Content):
    """
    Includes terrain blocks, not just building types.
    """

class BuildingType(Block): ...
class UnitType(Content): ...
class Team(Content): ...

class Senseable(ABC):
    def __getitem__(self, i: Item | Liquid | str | Any) -> Any: ...
    copper: int
    lead: int
    metaglass: int
    graphite: int
    sand: int
    coal: int
    titanium: int
    thorium: int
    scrap: int
    silicon: int
    plastanium: int
    phase_fabric: int
    surge_alloy: int
    spore_pod: int
    blast_compound: int
    pyratite: int
    beryllium: int
    tungsten: int
    oxide: int
    carbide: int
    fissile_matter: int
    dormant_cyst: int
    water: int
    slag: int
    oil: int
    cryofluid: int
    neoplasm: int
    arkycite: int
    gallium: int
    ozone: int
    hydrogen: int
    nitrogen: int
    cyanogen: int
    graphite_press: int
    multi_press: int
    silicon_smelter: int
    silicon_crucible: int
    kiln: int
    plastanium_compressor: int
    phase_weaver: int
    surge_smelter: int
    cryofluid_mixer: int
    pyratite_mixer: int
    blast_mixer: int
    melter: int
    separator: int
    disassembler: int
    spore_press: int
    pulverizer: int
    coal_centrifuge: int
    incinerator: int
    silicon_arc_furnace: int
    electrolyzer: int
    atmospheric_concentrator: int
    oxidation_chamber: int
    electric_heater: int
    slag_heater: int
    phase_heater: int
    heat_redirector: int
    small_heat_redirector: int
    heat_router: int
    slag_incinerator: int
    carbide_crucible: int
    surge_crucible: int
    cyanogen_synthesizer: int
    phase_synthesizer: int
    copper_wall: int
    copper_wall_large: int
    titanium_wall: int
    titanium_wall_large: int
    plastanium_wall: int
    plastanium_wall_large: int
    thorium_wall: int
    thorium_wall_large: int
    phase_wall: int
    phase_wall_large: int
    surge_wall: int
    surge_wall_large: int
    door: int
    door_large: int
    scrap_wall: int
    scrap_wall_large: int
    scrap_wall_huge: int
    scrap_wall_gigantic: int
    beryllium_wall: int
    beryllium_wall_large: int
    tungsten_wall: int
    tungsten_wall_large: int
    blast_door: int
    reinforced_surge_wall: int
    reinforced_surge_wall_large: int
    carbide_wall: int
    carbide_wall_large: int
    shielded_wall: int
    mender: int
    mend_projector: int
    overdrive_projector: int
    overdrive_dome: int
    force_projector: int
    shock_mine: int
    build_tower: int
    regen_projector: int
    shockwave_tower: int
    conveyor: int
    titanium_conveyor: int
    plastanium_conveyor: int
    armored_conveyor: int
    junction: int
    bridge_conveyor: int
    phase_conveyor: int
    sorter: int
    inverted_sorter: int
    router: int
    distributor: int
    overflow_gate: int
    underflow_gate: int
    unloader: int
    mass_driver: int
    duct: int
    armored_duct: int
    duct_router: int
    overflow_duct: int
    underflow_duct: int
    duct_bridge: int
    duct_unloader: int
    surge_conveyor: int
    surge_router: int
    unit_cargo_loader: int
    unit_cargo_unload_point: int
    mechanical_pump: int
    rotary_pump: int
    impulse_pump: int
    conduit: int
    pulse_conduit: int
    plated_conduit: int
    liquid_router: int
    liquid_container: int
    liquid_tank: int
    liquid_junction: int
    bridge_conduit: int
    phase_conduit: int
    reinforced_pump: int
    reinforced_conduit: int
    reinforced_liquid_junction: int
    reinforced_bridge_conduit: int
    reinforced_liquid_router: int
    reinforced_liquid_container: int
    reinforced_liquid_tank: int
    power_node: int
    power_node_large: int
    surge_tower: int
    diode: int
    battery: int
    battery_large: int
    combustion_generator: int
    thermal_generator: int
    steam_generator: int
    differential_generator: int
    rtg_generator: int
    solar_panel: int
    solar_panel_large: int
    thorium_reactor: int
    impact_reactor: int
    beam_node: int
    beam_tower: int
    beam_link: int
    turbine_condenser: int
    chemical_combustion_chamber: int
    pyrolysis_generator: int
    flux_reactor: int
    neoplasia_reactor: int
    mechanical_drill: int
    pneumatic_drill: int
    laser_drill: int
    blast_drill: int
    water_extractor: int
    cultivator: int
    oil_extractor: int
    vent_condenser: int
    cliff_crusher: int
    large_cliff_crusher: int
    plasma_bore: int
    large_plasma_bore: int
    impact_drill: int
    eruption_drill: int
    core_foundation: int
    core_nucleus: int
    core_bastion: int
    core_citadel: int
    core_acropolis: int
    container: int
    vault: int
    reinforced_container: int
    reinforced_vault: int
    duo: int
    scatter: int
    scorch: int
    hail: int
    wave: int
    lancer: int
    arc: int
    parallax: int
    swarmer: int
    salvo: int
    segment: int
    tsunami: int
    fuse: int
    ripple: int
    cyclone: int
    foreshadow: int
    spectre: int
    meltdown: int
    breach: int
    diffuse: int
    sublimate: int
    titan: int
    disperse: int
    afflict: int
    lustre: int
    scathe: int
    smite: int
    malign: int
    ground_factory: int
    air_factory: int
    naval_factory: int
    additive_reconstructor: int
    multiplicative_reconstructor: int
    exponential_reconstructor: int
    tetrative_reconstructor: int
    repair_point: int
    repair_turret: int
    tank_fabricator: int
    ship_fabricator: int
    mech_fabricator: int
    tank_refabricator: int
    ship_refabricator: int
    mech_refabricator: int
    prime_refabricator: int
    tank_assembler: int
    ship_assembler: int
    mech_assembler: int
    basic_assembler_module: int
    unit_repair_tower: int
    payload_conveyor: int
    payload_router: int
    reinforced_payload_conveyor: int
    reinforced_payload_router: int
    payload_mass_driver: int
    large_payload_mass_driver: int
    small_deconstructor: int
    deconstructor: int
    constructor: int
    large_constructor: int
    payload_loader: int
    payload_unloader: int
    message: int
    switch: int
    micro_processor: int
    logic_processor: int
    hyper_processor: int
    memory_cell: int
    memory_bank: int
    logic_display: int
    large_logic_display: int
    tile_logic_display: int
    canvas: int
    large_canvas: int
    reinforced_message: int
    dagger: int
    mace: int
    fortress: int
    scepter: int
    reign: int
    nova: int
    pulsar: int
    quasar: int
    vela: int
    corvus: int
    crawler: int
    atrax: int
    spiroct: int
    arkyid: int
    toxopid: int
    flare: int
    horizon: int
    zenith: int
    antumbra: int
    eclipse: int
    mono: int
    poly: int
    mega: int
    quad: int
    oct: int
    risso: int
    minke: int
    bryde: int
    sei: int
    omura: int
    retusa: int
    oxynoe: int
    cyerce: int
    aegires: int
    navanax: int
    alpha: int
    beta: int
    gamma: int
    stell: int
    locus: int
    precept: int
    vanquish: int
    conquer: int
    merui: int
    cleroi: int
    anthicus: int
    anthicus_missile: int
    tecta: int
    collaris: int
    elude: int
    avert: int
    obviate: int
    quell: int
    quell_missile: int
    disrupt: int
    disrupt_missile: int
    renale: int
    latum: int
    evoke: int
    incite: int
    emanate: int
    block: int
    manifold: int
    assembly_drone: int
    dummy: int
    scathe_missile: int
    scathe_missile_phase: int
    scathe_missile_surge: int
    scathe_missile_surge_split: int
    turret_unit_build_tower: int
    derelict: int
    sharded: int
    crux: int
    malis: int
    green: int
    blue: int
    neoplastic: int
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
    graphite_press: BuildingType
    multi_press: BuildingType
    silicon_smelter: BuildingType
    silicon_crucible: BuildingType
    kiln: BuildingType
    plastanium_compressor: BuildingType
    phase_weaver: BuildingType
    surge_smelter: BuildingType
    cryofluid_mixer: BuildingType
    pyratite_mixer: BuildingType
    blast_mixer: BuildingType
    melter: BuildingType
    separator: BuildingType
    disassembler: BuildingType
    spore_press: BuildingType
    pulverizer: BuildingType
    coal_centrifuge: BuildingType
    incinerator: BuildingType
    silicon_arc_furnace: BuildingType
    electrolyzer: BuildingType
    atmospheric_concentrator: BuildingType
    oxidation_chamber: BuildingType
    electric_heater: BuildingType
    slag_heater: BuildingType
    phase_heater: BuildingType
    heat_redirector: BuildingType
    small_heat_redirector: BuildingType
    heat_router: BuildingType
    slag_incinerator: BuildingType
    carbide_crucible: BuildingType
    slag_centrifuge: Block
    surge_crucible: BuildingType
    cyanogen_synthesizer: BuildingType
    phase_synthesizer: BuildingType
    heat_reactor: Block
    copper_wall: BuildingType
    copper_wall_large: BuildingType
    titanium_wall: BuildingType
    titanium_wall_large: BuildingType
    plastanium_wall: BuildingType
    plastanium_wall_large: BuildingType
    thorium_wall: BuildingType
    thorium_wall_large: BuildingType
    phase_wall: BuildingType
    phase_wall_large: BuildingType
    surge_wall: BuildingType
    surge_wall_large: BuildingType
    door: BuildingType
    door_large: BuildingType
    scrap_wall: BuildingType
    scrap_wall_large: BuildingType
    scrap_wall_huge: BuildingType
    scrap_wall_gigantic: BuildingType
    thruster: Block
    beryllium_wall: BuildingType
    beryllium_wall_large: BuildingType
    tungsten_wall: BuildingType
    tungsten_wall_large: BuildingType
    blast_door: BuildingType
    reinforced_surge_wall: BuildingType
    reinforced_surge_wall_large: BuildingType
    carbide_wall: BuildingType
    carbide_wall_large: BuildingType
    shielded_wall: BuildingType
    mender: BuildingType
    mend_projector: BuildingType
    overdrive_projector: BuildingType
    overdrive_dome: BuildingType
    force_projector: BuildingType
    shock_mine: BuildingType
    radar: Block
    build_tower: BuildingType
    regen_projector: BuildingType
    shockwave_tower: BuildingType
    shield_projector: Block
    large_shield_projector: Block
    conveyor: BuildingType
    titanium_conveyor: BuildingType
    plastanium_conveyor: BuildingType
    armored_conveyor: BuildingType
    junction: BuildingType
    bridge_conveyor: BuildingType
    phase_conveyor: BuildingType
    sorter: BuildingType
    inverted_sorter: BuildingType
    router: BuildingType
    distributor: BuildingType
    overflow_gate: BuildingType
    underflow_gate: BuildingType
    unloader: BuildingType
    mass_driver: BuildingType
    duct: BuildingType
    armored_duct: BuildingType
    duct_router: BuildingType
    overflow_duct: BuildingType
    underflow_duct: BuildingType
    duct_bridge: BuildingType
    duct_unloader: BuildingType
    surge_conveyor: BuildingType
    surge_router: BuildingType
    unit_cargo_loader: BuildingType
    unit_cargo_unload_point: BuildingType
    mechanical_pump: BuildingType
    rotary_pump: BuildingType
    impulse_pump: BuildingType
    conduit: BuildingType
    pulse_conduit: BuildingType
    plated_conduit: BuildingType
    liquid_router: BuildingType
    liquid_container: BuildingType
    liquid_tank: BuildingType
    liquid_junction: BuildingType
    bridge_conduit: BuildingType
    phase_conduit: BuildingType
    reinforced_pump: BuildingType
    reinforced_conduit: BuildingType
    reinforced_liquid_junction: BuildingType
    reinforced_bridge_conduit: BuildingType
    reinforced_liquid_router: BuildingType
    reinforced_liquid_container: BuildingType
    reinforced_liquid_tank: BuildingType
    power_node: BuildingType
    power_node_large: BuildingType
    surge_tower: BuildingType
    diode: BuildingType
    battery: BuildingType
    battery_large: BuildingType
    combustion_generator: BuildingType
    thermal_generator: BuildingType
    steam_generator: BuildingType
    differential_generator: BuildingType
    rtg_generator: BuildingType
    solar_panel: BuildingType
    solar_panel_large: BuildingType
    thorium_reactor: BuildingType
    impact_reactor: BuildingType
    beam_node: BuildingType
    beam_tower: BuildingType
    beam_link: BuildingType
    turbine_condenser: BuildingType
    chemical_combustion_chamber: BuildingType
    pyrolysis_generator: BuildingType
    flux_reactor: BuildingType
    neoplasia_reactor: BuildingType
    mechanical_drill: BuildingType
    pneumatic_drill: BuildingType
    laser_drill: BuildingType
    blast_drill: BuildingType
    water_extractor: BuildingType
    cultivator: BuildingType
    oil_extractor: BuildingType
    vent_condenser: BuildingType
    cliff_crusher: BuildingType
    large_cliff_crusher: BuildingType
    plasma_bore: BuildingType
    large_plasma_bore: BuildingType
    impact_drill: BuildingType
    eruption_drill: BuildingType
    core_shard: Block
    core_foundation: BuildingType
    core_nucleus: BuildingType
    core_bastion: BuildingType
    core_citadel: BuildingType
    core_acropolis: BuildingType
    container: BuildingType
    vault: BuildingType
    reinforced_container: BuildingType
    reinforced_vault: BuildingType
    duo: BuildingType
    scatter: BuildingType
    scorch: BuildingType
    hail: BuildingType
    wave: BuildingType
    lancer: BuildingType
    arc: BuildingType
    parallax: BuildingType
    swarmer: BuildingType
    salvo: BuildingType
    segment: BuildingType
    tsunami: BuildingType
    fuse: BuildingType
    ripple: BuildingType
    cyclone: BuildingType
    foreshadow: BuildingType
    spectre: BuildingType
    meltdown: BuildingType
    breach: BuildingType
    diffuse: BuildingType
    sublimate: BuildingType
    titan: BuildingType
    disperse: BuildingType
    afflict: BuildingType
    lustre: BuildingType
    scathe: BuildingType
    smite: BuildingType
    malign: BuildingType
    ground_factory: BuildingType
    air_factory: BuildingType
    naval_factory: BuildingType
    additive_reconstructor: BuildingType
    multiplicative_reconstructor: BuildingType
    exponential_reconstructor: BuildingType
    tetrative_reconstructor: BuildingType
    repair_point: BuildingType
    repair_turret: BuildingType
    tank_fabricator: BuildingType
    ship_fabricator: BuildingType
    mech_fabricator: BuildingType
    tank_refabricator: BuildingType
    ship_refabricator: BuildingType
    mech_refabricator: BuildingType
    prime_refabricator: BuildingType
    tank_assembler: BuildingType
    ship_assembler: BuildingType
    mech_assembler: BuildingType
    basic_assembler_module: BuildingType
    unit_repair_tower: BuildingType
    payload_conveyor: BuildingType
    payload_router: BuildingType
    reinforced_payload_conveyor: BuildingType
    reinforced_payload_router: BuildingType
    payload_mass_driver: BuildingType
    large_payload_mass_driver: BuildingType
    small_deconstructor: BuildingType
    deconstructor: BuildingType
    constructor: BuildingType
    large_constructor: BuildingType
    payload_loader: BuildingType
    payload_unloader: BuildingType
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
    message: BuildingType
    switch: BuildingType
    micro_processor: BuildingType
    logic_processor: BuildingType
    hyper_processor: BuildingType
    memory_cell: BuildingType
    memory_bank: BuildingType
    logic_display: BuildingType
    large_logic_display: BuildingType
    tile_logic_display: BuildingType
    canvas: BuildingType
    large_canvas: BuildingType
    reinforced_message: BuildingType
    world_processor: Block
    world_cell: Block
    world_message: Block
    world_switch: Block
    derelict: Team
    sharded: Team
    crux: Team
    malis: Team
    green: Team
    blue: Team
    neoplastic: Team

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

# add args and kwargs cuz the compiler technically allows them
def create_links(*args: Any, **kwargs: Any) -> tuple[Building, ...]:
    """
    Noop. Args are ignored by compiler. Used for typing.
    e.g.
    router1, junction1 = create_links()

    For single elements, still use tuple unpacking, like so:

    router1, = create_links()
           ^  notice the comma
    """

def create_vars(*args: Any, **kwargs: Any) -> tuple[None, ...]:
    """
    Noop. Args are ignored by compiler. Used for typing,
    to intentionally suppress "variable possibly unbound"
    when intentionally using mlog undefined variable behaviour.

    e.g.
    x, y = create_vars()

    For single elements, still use tuple unpacking, like so:

    x, = create_vars()
     ^  notice the comma
    """

def print(
    *args: Any,
    sep: str = " ",
    end: str = r"\n",
    flush: Building | Literal[False] = ...,
) -> None:
    """
    Param 'flush' defaults to 'message1'. Set 'flush' to False to omit 'printflush'.
    """

def mlog_raw(src: LiteralString, /) -> None:
    """
    Emit raw mlog. Use a raw string so that escape sequences work properly.
    """

def lookup(
    content_type: Literal["block", "unit", "item", "liquid", "team"] | Any,
    id: int,
) -> BuildingType | UnitType | Item | Liquid | Team: ...
def radar(
    building: Building,
    filter1: Literal[
        "any", "enemy", "ally", "player", "attacker", "flying", "boss", "ground"
    ]
    | Any = "any",
    filter2: Literal[
        "any", "enemy", "ally", "player", "attacker", "flying", "boss", "ground"
    ]
    | Any = "any",
    filter3: Literal[
        "any", "enemy", "ally", "player", "attacker", "flying", "boss", "ground"
    ]
    | Any = "any",
    /,
    *,
    order: bool | float | str = True,
    key: Literal[
        "distance",
        "health",
        "shield",
        "armor",
        "maxHealth",
        "max_health",
        "maxhealth",
    ]
    | Any = "distance",
) -> UnitObj | None: ...
def ord(character: str, /) -> float: ...
def min(arg1: float, arg2: float) -> float: ...
def Color(x: float | ColorType | str, /) -> ColorType: ...
def color(x: float | ColorType | str, /) -> ColorType: ...
def sleep(t: float, /) -> None: ...
def wait(t: float, /) -> None: ...
def print_raw(value: Any, /) -> None: ...
def printRaw(value: Any, /) -> None: ...
def printraw(value: Any, /) -> None: ...
def print_char(value: float, /) -> None: ...
def printChar(value: float, /) -> None: ...
def printchar(value: float, /) -> None: ...
def format_raw(value: Any, /) -> None: ...
def formatRaw(value: Any, /) -> None: ...
def formatraw(value: Any, /) -> None: ...
def print_flush(tgt: Any = ..., /) -> None:
    """
    Param 'tgt' defaults to 'message1'.
    """

def printFlush(tgt: Any = ..., /) -> None:
    """
    Param 'tgt' defaults to 'message1'.
    """

def printflush(tgt: Any = ..., /) -> None:
    """
    Param 'tgt' defaults to 'message1'.
    """

def end() -> None:
    """
    Jump to the top of the program.
    Does NOT terminate the program; use 'stop()' for that instead.
    """

def top() -> None:
    """
    Jump to the top of the program.
    Does NOT terminate the program; use 'stop()' for that instead.
    """

def stop() -> None:
    """
    Terminates the program.
    """

def set_rate(rate: float, /) -> None: ...
def setRate(rate: float, /) -> None: ...
def setrate(rate: float, /) -> None: ...
def set_ipt(rate: float, /) -> None: ...
def setIpt(rate: float, /) -> None: ...
def setipt(rate: float, /) -> None: ...
def pack_color(r: float, g: float, b: float, a: float) -> float:
    """
    Arguments should be between 0 and 1 inclusive.
    """

def packColor(r: float, g: float, b: float, a: float) -> float:
    """
    Arguments should be between 0 and 1 inclusive.
    """

def packcolor(r: float, g: float, b: float, a: float) -> float:
    """
    Arguments should be between 0 and 1 inclusive.
    """

def unpack_color(color: ColorType, /) -> float: ...
def unpackColor(color: ColorType, /) -> float: ...
def unpackcolor(color: ColorType, /) -> float: ...
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

def vecAngle(x: float, y: float, /) -> float:
    """
    Similar to atan2.
    Note that this function takes (x, y) and not (y, x).
    Returns 0 to 360 **degrees**.
    """

def vecangle(x: float, y: float, /) -> float:
    """
    Similar to atan2.
    Note that this function takes (x, y) and not (y, x).
    Returns 0 to 360 **degrees**.
    """

def vec_len(a: float, b: float, /) -> float: ...
def vecLen(a: float, b: float, /) -> float: ...
def veclen(a: float, b: float, /) -> float: ...
def logn(x: float, base: float) -> float: ...
def mod(a: float, b: float, /) -> float: ...
def ushr(a: float, b: float, /) -> float: ...
def angle_diff(a: float, b: float, /) -> float: ...
def angleDiff(a: float, b: float, /) -> float: ...
def anglediff(a: float, b: float, /) -> float: ...
def noise(a: float, b: float, /) -> float: ...

class Unit:
    @staticmethod
    def bind(type: str | UnitType | UnitObj, /) -> None: ...
    @staticmethod
    def radar(
        filter1: str | Any = "any",
        filter2: str | Any = "any",
        filter3: str | Any = "any",
        /,
        *,
        order: bool | float | str = True,
        key: str = "distance",
    ) -> UnitObj | None: ...
    @overload
    @staticmethod
    # Any here for var name as subop name (e.g. subop=ore instead of subop="ore")
    def locate(
        subop: Literal["ore"] | Any, /, *, ore_type: Item
    ) -> tuple[float, float, bool]: ...
    @overload
    @staticmethod
    def locate(
        subop: Literal["building"] | Any,
        /,
        *,
        block_flag: str | Any,
        is_enemy_building: bool | int | str,
    ) -> tuple[float, float, bool, Building | None]: ...
    @overload
    @staticmethod
    def locate(
        subop: Literal["spawn", "damaged"] | Any, /
    ) -> tuple[float, float, bool, Building | None]: ...
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
