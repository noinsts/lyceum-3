from typing import Dict

from src.handlers.service.broker import BrokerSystemHandler


class AdminBroker(BrokerSystemHandler):
    def get_signature(self) -> Dict[str, str]:
        return {
            "type": "admin",
            "name": ""
        }

    def get_triggers(self) -> Dict[str, str]:
        return {
            "hub": "back_to_admin_hub",
            "handler": "admin_broker"
        }
