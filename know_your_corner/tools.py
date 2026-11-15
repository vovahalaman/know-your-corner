"""The functions the agent may call, and run_tool() (issues #10, #11).

Every tool returns a dict. Failures come back as {"error": ...} that say what
is allowed; run_tool() never raises.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from know_your_corner import store
from know_your_corner.schemas import GetNeighborhoodArgs, ListNeighborhoodsArgs, Neighborhood

MAX_RENT = 5000


def _summary(n: Neighborhood) -> dict[str, Any]:
    return {"name": n.name, "rent_room_avg": n.rent_room_avg, "metro_lines": n.metro_lines}


def _names() -> list[str]:
    return [n.name for n in store.neighborhoods()]


def list_neighborhoods(args: ListNeighborhoodsArgs) -> dict[str, Any]:
    rows = list(store.neighborhoods())
    if args.metro_line:
        rows = [n for n in rows if args.metro_line in n.metro_lines]
    no_rent_data: list[str] = []
    if args.max_room_rent is not None:
        no_rent_data = [n.name for n in rows if n.rent_room_avg is None]
        rows = [n for n in rows if n.rent_room_avg is not None and n.rent_room_avg <= args.max_room_rent]
    result: dict[str, Any] = {"neighborhoods": [_summary(n) for n in rows]}
    if no_rent_data:
        result["no_rent_data"] = no_rent_data
    return result


def get_neighborhood(args: GetNeighborhoodArgs) -> dict[str, Any]:
    n = store.find_neighborhood(args.name)
    if n is None:
        return {"error": f"No data on '{args.name}'. Known neighborhoods: {', '.join(_names())}."}
    return n.model_dump(mode="json")


def check(name: str, args: BaseModel) -> str | None:
    if isinstance(args, ListNeighborhoodsArgs) and args.max_room_rent is not None:
        if not 0 < args.max_room_rent <= MAX_RENT:
            return f"max_room_rent must be between 1 and {MAX_RENT} EUR per month."
    return None


@dataclass(frozen=True)
class Tool:
    description: str
    args: type[BaseModel]
    fn: Callable[[Any], dict[str, Any]]


TOOLS: dict[str, Tool] = {
    "list_neighborhoods": Tool(
        "List Lisbon neighborhoods we have data on, optionally filtered by room rent or metro line.",
        ListNeighborhoodsArgs,
        list_neighborhoods,
    ),
    "get_neighborhood": Tool(
        "Get all stored facts about one Lisbon neighborhood, with sources and dates.",
        GetNeighborhoodArgs,
        get_neighborhood,
    ),
}


def _parameters(model: type[BaseModel]) -> dict[str, Any]:
    schema = model.model_json_schema()
    schema.pop("title", None)
    for prop in schema.get("properties", {}).values():
        prop.pop("title", None)
        prop.pop("default", None)
    return schema


DECLARATIONS: list[dict[str, Any]] = [
    {"type": "function", "name": name, "description": t.description, "parameters": _parameters(t.args)}
    for name, t in TOOLS.items()
]


def run_tool(name: str, raw_args: dict[str, Any] | None) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        return {"error": f"Unknown tool '{name}'. Available: {', '.join(TOOLS)}."}
    try:
        args = tool.args.model_validate(raw_args or {})
    except ValidationError as e:
        problems = "; ".join(f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors())
        return {"error": f"Invalid arguments for {name}: {problems}"}
    if problem := check(name, args):
        return {"error": problem}
    try:
        return tool.fn(args)
    except Exception as e:  # a bug in a tool must not crash the turn
        return {"error": f"{name} failed: {type(e).__name__}"}