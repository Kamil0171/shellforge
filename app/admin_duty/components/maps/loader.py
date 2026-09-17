from pathlib import Path

from app.admin_duty.components.maps.definition import MapDefinition


def load_map(path: Path) -> MapDefinition:
    return MapDefinition.model_validate_json(path.read_text(encoding="utf-8"))


MODERN_NOC = load_map(Path(__file__).with_name("modern_noc.json"))
DATACENTER_HALL = load_map(Path(__file__).with_name("datacenter_hall.json"))
