# copyright (c) 2025 Yuuki Furuta

################
# Battle.py #
################
# 
#Battle.pyではバトル整理の定義に関するプログラムを書いていきます。

from Player import Player
from Charactor import *

class Battle1v1:
    def __init__(self,p1:Player,p2:Player):
        # players
        self.p1=p1
        self.p2=p2
        # ターン数
        self.turn=0
        
        self._first_check_exception()
    
    def _first_check_exception(self):
        # initの例外チェック
        # TODO:例外を投げずにreturnし、APIを発行
        pass
    
    def exec_battle(self):
        self._check_exception()
        pass
    
    def use_skill(self):
        
        pass
    
    def nextturn(self):
        # カードの待ちターン処理
        for i in self.p1.cards:
            i.nextTrun()
        for j in self.p2.cards:
            j.nextTrun()
        pass
    
    def _check_exception(self):
        # TODO:例外を投げずにreturnし、APIを発行
        pass


if __name__ == "__main__":
    my1=Attacker(CharactorStatus(10,1,2,3),RoleStatus("attacker","pipi"),10,15,20)
    my2=Healer(CharactorStatus(10,0,10,10),RoleStatus("healer","qiqi"),10,CharactorStatus(10,10,10,10),CharactorStatus(-10,0,0,0))
    my=Player("yuki",[my1,my2])
    you1=Attacker(CharactorStatus(10,1,2,3),RoleStatus("attacker","pipi"),10,15,20)
    you2=Healer(CharactorStatus(10,0,10,10),RoleStatus("healer","qiqi"),10,CharactorStatus(10,10,10,10),CharactorStatus(-10,0,0,0))
    you=Player("yuki",[you1,you2])
    bt=Battle1v1(my,you)