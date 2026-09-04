from enum import IntEnum


class EmailChangeRequestEnum(IntEnum):
    
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    EXPIRED = 4
