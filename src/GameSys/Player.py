# copyright (c) 2025 Yuuki Furuta

################
# Player.py #
################
#
# Player.pyではユーザー保持の定義に関するプログラムを書いていきます。

import Charactor
from abc import *
from dataclasses import dataclass, field
from typing import Generic, TypeVar, List
import random


@dataclass
class Player:
    user_name: str
    cards: List[Charactor] = field(default_factory=list)
