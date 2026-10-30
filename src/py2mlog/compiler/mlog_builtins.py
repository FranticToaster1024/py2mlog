from collections.abc import Mapping

from py2mlog.mlog.mlog_expressions import MlogBuiltin, MlogExpr

# TODO: maybe use mimex data?


RES_MAP: Mapping[str, MlogBuiltin] = {
    s: MlogBuiltin(s)
    for s in [
        # items
        "copper",
        "lead",
        "metaglass",
        "graphite",
        "sand",
        "coal",
        "titanium",
        "thorium",
        "scrap",
        "silicon",
        "plastanium",
        "phase-fabric",
        "surge-alloy",
        "spore-pod",
        "blast-compound",
        "pyratite",
        "beryllium",
        "tungsten",
        "oxide",
        "carbide",
        "fissile-matter",
        "dormant-cyst",
        # liquids
        "water",
        "slag",
        "oil",
        "cryofluid",
        "neoplasm",
        "arkycite",
        "gallium",
        "ozone",
        "hydrogen",
        "nitrogen",
        "cyanogen",
    ]
}
# yea blocks n stuff will definitely need mimex data

ENV_ATTR_MAP: Mapping[str, MlogExpr] = RES_MAP  # add other maps later maybe
