from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OperationType(Enum):
    BUY = 'BUY'
    SEND = 'SEND'


@dataclass
class Transaction:
    user_id: Optional[str] = None
    spended_currency: Optional[str] = None
    spended_count: Optional[str] = None
    received_currency: Optional[str] = None
    received_count: Optional[str] = None

    def loads(self, raw_data: dict):
        ...

    def set_user_id(self, user_id: str) -> 'Transaction':
        self.user_id = user_id
        return self

    def set_spended_currency(self, val_name: str) -> 'Transaction':
        self.spended_currency = val_name
        return self

    def set_spended_count(self, val_count: str) -> 'Transaction':
        self.spended_count = val_count
        return self

    def set_received_currency(self, val_name: str) -> 'Transaction':
        self.received_currency = val_name
        return self

    def set_received_count(self, val_count: str) -> 'Transaction':
        self.received_count = val_count
        return self


if __name__ == '__main__':
    print('BUY' == OperationType.BUY.value)
