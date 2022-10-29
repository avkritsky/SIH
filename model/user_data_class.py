from dataclasses import dataclass, field
import json
from typing import Union


@dataclass
class UserData:
    user_id: str = None
    user_name: str = None
    default_value: str = None
    total: Union[str, dict] = field(default_factory=lambda: {})
    settings: Union[str, dict] = field(default_factory=lambda: {})

    def from_raw_data(self, raw_data: tuple):
        self.user_id, self.user_name, self.default_value, self.total, self.settings = raw_data[1:]
        self.total = json.loads(self.total)
        self.settings = json.loads(self.settings)
        return self

    @property
    def users_cash(self):
        return '\n'.join((f'{key}:   {val}' for key, val in self.total.items() if key != self.default_value))


if __name__ == '__main__':
    ...

