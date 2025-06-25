# copyright (c) 2025 Yuuki Furuta

################
# Player.py #
################
#
# Player.pyではユーザー保持の定義に関するプログラムを書いていきます。

from Charactor import Charactor
from abc import *
from dataclasses import dataclass, field
from typing import Generic, TypeVar, List
import random
import GameException


@dataclass
class Player:
    user_name: str
    cards: List[Charactor] = field(default_factory=list)
    mp:int=0
    mp_inheritance:bool=False
    
    def __post_init__(self):
        self.sync_mp()
    
    def sync_mp(self):
        if self.mp_inheritance:
            for i in self.cards:
                i.status.mp=self.mp
    
    def use_mp(self,point):
        
        temp_mp=self.mp-point
        if(temp_mp<0):
            return GameException.NoMP()
        self.mp=temp_mp
        self.sync_mp()
    
    def add_mp(self,point):
        self.mp+=point
        self.sync_mp()