# copyright (c) 2025 Yuuki Furuta

################
# Charactor.py #
################
#
# Charactor.pyではキャラクターの定義に関するプログラムを書いていきます。


from abc import *
from dataclasses import dataclass, field
from typing import Generic, TypeVar, List, Union, Callable
import random
import GameException

C = TypeVar("C")
C_ = TypeVar("C_")
S = TypeVar("S")


# キャラクターの状態管理
@dataclass
class CharactorStatus(Generic[S]):
    hp: float
    attack: float
    defence: float
    speed: float
    queue: List[tuple[S, int]] = field(default_factory=list)

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
    @abstractmethod
    def normalAttack(self, target: C):
        pass

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
    def receveMind(
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
class Charactor(Charactor_, Generic[C]):
    def __init__(self, status, role):

        super().__init__(status, role)

        self.thisTurnSkill: List[tuple[tuple[SkillStatus, Callable], C]] = []
        self.thisTrunGuard: List[tuple[str, float]] = []
        self.skills: List[tuple[SkillStatus, Callable]] = [
            [SkillStatus("normalAttack", "通常攻撃", 0, 0, -1, True), self.normalAttack]
        ]
        self.mindControledQueue: List[tuple[tuple[SkillStatus, Callable], C]] = []

    def noguardmsg(self, damage: float) -> str:
        return f"ダメージを{str(damage)}受けた"

    def guardmsg(self, damage: float) -> str:
        return f"防御でダメージ軽減,ダメージを{damage}受けた"

    def normalAttack(self, target: C):
        target.status.hp -= self.status.attack

    def setGuard(self, guardtype: str, guardpoint: float):
        """
        guardtype:str 軽減方式を選択 - or *
        guardpoint float 軽減方式に基づいて計算される値
        """
        self.thisTrunGuard.append([guardtype, guardpoint])
        pass

    def receveDamage(self, damage: float, penetrate: bool = False) -> None:
        """
        damage:float ダメージ量
        penetrate:bool 防御貫通 通常時false
        """
        if self.thisTrunGuard != [] and penetrate:
            # 貫通の貫通塞ぎ
            thisguard = self.thisTrunGuard.pop(0)
            if thisguard[1] == -1:
                return "強力ガードによる一撃必殺無効化"
        if self.thisTrunGuard != [] and not penetrate:
            # ガードされるとき
            thisguard = self.thisTrunGuard.pop(0)
            # damage = damage - thisguard[1]
            damage = self.decreeceOrPer(thisguard[0], damage, thisguard[1])
            if damage < 0:
                damage = 0
            self.status.hp -= damage
            return self.guardmsg(self.decreeceOrPer(thisguard[0], damage, thisguard[1]))

        self.status.hp -= damage
        return self.noguardmsg(damage)

    def decreeceOrPer(
        self, calculationtype: str, point1: float, point2: float
    ) -> float:
        """
        マイナス : point1 - point2
        スター : point1 * point2
        """
        if calculationtype == "-":
            return point1 - point2
        if calculationtype == "*":
            return point1 * point2

    def receveBuff(self, Buff: CharactorStatus, lifetime: int = -1):
        self.status.addStatus(Buff, lifetime)

    def receveDeBuff(self, DeBuff: CharactorStatus, lifetime: int = -1):
        self.status.addStatus(DeBuff, lifetime)

    def receveMind(self, skill: tuple[SkillStatus, Callable], target: C = None):
        # スキルが選択されていないとき
        if skill == [] and skill == None:
            pass
            # raise GameException.NoselectedSkill()

        skill_status: SkillStatus = skill[0]

        # 対象がいないとき
        if skill_status.target_exist and target == None:
            raise GameException.NotSelectedTarget()
        self.mindControledQueue.append(
            [
                skill,
                target,
            ]
        )

        # INFO:マジシャンの実装でパーセンテージを作る

    def nextTurn(self):
        for i in self.skills:
            i[0].nextTurn()

    def execSkill(self):
        resultmsg = "none"
        if self.mindControledQueue != []:
            resultmsg: list = []
            for i in self.mindControledQueue:
                # TODO:mindcontrolされるときの処理
                # マインドコントロールが成功したとき
                resultmsg.append(i[0][1](i[1]))  # 技を実行
                i[0][0].useSkill()  # 技ステータスに反映

            self.TurnInitialize()  # 初期化

            self.nextTurn()
            return f"minded:{resultmsg}"

        if self.thisTurnSkill == []:
            return ""
            # raise GameException.NoselectedSkill()
        if (
            self.thisTurnSkill[0][0].nowlooktime != 0
            and self.thisTurnSkill[0][0].usetimes == 0
        ):
            raise GameException.DontUseSkill()
        resultmsg = self.thisTurnSkill[0][1](self.thisTurnSkill[1])  # 技を実行
        self.thisTurnSkill[0][0].useSkill()  # 技ステータスに反映
        self.TurnInitialize()  # 初期化
        self.nextTurn()
        return resultmsg

    def TurnInitialize(self):
        self.thisTurnSkill = []  # 初期化
        self.thisTrunGuard = []
        self.mindControledQueue = []

    def setThisTurnSkill(self, skill: tuple[SkillStatus, Callable], target: C = None):
        # リセレクト禁止
        if self.thisTurnSkill != []:
            raise GameException.DontReselect()
        # スキルが選択されていないとき
        if skill == [] and skill == None:
            return
            # raise GameException.NoselectedSkill()

        skill_status: SkillStatus = skill[0]

        # 対象がいないとき
        if skill_status.target_exist and target == None:
            raise GameException.NotSelectedTarget()
        self.thisTurnSkill = [
            skill,
            target,
        ]


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
        self.onehitkillmsg = "一撃必殺が当たった！！"
        self.strongAttackmsg = "強い攻撃がヒット！！"
        self.weakattackmsg = "攻撃を与えた！"
        self.missSkill = "攻撃を外した。。。"
        self.thisTurnSkill = []
        self.skills.append(
            [
                SkillStatus("strongAttack", "強い攻撃", 3, 0, -1, True),
                self.strongAttack,
            ]
        )
        self.skills.append(
            [SkillStatus("normalAttack", "弱い攻撃", 0, 0, -1, True), self.weakAttack],
        )

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

    def weakAttack(self, target: Charactor):
        target.receveDamage(self.status.attack)
        return self.weakattackmsg


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
        self.skills.append(
            [
                SkillStatus(
                    name="buffAndHeal",
                    nickname="バフ＆ヒール",
                    lookturn=1,
                    nowlooktime=0,
                ),
                self.buffHeal,
            ]
        )
        self.skills.append(
            [
                SkillStatus(
                    name="normalHeal", nickname="通常回復", lookturn=0, nowlooktime=0
                ),
                self.normalHeal,
            ]
        )

    # TODO:show my skills
    def buffHeal(self, target: Charactor):

        target.receveBuff(self.powerfulRecoveryPower)
        self.receveDeBuff(self.selfDeBuff, 1)
        pass

    def normalHeal(self, target: Charactor):
        target.receveBuff(CharactorStatus(self.recoveryPower, 0, 0, 0), -1)
        pass


class Guard(Charactor):
    def __init__(self, status: CharactorStatus, role: RoleStatus):
        super().__init__(status, role)
        self.skills.append(
            [SkillStatus("normalGuard", "通常ガード", 1, 0, -1, True), self.normalGuard]
        )
        self.skills.append(
            [SkillStatus("strongGuard", "強力ガード", 0, 0, 1, True), self.strongGuard]
        )

    # TODO:未完成
    def normalGuard(self):

        pass

    def strongGuard(self):
        pass


# TODO:未完成
class Speeder(Charactor):
    def __init__(self, status, role):
        super().__init__(status, role)
        self.skills.append(
            [SkillStatus("doubleAttack", "二回攻撃", 0, 0, -1, True), self.doubleAttack]
        )
        self.skills.append(
            [SkillStatus("stealth", "ステルス", 0, 0, -1, True), self.stealth]
        )

    def doubleAttack(self, target: Charactor):
        # ダブルダメージ
        target.receveDamage(self.status.attack * 2)
        pass

    def stealth(self, target: Charactor):

        pass


class Magician(Charactor):
    def __init__(
        self,
        status,
        role,
        maindCntrolPr: float,
        debuffPower: CharactorStatus,
        debuffLifeTime: int,
        debuffPr: float,  # 自分も被弾する確率
    ):

        super().__init__(status, role)
        self.maindControl = maindCntrolPr
        self.deBuffPower = debuffPower
        self.debuffLifeTime = debuffLifeTime
        self.debuffPr = debuffPr
        self.mindControlmsg = "マインドコントロール"
        self.unmindControle = "マインドコントロールにしっぱい"

        self.skills.append(
            [
                SkillStatus("mindControl", "マインドコントロール", 0, 0, 3, True),
                self.mindControl,
            ]
        )
        self.skills.append([SkillStatus("giveDebuff", "デバフ", 0, 0, -1, True)])

    def showTargetSkill(self, target: Charactor):
        # TODO:ここもっとちゃんと作る
        return target.skills

    def mindControl(
        self,
        target: Charactor,
        targetSkill: tuple[SkillStatus, Callable],
        SkillTarget: Charactor,
    ):
        if random.random() <= self.maindControl:
            target.receveMind(targetSkill, SkillTarget)
            return self.mindControlmsg
        return self.unmindControle

    def giveDebuff(self, target: Charactor):
        target.receveDeBuff(self.deBuffPower, self.debuffLifeTime)
        if random.random() <= self.debuffPr:
            self.receveDeBuff(self.deBuffPower, self.debuffLifeTime)


if __name__ == "__main__":
    m = Magician(
        CharactorStatus(10, 1, 0, 0),
        RoleStatus("aa", "aa"),
        1,
        CharactorStatus(0, -1, 0, 0),
        1,
        0,
    )
    a = Attacker(
        CharactorStatus(hp=10, attack=1, defence=2, speed=3),
        RoleStatus("attacker", "pipi"),
        10,
        15,
        20,
    )
    print(m.mindControl(a, a.skills[0], a))
    a.execSkill()
    print(a.status)
