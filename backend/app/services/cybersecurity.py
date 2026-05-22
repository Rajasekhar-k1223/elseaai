import json
from datetime import datetime

class CybersecurityService:
    @staticmethod
    def normalize_syslog_to_ecs(log_line: str) -> dict:
        """
        Parses a raw syslog line and normalizes it into Elastic Common Schema (ECS).
        Example raw syslog: "May 22 15:30:00 server sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2"
        """
        ecs_event = {
            "@timestamp": datetime.utcnow().isoformat(),
            "ecs": {"version": "8.0.0"},
            "event": {"kind": "event", "category": ["authentication"], "type": ["info"]},
            "log": {"original": log_line}
        }
        
        # Simple heuristic parser for SSH failed logins
        if "sshd" in log_line and "Failed password" in log_line:
            ecs_event["event"]["type"] = ["authentication_failure"]
            ecs_event["event"]["outcome"] = "failure"
            ecs_event["user"] = {"name": "root"}
            
            parts = log_line.split("from")
            if len(parts) > 1:
                ip_part = parts[1].strip().split(" ")[0]
                ecs_event["source"] = {"ip": ip_part}
                
        return ecs_event
