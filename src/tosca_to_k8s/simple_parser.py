import yaml
from pathlib import Path


class SimpleProperty:
    """Mimics a ToscaProperty with .name and .value."""

    def __init__(self, name, value):
        self.name = name
        self.value = value


class SimpleNode:
    """Mimics a ToscaNodeTemplate."""

    def __init__(self, name, typename, props, type_defs=None):
        self.name = name
        self.type = typename or ""
        self._type_defs = type_defs or {}
        self._properties = self._merge_with_defaults(props)

    def _merge_with_defaults(self, props: dict):
        merged = {}
        # load defaults from type definition if present
        if self.type in self._type_defs:
            tdef = self._type_defs[self.type]
            defaults = {
                k: v.get("default")
                for k, v in tdef.get("properties", {}).items()
                if isinstance(v, dict) and "default" in v
            }
            merged.update(defaults)
        # then overlay explicit values
        merged.update(props or {})
        return merged

    def get_properties(self):
        """Return properties in tosca-parser style."""
        return [SimpleProperty(k, v) for k, v in self._properties.items()]

    def is_derived_from(self, typename: str) -> bool:
        """Heuristic: pretend inheritance based on type string."""
        t = self.type.lower()
        return typename.lower() in t or "container" in t or "oci" in t or "docker" in t


class SimpleToscaTemplate:
    """Mimics ToscaTemplate with .nodetemplates."""

    def __init__(self, path):
        path = Path(path)
        # type_defs stores all node types
        self.type_defs = {}

        text = path.read_text()
        doc = yaml.safe_load(text)

        # 1. Load imports (profiles) to expand node definitions
        imports = []
        if "imports" in doc:
            imports = doc["imports"]
        elif "service_template" in doc and "imports" in doc["service_template"]:
            imports = doc["service_template"]["imports"]

        for imp in imports:
            if isinstance(imp, str):
                profile_path = (path.parent / imp).resolve()
            elif isinstance(imp, dict) and "file" in imp:
                profile_path = (path.parent / imp["file"]).resolve()
            else:
                continue

            profile = yaml.safe_load(Path(profile_path).read_text())
            if "node_types" in profile:
                self.type_defs.update(profile["node_types"])

        # 2. Load the template itself
        if "service_template" in doc:
            template = doc["service_template"]
        else:
            template = doc.get("topology_template", {})

        nodes = template.get("node_templates", {})
        self.nodetemplates = []
        # TODO: it should parse each node, but not all in one
        for nodename, nodedef in nodes.items():
            typename = nodedef.get("type", "")
            props = nodedef.get("properties", {})
            node = SimpleNode(nodename, typename, props, self.type_defs)
            #print("00000000000000")
            #print(nodes)
            self.nodetemplates.append(node)

