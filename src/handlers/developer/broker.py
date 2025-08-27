from typing import Dict

from src.handlers.service.broker import BrokerSystemHandler


class DeveloperBrokerHandler(BrokerSystemHandler):
    def __init__(self):
        super().__init__()

    def get_signature(self) -> Dict[str, str]:
        return {
            "type": "developer",
            "name": ""
        }

    def get_triggers(self) -> Dict[str, str]:
        return {
            "hub": "dev_hub",
            "handler": "dev_broker"
        }
