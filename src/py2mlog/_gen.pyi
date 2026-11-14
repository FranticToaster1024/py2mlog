from typing import Any, overload

from py2mlog._base import Block, Building, Content, Item, Liquid, _Color, _Unit

class Env:
    this: Building
    unit: _Unit
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

def abs(x: Any = ..., /) -> Any: ...
def ord(character: Any = ..., /) -> Any: ...
def min(arg1: Any = ..., arg2: Any = ...) -> Any: ...
def Color(x: Any = ..., /) -> _Color: ...
def sleep(t: Any = ..., /) -> None: ...
def wait(t: Any = ..., /) -> None: ...

class Unit:
    @overload
    @staticmethod
    def locate(subop: str, /, *, ore_type: Item) -> None: ...
    @overload
    @staticmethod
    # Any here for var name as subop name (e.g. subop=ore instead of subop="ore")
    def locate(
        subop: str | Any,
        /,
        *,
        block_flag: str | Any,
        is_enemy_building: bool | float | str,
    ) -> None: ...
    @overload
    @staticmethod
    def locate(subop: str, /) -> None: ...
    @overload
    @staticmethod
    def shoot() -> None: ...
    @overload
    @staticmethod
    def shoot(x: float, y: float) -> None: ...
    @staticmethod
    # should be int i worry that return types may be inaccurate
    def targetp(unit: Unit, shoot: bool | float) -> None: ...

    target_unit = targetp

    @staticmethod
    def item_drop(to: Building, amount: float) -> None: ...

    store = item_drop

    @staticmethod
    def item_take(from_: Building, item: Item, amount: float) -> None: ...

    fetch = item_take
    @staticmethod
    def bind(type: str | Content = ..., /) -> None: ...
    @staticmethod
    def radar(
        filter1: str | Any = ...,
        filter2: str | Any = ...,
        filter3: str | Any = ...,
        /,
        *,
        order: bool | float | str = ...,
        key: str = ...,
    ) -> Any: ...
    @staticmethod
    def idle() -> None: ...
    @staticmethod
    def stop() -> None: ...
    @staticmethod
    def move(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def approach(
        x: float = ..., y: float = ..., radius: float = ...
    ) -> None: ...
    @staticmethod
    def pathfind(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def autoPathfind() -> None: ...
    @staticmethod
    def autopathfind() -> None: ...
    @staticmethod
    def auto_pathfind() -> None: ...
    @staticmethod
    def boost(enabled: bool | float = ...) -> None: ...
    @staticmethod
    def target(
        x: float = ..., y: float = ..., shoot: bool | float = ...
    ) -> None: ...
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
    def paytake(take_units: bool | float = ...) -> None: ...
    @staticmethod
    def pay_take(take_units: bool | float = ...) -> None: ...
    @staticmethod
    def payTake(take_units: bool | float = ...) -> None: ...
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
    def mine(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def flag(value: float = ..., /) -> None: ...
    @staticmethod
    def build(
        x: float = ...,
        y: float = ...,
        block: Content = ...,
        rotation: float = ...,
        config: Any = ...,
    ) -> None: ...
    @staticmethod
    def deconstruct(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def getBlock(x: float = ..., y: float = ...) -> Any: ...
    @staticmethod
    def get_block(x: float = ..., y: float = ...) -> Any: ...
    @staticmethod
    def getblock(x: float = ..., y: float = ...) -> Any: ...
    @staticmethod
    def within(x: float = ..., y: float = ..., radius: float = ...) -> Any: ...
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
    def clear(
        r: float | Any = ..., g: float | Any = ..., b: float | Any = ...
    ) -> None: ...
    @staticmethod
    def fill(
        r: float | Any = ..., g: float | Any = ..., b: float | Any = ...
    ) -> None: ...
    @staticmethod
    def color(
        r: float | Any = ...,
        g: float | Any = ...,
        b: float | Any = ...,
        a: float | Any = ...,
    ) -> None: ...
    @staticmethod
    def col(color: _Color = ..., /) -> None: ...
    @staticmethod
    def stroke(width: float = ...) -> None: ...
    @staticmethod
    def line(
        x1: float = ..., y1: float = ..., x2: float = ..., y2: float = ...
    ) -> None: ...
    @staticmethod
    def rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def fillRect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def fillrect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def fill_rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def linerect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def line_rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def lineRect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def hollowrect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def hollowRect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def hollow_rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def fillpoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def fillPoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def fill_poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def linepoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def linePoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def line_poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def hollowpoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def hollowPoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def hollow_poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def triangle(
        x1: float = ...,
        y1: float = ...,
        x2: float = ...,
        y2: float = ...,
        x3: float = ...,
        y3: float = ...,
    ) -> None: ...
    @staticmethod
    def image(
        x: float = ...,
        y: float = ...,
        image: Content = ...,
        size: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def print(
        x: float = ..., y: float = ..., alignment: Content = ...
    ) -> None: ...
    @staticmethod
    def translate(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def scale(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def rotate(degrees: float = ...) -> None: ...
    @staticmethod
    def reset() -> None: ...

class Links:
    def __getitem__(self, index: int) -> Building: ...

Link = Links

class MemBuilding(Building):
    def __getitem__(self, index: int) -> Any: ...
    def __setitem__(self, index: int, value: Any) -> None: ...

class Mem:
    def __getattr__(self, name: str) -> MemBuilding: ...

    # can't really generate MemBuilding
    @staticmethod
    def read(cell: MemBuilding, index: int) -> Any: ...
    @staticmethod
    def write(value: int, cell: MemBuilding, index: int) -> Any: ...
    @staticmethod
    def clear(
        r: float | Any = ..., g: float | Any = ..., b: float | Any = ...
    ) -> None: ...
    @staticmethod
    def fill(
        r: float | Any = ..., g: float | Any = ..., b: float | Any = ...
    ) -> None: ...
    @staticmethod
    def color(
        r: float | Any = ...,
        g: float | Any = ...,
        b: float | Any = ...,
        a: float | Any = ...,
    ) -> None: ...
    @staticmethod
    def col(color: _Color = ..., /) -> None: ...
    @staticmethod
    def stroke(width: float = ...) -> None: ...
    @staticmethod
    def line(
        x1: float = ..., y1: float = ..., x2: float = ..., y2: float = ...
    ) -> None: ...
    @staticmethod
    def rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def fillRect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def fillrect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def fill_rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def linerect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def line_rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def lineRect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def hollowrect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def hollowRect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def hollow_rect(
        x: float = ..., y: float = ..., width: float = ..., height: float = ...
    ) -> None: ...
    @staticmethod
    def poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def fillpoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def fillPoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def fill_poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def linepoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def linePoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def line_poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def hollowpoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def hollowPoly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def hollow_poly(
        x: float = ...,
        y: float = ...,
        sides: float = ...,
        radius: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def triangle(
        x1: float = ...,
        y1: float = ...,
        x2: float = ...,
        y2: float = ...,
        x3: float = ...,
        y3: float = ...,
    ) -> None: ...
    @staticmethod
    def image(
        x: float = ...,
        y: float = ...,
        image: Content = ...,
        size: float = ...,
        rotation: float = ...,
    ) -> None: ...
    @staticmethod
    def print(
        x: float = ..., y: float = ..., alignment: Content = ...
    ) -> None: ...
    @staticmethod
    def translate(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def scale(x: float = ..., y: float = ...) -> None: ...
    @staticmethod
    def rotate(degrees: float = ...) -> None: ...
    @staticmethod
    def reset() -> None: ...
    @staticmethod
    def flush(target: Any = ...) -> None: ...
