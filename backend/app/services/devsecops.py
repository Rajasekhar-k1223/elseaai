import yaml
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any, Optional

class KubernetesContainer(BaseModel):
    name: str
    image: str
    securityContext: Optional[Dict[str, Any]] = None

class KubernetesSpec(BaseModel):
    containers: list[KubernetesContainer]

class KubernetesTemplate(BaseModel):
    spec: KubernetesSpec

class KubernetesDeployment(BaseModel):
    apiVersion: str
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any]  # Allow nested structure, validate templates

class DevSecOpsService:
    @staticmethod
    def validate_k8s_yaml(yaml_content: str) -> dict:
        """
        Parses K8s YAML and checks for common security misconfigurations using Pydantic.
        """
        try:
            parsed = yaml.safe_load(yaml_content)
            if parsed.get("kind") != "Deployment":
                return {"valid": True, "message": "Not a Deployment, skipping strict validation."}
            
            # Simple validation check
            deployment = KubernetesDeployment(**parsed)
            containers = deployment.spec.get("template", {}).get("spec", {}).get("containers", [])
            
            issues = []
            for container in containers:
                sec_ctx = container.get("securityContext", {})
                if sec_ctx.get("privileged") is True:
                    issues.append(f"Container {container['name']} is running as privileged.")
                if sec_ctx.get("allowPrivilegeEscalation") is not False:
                    issues.append(f"Container {container['name']} does not explicitly disable privilege escalation.")
                    
            if issues:
                return {"valid": False, "issues": issues}
            return {"valid": True, "issues": []}
            
        except ValidationError as e:
            return {"valid": False, "error": "YAML Schema validation failed", "details": str(e)}
        except yaml.YAMLError as e:
            return {"valid": False, "error": "Invalid YAML structure", "details": str(e)}
