from pathlib import Path
from tosca_to_k8s.converter import (
    parse_tosca,
    convert_node_to_deployment,
    convert_node_to_service,
    convert_node_to_pvcs,
    convert_node_to_configmap,
)
import yaml

tpl = parse_tosca(Path("stressng-ec2.yaml"))

for node in tpl.nodetemplates:
    dep = convert_node_to_deployment(node, namespace="demo")
    if dep:
        print("---\n" + yaml.safe_dump(dep))

    svc = convert_node_to_service(node, namespace="demo")
    if svc:
        print("---\n" + yaml.safe_dump(svc))

    for pvc in convert_node_to_pvcs(node, namespace="demo"):
        print("---\n" + yaml.safe_dump(pvc))

    cm = convert_node_to_configmap(node, namespace="demo")
    if cm:
        print("---\n" + yaml.safe_dump(cm))

