import re
import json

class HealthcareService:
    @staticmethod
    def mask_phi(text: str) -> str:
        """
        Regex-based simple PII/PHI masker for enterprise depth demonstration.
        In full production, this integrates with Microsoft Presidio or AWS Comprehend Medical.
        """
        # Mask SSN
        text = re.compile(r'\b\d{3}-\d{2}-\d{4}\b').sub('[SSN_REDACTED]', text)
        # Mask Emails
        text = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b').sub('[EMAIL_REDACTED]', text)
        # Mask Dates of Birth (DOB) - simple MM/DD/YYYY format
        text = re.compile(r'\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b').sub('[DOB_REDACTED]', text)
        return text

    @staticmethod
    def parse_fhir_resource(json_string: str) -> dict:
        """
        Parses and flattens a standard FHIR resource (e.g., Patient, Observation).
        """
        try:
            resource = json.loads(json_string)
            resource_type = resource.get("resourceType", "Unknown")
            flattened = {"type": resource_type}
            
            if resource_type == "Patient":
                name_list = resource.get("name", [{}])
                flattened["name"] = f"{name_list[0].get('given', [''])[0]} {name_list[0].get('family', '')}"
                flattened["gender"] = resource.get("gender")
                flattened["id"] = resource.get("id")
            elif resource_type == "Observation":
                flattened["code"] = resource.get("code", {}).get("text")
                flattened["value"] = resource.get("valueQuantity", {}).get("value")
                flattened["unit"] = resource.get("valueQuantity", {}).get("unit")
            
            return flattened
        except Exception as e:
            return {"error": f"Invalid FHIR resource: {str(e)}"}
