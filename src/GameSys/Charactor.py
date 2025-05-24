# copyright (c) 2025 Yuuki Furuta

################
# Charactor.py #
################
# 
#Charactor.pyではキャラクターの定義に関するプログラムを書いていきます。

from abc import *
from dataclasses import dataclass
from typing import Generic,TypeVar
import random

C=TypeVar("C")
C_=TypeVar("C_")
S=TypeVar("S")
# キャラクターの状態管理
@dataclass
class Status(Generic[S]):
    hp:float
    attack:float
    defence:float
    speed:float
    
    def __add__(self,status:S):
        self.hp+=status.hp
        self.attack+=status.attack
        self.defence+=status.defence
        self.speed+=status.speed
    def __sub__(self,status:S):
        self.hp-=status.hp
        self.attack-=status.attack
        self.defence-=status.defence
        self.speed-=status.speed
    def addStatus(self,status:S):
        self.hp+=status.hp
        self.attack+=status.attack
        self.defence+=status.defence
        self.speed+=status.speed
    def subStatus(self,status:S):
        self.hp-=status.hp
        self.attack-=status.attack
        self.defence-=status.defence
        self.speed-=status.speed


# charactor の設定
# Charactor_は抽象基底クラスなのであるべき機能の設定のみが行われます。
class Charactor_(ABC,Generic[C_]):
    def __init__(
        self,
        status:Status,
        ):
        self.status:Status=status
    # 通常攻撃
    def nomalAttack(self,target:C_,):
        target.status.hp-=self.status.attack
    # ダメージを受けたとき
    @abstractmethod
    def receveDamage(self,damage:float):pass
    
    # デバフを受けたとき
    @abstractmethod
    def receveDeBuff(self,DeBuff:Status):pass
    
    # バフを受けたとき
    @abstractmethod
    def receveBuff(self,Buff:Status):pass
    
    # マインドコントロールを受けたとき
    @abstractmethod
    def receveMaind(self,):pass
    

# Charactorの実装
class Charactor(Charactor_):
    def __init__(self, status):
        super().__init__(status)
    
    def nomalAttack(self, target:C):
        return super().nomalAttack(target)
    
    def receveDamage(self, damage:float)->None:
        self.status.hp-=damage
    
    def receveBuff(self, Buff:Status):
        self.status+=Buff
    
    def receveDeBuff(self, DeBuff):
        self.status-=DeBuff
    
    def receveMaind(self):
        # TODO:どうやって技してするか
        pass
    

# Attackerの設定
class Attacker(Charactor):
    def __init__(self,
                status:Status,
                storngPower:float,
                strongPitchAwayPr:float,
                oneHitKillPr:float,):
        """
        status:Status
        - アタッカー自身の状態を示します。
        strongPower:float
        - strongAttackの増加量または増倍量
        strongPitchAwayPr
        - strongAttackの外れる確率
        oneHitKillPr
        - strongAttackで一撃必殺が発生する確率
        
        """
        super().__init__(status)
        self.strongPower=self.status.attack+storngPower
        self.strongPitchAwayPr=strongPitchAwayPr
        self.oneHitKillProBability=oneHitKillPr
    
    def strongAttack(self,target:Charactor)->None:
        """
        strongAttack:Attacker,target:Charactor
        敵に強い攻撃を与えることができます。
        TODO:計算方法の決定
        ダメージ=通常攻撃の1.5倍？確率で一撃
        """
        if random.random()>self.strongPitchAwayPr: # hitしたとき
            if random.random()<=self.oneHitKillProBability: # 一撃必殺したとき
                self.oneHitKill(target)
                return None
            else:
                target.receveDamage(self.strongPower)
                return None
        return None
    
    def oneHitKill(self,target:Charactor):
        target.receveDamage(target.status.hp)