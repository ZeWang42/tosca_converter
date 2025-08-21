def deployment_manifest(name, image, args=None, env=None,
                        ports=None, replicas=1, resources=None,
                        volumes=None, namespace="default"):
    containers = [{
        "name": name,
        "image": image,
        "args": args or [],
        "ports": [{"containerPort": p} for p in (ports or [])],
        "env": [{"name": k, "value": str(v)} for k, v in (env or {}).items()],
    }]
    if resources:
        containers[0]["resources"] = resources
    if volumes:
        containers[0]["volumeMounts"] = [
            {"name": v["name"], "mountPath": v.get("mountPath", f"/mnt/{v['name']}")}
            for v in volumes
        ]

    spec = {"containers": containers}
    if volumes:
        spec["volumes"] = [
            {"name": v["name"],
             "persistentVolumeClaim": {"claimName": f"{name}-{v['name']}"}}
            for v in volumes
        ]

    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name}},
                "spec": spec,
            },
        },
    }


def service_manifest(name, ports, namespace="default", service_type="ClusterIP"):
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "selector": {"app": name},
            "ports": [{"port": p, "targetPort": p} for p in ports],
            "type": service_type,
        },
    }


def pvc_manifest(name, size, namespace="default", storage_class=None):
    pvc = {
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": size}},
        },
    }
    if storage_class:
        pvc["spec"]["storageClassName"] = storage_class
    return pvc

def configmap_manifest(name, data, namespace="default"):
    """
    Build a Kubernetes ConfigMap manifest.

    Args:
        name: name of the ConfigMap
        data: dict of key -> value (string data)
        namespace: k8s namespace
    """
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": name, "namespace": namespace},
        "data": {k: str(v) for k, v in data.items()},
    }

