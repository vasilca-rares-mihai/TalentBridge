from enum import Enum


class GenderEnum(str, Enum):
    Male = 'Male'
    Female = 'Female'
    Other = 'Other'

class PositionsEnum(str, Enum):
    goalkeeper = 'goalkeeper'
    center_back = "center_back"
    full_back = "full_back"
    defensive_midfielder = "defensive_midfielder"
    midfielder = "midfielder"
    attacking_midfielder  = "attacking_midfielder"
    winger = "winger"
    attacker = "attacker"

class WeakFootEnum(str, Enum):
    left = 'left'
    right = 'right'

class RolesEnum(str, Enum):
    admin = 'admin'
    athlete = 'athlete'
    football_club = 'football_club'