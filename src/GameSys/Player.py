# copyright (c) 2025 Yuuki Furuta


import Charactor
from abc import *
from dataclasses import dataclass,field
from typing import Generic,TypeVar,List
import random

@dataclass
class Player:
    user_name:str
    cards:List[List[Charactor]]=field(default_factory=list)