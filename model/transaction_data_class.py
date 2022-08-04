from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    BUY = 'BUY'
    SEND = 'SEND'


@dataclass
class Transaction:
    user_id: Optional[str] = None
    operation_type: Optional[TransactionType] = None
    spended_currency: Optional[str] = None
    spended_count: Optional[int] = None
    received_currency: Optional[str] = None
    received_count: Optional[int] = None

    def loads(self, raw_data: dict):
        ...


if __name__ == '__main__':
    print('BUY' == TransactionType.BUY.value)
