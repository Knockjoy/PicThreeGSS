# copyright (c) 2025 Yuuki Furuta

################
# Battle.py #
################
# 
#Battle.pyではバトル整理の定義に関するプログラムを書いていきます。

import Charactor
import Player

class Battle:
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
    
    def _check_exception(self):
        # TODO:例外を投げずにreturnし、APIを発行
        pass