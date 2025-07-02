import dataclasses
from dataclasses import dataclass,field
import Charactor

@dataclasses.dataclass
class BattleMotion:
    damaged="::damaged::"
    gurded="::guarded::"
    ungurded="::unguarded::"
    healed="::healed::"
    none="::none::"

@dataclasses.dataclass
class BattleMotionMsg:
    """
    target : モーションを実行するターゲットid
    motion : モーション名
    """
    target:str=""
    motion:BattleMotion=BattleMotion.none

@dataclasses.dataclass
class BattleMsg:
    msg:str
    motion:BattleMotionMsg=field(default_factory=BattleMotionMsg("",BattleMotion.none)) 