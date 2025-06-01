# copyright (c) 2025 Yuuki Furuta

################
# Charactor.py #
################
#
# Charactor.pyではキャラクターの定義に関するプログラムを書いていきます。

from abc import *
from dataclasses import dataclass, field
from typing import Generic, TypeVar, List, Union,Callable
import random
import GameException

C = TypeVar("C")
C_ = TypeVar("C_")
S = TypeVar("S")

# TODO:技の発動タイミング


# キャラクターの状態管理
@dataclass
class CharactorStatus(Generic[S]):
    hp: float
    attack: float
    defence: float
    speed: float
    queue: List[Union[S, int]] = field(default_factory=list)

    def __add__(self, status: S):
        self.hp += status.hp
        self.attack += status.attack
        self.defence += status.defence
        self.speed += status.speed
        return self

    # def __add__(self,status:S,lifetime:int=-1):
    #     self.queue.append(status,lifetime)
    # def __sub__(self,status:S,lifetime:int=-1):
    #     self.queue.append(status,lifetime)
    def addStatus(self, status: S, lifetime: int = -1):
        self.queue.append([status, lifetime])

    def sum(self) -> S:
        result = CharactorStatus(0, 0, 0, 0)
        for i in self.queue:
            result += i[0]
        result += self
        return result

    def nextTurn(self):
        rem = []
        for i in range(len(self.queue) - 1):
            n = self.queue[i]
            if n - 1 == -1:  # 0から-1になった場合
                rem.append(i)
        for i in sorted(rem, reverse=True):
            self.queue.pop(i)  # 切れた効果を消す


@dataclass
class RoleStatus:
    """
    chara_name:管理名
    nickname:プレイヤーに表示されるキャラクターの名前
    # id:内部管理
    """

    chara_name: str
    nickname: str
    # id:int
    # lookskill:bool #このターンにskillを選択できるか


@dataclass
class SkillStatus:
    """
    name:関数名,管理名
    nickname:プレイヤーに表示される技の名前
    lookturn:次使えるまでのターン数
    nowlookturn:現在の待ちターン数(減数方式)
    usetimes:使用回数(-1は無限)
    target_exist:ターゲットの存在
    """

    name: str
    nickname: str
    lookturn: int = 0
    nowlooktime: int = 0
    usetimes: int = -1
    target_exist: bool = True

    def useSkill(self):
        n = self.usetimes - 1
        # 使用制限
        if n == -1:
            self.nowlooktime = 0
            raise GameException.NoSkillCredit()
        # 無限回
        elif n == -2:
            self.nowlooktime = -1
        # 減数
        else:
            self.nowlooktime = n

        self.nowlooktime += self.lookturn  # 待機ターンを作成

    def nextTurn(self):
        n = self.nowlooktime - 1
        if n == -1:
            self.nowlooktime = 0
        elif n == -2:
            self.nowlooktime = -1
        else:
            self.nowlooktime = n


# charactor の設定
# Charactor_は抽象基底クラスなのであるべき機能の設定のみが行われます。
class Charactor_(ABC, Generic[C_]):
    def __init__(self, status: CharactorStatus, Role: RoleStatus):
        self.status: CharactorStatus = status
        self.role = Role

    # 通常攻撃
    def nomalAttack(
        self,
        target: C_,
    ):
        target.status.hp -= self.status.attack

    # ダメージを受けたとき
    @abstractmethod
    def receveDamage(self, damage: float):
        pass

    # デバフを受けたとき
    @abstractmethod
    def receveDeBuff(self, DeBuff: CharactorStatus):
        pass

    # バフを受けたとき
    @abstractmethod
    def receveBuff(self, Buff: CharactorStatus):
        pass

    # マインドコントロールを受けたとき
    @abstractmethod
    def receveMaind(
        self,
    ):
        pass

    @abstractmethod
    def nextTurn(
        self,
    ):
        pass

    @abstractmethod
    def setThisTurnSkill(self, skill):
        pass
    
    @abstractmethod
    def execSkill(self):
        pass


# Charactorの実装
class Charactor(Charactor_):
    def __init__(self, status, role):
        super().__init__(status, role)

    def nomalAttack(self, target: C):
        return super().nomalAttack(target)

    def receveDamage(self, damage: float) -> None:
        self.status.hp -= damage

    def receveBuff(self, Buff: CharactorStatus, lifetime: int = -1):
        self.status.addStatus(Buff, lifetime)

    def receveDeBuff(self, DeBuff: CharactorStatus, lifetime: int = -1):
        self.status.addStatus(DeBuff, lifetime)

    def receveMaind(self):
        # TODO:どうやって技を実装するか
        pass


