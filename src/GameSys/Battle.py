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
        self.p1=p1
        self.p2=p2
        self._check_exepcetion()
    
    def _check_exepcetion(self):
        # 例外チェック
        pass