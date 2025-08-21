from pathlib import Path
import yaml
from typing import Dict, List

from .simple_parser import SimpleToscaTemplate
#from toscaparser.tosca_template import ToscaTemplate

from .k8s import (
    deployment_manifest,
    service_manifest,
    pvc_manifest,
    configmap_manifest,
)



def parse_tosca(template_path, profile_paths=None):
    """
    Load a TOSCA service template.
    NOTE: profiles must be listed under 'imports:' in the template YAML itself
    if your tosca-parser version does not support import_definition_file.
    """
    return SimpleToscaTemplate(path=str(template_path))


def convert_node_to_deployment(node, namespace="default") -> Dict:
    """Convert a TOSCA node into a Kubernetes Deployment manifest dict."""
    props = {p.name: p.value for p in node.get_properties()}
    if not node.is_derived_from("tosca.nodes.Container.Application"):
        return None

    return deployment_manifest(
        name=node.name.lower(),
        image=props.get("image"),
        args=props.get("args"),
        env=props.get("env"),
        ports=props.get("ports"),
        replicas=props.get("replicas", 1),
        resources=props.get("resources"),
        volumes=props.get("volumes"),
        namespace=namespace,
    )


def convert_node_to_service(node, namespace="default") -> Dict:
    """Convert a TOSCA node into a Kubernetes Service manifest dict."""
    props = {p.name: p.value for p in node.get_properties()}
    # if it contains both container and ports, it is a service
    if not node.is_derived_from("tosca.nodes.Container.Application"):
        return None
    if not props.get("ports"):
        return None

    return service_manifest(
        name=node.name.lower(),
        ports=props.get("ports"),
        namespace=namespace,
        service_type=props.get("service_type", "ClusterIP"),
    )


def convert_node_to_pvcs(node, namespace="default") -> List[Dict]:
    """Convert a TOSCA node into one or more PVC manifest dicts."""
    props = {p.name: p.value for p in node.get_properties()}
    if not props.get("volumes"):
        return []

    results = []
    for v in props["volumes"]:
        pvc = pvc_manifest(
            name=f"{node.name.lower()}-{v['name']}",
            size=v.get("size", "1Gi"),
            namespace=namespace,
            storage_class=v.get("storageClassName"),
        )
        results.append(pvc)
    return results


def convert_node_to_configmap(node, namespace="default") -> Dict:
    """Convert a TOSCA node into a ConfigMap manifest dict."""
    props = {p.name: p.value for p in node.get_properties()}
    if not props.get("config"):
        return None

    return configmap_manifest(
        name=f"{node.name.lower()}-config",
        data=props["config"],
        namespace=namespace,
    )