# Attackerの設定
class Attacker(Charactor):
    def __init__(
        self,
        status: CharactorStatus,
        role: RoleStatus,
        storngPower: float,
        strongHitPr: float,
        oneHitKillPr: float,
    ):
        """
        status:Status
        - アタッカー自身の状態を示します。

        strongPower:float
        - strongAttackの増加量または増倍量

        strongPitchAwayPr
        - strongAttackのあたる確率

        oneHitKillPr
        - strongAttackで一撃必殺が発生する確率

        """
        super().__init__(status, role)
        self.strongPower = self.status.attack + storngPower
        self.strongHitAwayPr = strongHitPr
        self.oneHitKillProBability = oneHitKillPr
        self.onehitkillmsg="一撃必殺が当たった！！"
        self.strongAttackmsg="強い攻撃がヒット！！"
        self.weakattackmsg="攻撃を与えた！"
        self.missSkill="攻撃を外した。。。"
        self.skills:List[Union[SkillStatus,Callable]] = [
            [
                SkillStatus("strongAttack", "強い攻撃", 3, 0, -1, True),
                self.strongAttack,
            ],
            [SkillStatus("normalAttack", "弱い攻撃", 0, 0, -1, True), self.weakAttack],
        ]
        # TODO:スキルの待ちターンについて

    def strongAttack(self, target: Charactor) -> None:
        """
        strongAttack:Attacker,target:Charactor
        敵に強い攻撃を与えることができます。
        TODO:計算方法の決定
        ダメージ=通常攻撃の1.5倍？確率で一撃
        """
        # 止められるときの処理
        if random.random() < self.strongHitAwayPr:  # hitしたとき
            if random.random() <= self.oneHitKillProBability:  # 一撃必殺したとき
                self._oneHitKill(target)
                return self.onehitkillmsg
            else:
                target.receveDamage(self.strongPower)
                return self.strongAttackmsg
        return self.missSkill

    def _oneHitKill(self, target: Charactor):
        target.receveDamage(target.status.hp)
        return None

    def weakAttack(self, target:Charactor):
        # TODO:弱い攻撃の実装
        target.receveDamage(self.status.attack)
        return self.weakattackmsg

    def nextTurn(self):
        for i in self.skills[0]:
            i[0].nextTrun()

    def execSkill(self):
        # TODO:self.thisTurnSkillが存在するか
        # TODO:技ステータスに例外はないか
        self.thisTurnSkill[0][1](self.thisTurnSkill[1]) # 技を実行
        self.thisTurnSkill[0][0].useSkill() # 技ステータスに反映
    
    def setThisTurnSkill(self, skill, target=None):
        # TODO:例外チェック
        skill_status: SkillStatus = skill[0]
        if skill_status.target_exist and target == None:
            raise GameException.NotSelectedTarget()  # 対象がいないとき
        self.thisTurnSkill:List[Union[List[SkillStatus,Callable],Charactor]] = [skill, target]


class Healer(Charactor):
    def __init__(
        self,
        status: CharactorStatus,
        role: RoleStatus,
        recoveryPower: float,
        powerfulBuff: CharactorStatus,
        selfDeBuff: CharactorStatus,
    ):
        """
        status:キャラクターの状態
        role:キャラクターに関する情報
        recoveryPower:通常回復力
        powerfulBuff:回復力およびバフ
        selfDeBuff:バフ＆ヒールを実行した際に自身が負うデバフ
        """

        super().__init__(status, role)
        self.recoveryPower: float = recoveryPower
        self.powerfulRecoveryPower = powerfulBuff
        self.selfDeBuff = selfDeBuff
        self.thisTurnSkill = []
        self.skills = [
            [
                SkillStatus(
                    name="buffAndHeal",
                    nickname="バフ＆ヒール",
                    lookturn=1,
                    nowlooktime=0,
                ),
                self.buffHeal,
            ],
            [
                SkillStatus(
                    name="normalHeal", nickname="通常回復", lookturn=0, nowlooktime=0
                ),
                self.normalHeal,
            ],
        ]

    # TODO:show my skills
    def buffHeal(self, target: Charactor):

        target.receveBuff(self.powerfulRecoveryPower)
        self.receveDeBuff(self.selfDeBuff, 1)
        pass

    def normalHeal(self, target: Charactor):
        target.receveBuff(CharactorStatus(self.recoveryPower, 0, 0, 0), -1)
        pass

    def nextTurn(self):
        for i in self.skills[0]:
            i[0].nextTrun()

    def setThisTurnSkill(self, skill, target=None):
        # TODO:例外チェック
        skill_status: SkillStatus = skill[0]
        if skill_status.target_exist and target == None:
            raise GameException.NotSelectedTarget()  # 対象がいないとき
        self.thisTurnSkill = [skill, target]
    
    def execSkill(self):
        # TODO:self.thisTurnSkillが存在するか
        # TODO:技ステータスに例外はないか
        self.thisTurnSkill[0][1](self.thisTurnSkill[1]) # 技を実行
        self.thisTurnSkill[0][0].useSkill() # 技ステータスに反映


if __name__ == "__main__":
    # SkillStatus("aaa", "bbb", 0, 0, -1, True).nextTurn()
    cs = CharactorStatus(10, 10, 10, 10)
    q1 = CharactorStatus(20, 20, 20, 20)
    q2 = CharactorStatus(20, 20, -5, 20)
    cs.addStatus(q1, -1)
    cs.addStatus(q2, -1)
    print(cs)
    print(cs.sum())
