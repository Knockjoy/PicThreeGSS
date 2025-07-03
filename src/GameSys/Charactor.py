# copyright (c) 2025 Yuuki Furuta

################
# Charactor.py #
################
#
# Charactor.pyではキャラクターの定義に関するプログラムを書いていきます。


from abc import *
from dataclasses import dataclass, field, asdict
from typing import Generic, TypeVar, List, Union, Callable, Tuple
import random
import GameException
from BattleMsg import BattleMsg, BattleMotion, BattleMotionMsg

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
    mp: float = 0
    grant_mp: float = 0  # mpの付与量
    queue: List[tuple[S, int, bool, str]] = field(
        default_factory=list
    )  # バフ管理キュー
    isdeath: bool = False  # 死亡判定

    def __add__(self, status: S):
        hp = self.hp + status.hp
        attack = self.attack + status.attack
        defence = self.defence + status.defence
        speed = self.speed + status.speed
        return CharactorStatus(hp, attack, defence, speed, self.queue, self.isdeath)

    def __sub__(self, status: S):
        hp = self.hp - status.hp
        attack = self.attack - status.attack
        defence = self.defence - status.defence
        speed = self.speed - status.speed
        return CharactorStatus(hp, attack, defence, speed, self.queue, self.isdeath)

    def __mul__(self, status: S):
        hp = self.hp * status.hp
        attack = self.attack * status.attack
        defence = self.defence * status.defence
        speed = self.speed * status.speed
        return CharactorStatus(hp, attack, defence, speed, self.queue, self.isdeath)

    def __truediv__(self, status: S):
        hp = self.hp / status.hp
        attack = self.attack / status.attack
        defence = self.defence / status.defence
        speed = self.speed / status.speed
        return CharactorStatus(hp, attack, defence, speed, self.queue, self.isdeath)

    def addStatus(
        self,
        status: S,
        lifetime: int = -1,
        overlapping: bool = False,
        resolve_type: str = "+",
    ):
        """
        バフや回復を付与
        lifetime 0:即時付与（解除不可）
        lifetime n:nターン継続
        lifetime -1:永久継続
        overlapping : 毎ターン実行するか
        resolve_type : 計算方法 + or - or * or /
        """
        if (
            resolve_type != "+"
            or resolve_type != "-"
            or resolve_type != "*"
            or resolve_type != "/"
        ):
            # TODO:計算エラー
            pass
        if lifetime == 0:
            self.resolve(resolve_type, status)
        self.resolve(resolve_type, status)
        self.queue.append([status, lifetime-1, overlapping, resolve_type])

    def resolve(self, resolve_type, status: S):
        """
        楽々計算機
        """
        result = CharactorStatus(0, 0, 0, 0)
        if resolve_type == "+":
            result = self.__add__(status)
        if resolve_type == "-":
            result = self.__sub__(status)
        if resolve_type == "*":
            result = self.__mul__(status)
        if resolve_type == "/":
            result = self.__truediv__(status)
        self.hp = result.hp
        self.attack = result.attack
        self.defence = result.defence
        self.speed = result.speed

    def reverse_resolve(self, resolve_type, status: S):
        """
        楽々逆計算機
        """
        result = CharactorStatus(0, 0, 0, 0)
        if resolve_type == "-":
            result = self.__add__(status)
        if resolve_type == "+":
            result = self.__sub__(status)
        if resolve_type == "/":
            result = self.__mul__(status)
        if resolve_type == "*":
            result = self.__truediv__(status)
        self.hp = result.hp
        self.attack = result.attack
        self.defence = result.defence
        self.speed = result.speed

    def checkDie(self) -> bool:
        if self.hp <= 0:
            self.isdeath = True
            self.hp = 0
            return True
        return False

    def removeAddstatus(self, num: int = -1, remove_type: str = "old"):
        """
        現在かかっているバフを解除します。
        解除されるとステータスは元に戻ります。
        num -1 すべて
        remove_type "new"/"old"
        """
        if num == -1 or len(self.queue) <= num:
            for i in self.queue:
                self.reverse_resolve(i[3], i[0])
                self.queue = []
        if remove_type == "new":
            for i in self.queue[num:]:
                self.reverse_resolve(i[3], i[0])
                del self.queue[num:]
        if remove_type == "old":
            for i in self.queue[:num]:
                self.reverse_resolve(i[3], i[0])
                del self.queue[:num]

    def nextTurn(self):
        """
        ターン進行用処理
        バフの効果期間のチェック
        """
        rem = []
        # turn進行
        for i, j in enumerate(self.queue):
            j[1] -= 1
            if j[1] == -2:
                j[1] = -1
            if j[1] == -1:
                rem.append(i)

        for i in sorted(rem, reverse=True):
            effect = self.queue.pop(i)  # 切れた効果を消す
            self.reverse_resolve(effect[3], effect[0])  # 解消

        for i in self.queue:
            # overlapping 有効
            if i[2]:
                self.resolve(i[3], i[0])

    def use_mp(self, point):
        temp_mp = self.mp - point
        # mp不足のとき
        if temp_mp < 0:
            raise GameException.NoMP()
        self.mp = temp_mp

    def add_mp(self, point):
        self.mp += point


@dataclass
class RoleStatus:
    """
    chara_name:管理名
    nickname:プレイヤーに表示されるキャラクターの名前
    # id:内部管理
    """

    chara_name: str
    nickname: str
    id_: str = None
    # lookskill:bool #このターンにskillを選択できるか


@dataclass
class SkillStatus:
    """
    name:関数名,管理名
    nickname:プレイヤーに表示される技の名前
    ex:説明文
    lookturn:次使えるまでのターン数
    nowlookturn:現在の待ちターン数(減数方式)
    usetimes:使用回数(-1は無限)
    target_exist:ターゲットの存在
    """

    name: str
    nickname: str
    ex: str
    lookturn: int = 0
    nowlooktime: int = 0
    usetimes: int = -1
    target_exist: bool = True

    def useSkill(self):
        """
        スキルの使用制限に関する処理の進行
        """
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
        """
        スキルの使用禁止期限に関する処理の進行
        """
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

        self.thisTurnSkill: List[Tuple[Tuple[SkillStatus, Callable], C]] = []
        self.thisTrunGuard: List[tuple[str, float]] = []
        self.skills: List[tuple[SkillStatus, Callable]] = [
            [
                SkillStatus("normalAttack", "通常攻撃", "相手に攻撃を与えます。\n計算式: 相手の防御力-自分のアタック力", 0, 0, -1, True),
                self.normalAttack,
            ]
        ]
        self.mindControledQueue: List[tuple[tuple[SkillStatus, Callable], C]] = []
        self.avoidAct: bool = False
        self.avoidPer: float = 0.5

    def noguardmsg(self, damage: float) -> str:
        return f"{self.role.nickname}はダメージを{str(damage)}受けた。"

    def guardmsg(self, damage: float) -> str:
        return f"防御でダメージ軽減,ダメージを{damage}受けた"

    def diemsg(self, damage: float):
        return f"ダメージを{damage}受けた。hpがゼロになった。"

    def normalAttack(self, target: C) -> List[BattleMsg]:
        result_msg,damagemsg = target.receveDamage(self.status.attack)
        msg = BattleMsg(
            f"{self.role.nickname}の通常攻撃!!\n{result_msg}", BattleMotionMsg("", BattleMotion.none)
        )

        return [msg]

    def setGuard(self, guardtype: str, guardpoint: float):
        """
        guardtype:str 軽減方式を選択 - or *
        guardpoint float 軽減方式に基づいて計算される値
        """
        self.thisTrunGuard.append([guardtype, guardpoint])
        pass

    def receveDamage(self, damage: float, penetrate: bool = False) -> BattleMsg:
        """
        damage:float ダメージ量
        penetrate:bool 防御貫通 通常時false
        """
        receiveDamage =  damage -self.status.defence

        if self.avoidAct:
            self.avoidAct = False
            if random.random() <= self.avoidPer:
                return f"{self.role.chara_name}は攻撃を回避した！",BattleMsg(f"{self.role.chara_name}は攻撃を回避した！",BattleMotionMsg("",BattleMotion.none))
        if penetrate:
            self.status.hp-=damage
            if self.status.hp-damage<0:
                self.status.hp=0
            if self.status.checkDie():
                return self.diemsg(receiveDamage),BattleMsg(
                    self.diemsg(damage=receiveDamage),
                    BattleMotionMsg("", BattleMotion.none),
                )
            return f"{self.role.nickname}は{damage}ダメージ受けた",BattleMsg(f"{self.role.nickname}は{damage}ダメージ受けた",BattleMotionMsg("",BattleMotion.none))
        # if self.thisTrunGuard != [] and penetrate:
        #     # 貫通の貫通塞ぎ
        #     thisguard = self.thisTrunGuard.pop(0)
        #     if thisguard[1] == -1:
        #         return BattleMsg(
        #             "強力ガードによる一撃必殺無効化",
        #             BattleMotionMsg("", BattleMotion.none),
        #         )
        # if self.thisTrunGuard != [] and not penetrate:
        #     # ガードされるとき
        #     thisguard = self.thisTrunGuard.pop(0)
        #     receiveDamage = self.decreeceOrPer(
        #         thisguard[0], receiveDamage, thisguard[1]
        #     )
        #     if receiveDamage < 0:
        #         receiveDamage = 0
        #     self.status.hp -= receiveDamage
        #     # 死亡チェック
        #     if self.status.checkDie():
        #         return BattleMsg(
        #             self.diemsg(damage=receiveDamage),
        #             BattleMotionMsg("", BattleMotion.none),
        #         )
        #     return BattleMsg(
        #         self.guardmsg(
        #             self.decreeceOrPer(thisguard[0], receiveDamage, thisguard[1])
        #         ),
        #         BattleMotionMsg("", BattleMotion.none),
        #     )
        if receiveDamage < 0:
            receiveDamage = 0
        self.status.hp -= receiveDamage
        # 死亡チェック
        if self.status.checkDie():
            return self.diemsg(damage=receiveDamage),BattleMsg(
                self.diemsg(damage=receiveDamage),
                BattleMotionMsg("", BattleMotion.none),
            )
        return self.noguardmsg(damage=receiveDamage),BattleMsg(
            self.noguardmsg(receiveDamage),
            BattleMotionMsg(self.role.id_, BattleMotion.damaged),
        )

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

    def receveBuff(
        self,
        Buff: CharactorStatus,
        lifetime: int = -1,
        overlapping: bool = False,
        resolve_type: str = "+",
    ):
        """
        バフや回復を付与
        lifetime 0:即時付与（解除不可）
        lifetime n:nターン継続
        lifetime -1:永久継続
        overlapping : 毎ターン実行するか
        resolve_type : 計算方法 + or - or * or /
        """
        self.status.addStatus(Buff, lifetime, overlapping, resolve_type)

    def receveDeBuff(
        self,
        Buff: CharactorStatus,
        lifetime: int = -1,
        overlapping: bool = False,
        resolve_type: str = "+",
    ):
        """
        バフや回復を付与
        lifetime 0:即時付与（解除不可）
        lifetime n:nターン継続
        lifetime -1:永久継続
        overlapping : 毎ターン実行するか
        resolve_type : 計算方法 + or - or * or /
        """
        self.status.addStatus(Buff, lifetime, overlapping, resolve_type)

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
        """
        スキルの制限に関する処理やバフの効果処理
        """
        self.avoidAct=False
        for i in self.skills:
            i[0].nextTurn()
        self.status.nextTurn()
        # TODO：メッセージの設定
        return "バフの継続がAになった"

    def execSkill(self):
        """
        技の実施
        """
        # TODO:技メッセージリターン
        resultmsg = "none"
        if self.mindControledQueue != []:
            resultmsg: list = []
            for i in self.mindControledQueue:
                # TODO:mindcontrolされるときの処理
                # マインドコントロールが成功したとき
                resultmsg.append(i[0][1](i[1]))  # 技を実行
                i[0][0].useSkill()  # 技ステータスに反映

            self.TurnInitialize()  # 初期化

            return f"minded:{resultmsg}"

        if self.thisTurnSkill == []:
            return None
            # raise GameException.NoselectedSkill()
        if (
            self.thisTurnSkill[0][0].nowlooktime != 0
            and self.thisTurnSkill[0][0].usetimes == 0
        ):
            raise GameException.DontUseSkill()
        if self.thisTurnSkill[0][0].target_exist:
            target = self.thisTurnSkill[1].role.id_
            resultmsg: List[BattleMsg] = self.thisTurnSkill[0][1](
                self.thisTurnSkill[1]
        )  # 技を実行
        else:
            target=""
            resultmsg:List[BattleMsg]=self.thisTurnSkill[0][1]()
        self.thisTurnSkill[0][0].useSkill()  # 技ステータスに反映
        self.TurnInitialize()  # 初期化
        print("log")
        print([self.role.id_, target, resultmsg])
        return [self.role.id_, target, resultmsg]

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

    def show_my_skill(self):
        return [asdict(i[0]) for i in self.skills]


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
        self.avoidPer = 0.75
        self.skills.extend(
            [
                [
                    SkillStatus(
                        "penetrationAttack",
                        "貫通攻撃",
                        "相手が防御していても、貫通して攻撃できます。",
                        0,
                        0,
                        -1,
                        True,
                    ),
                    self.penetrationAttack,
                ],
                [
                    SkillStatus(
                        "avoidance",
                        "回避",
                        "敵の攻撃を75%の確率で回避できます。",
                        0,
                        0,
                        -1,
                        False,
                    ),
                    self.avoidance,
                ],
                # [
                #     SkillStatus(
                #         name="skill1",
                #         nickname="スキル1",
                #         ex="ex",
                #         lookturn=0,
                #         nowlooktime=0,
                #     ),
                #     self.skill1,
                # ],
            ]
        )

    # def strongAttack(self, target: Charactor) -> None:
    #     """
    #     strongAttack:Attacker,target:Charactor
    #     敵に強い攻撃を与えることができます。
    #     TODO:計算方法の決定
    #     ダメージ=通常攻撃の1.5倍？確率で一撃
    #     """
    #     # 止められるときの処理
    #     if random.random() < self.strongHitAwayPr:  # hitしたとき
    #         if random.random() <= self.oneHitKillProBability:  # 一撃必殺したとき
    #             result=self._oneHitKill(target)
    #             return result
    #         else:
    #             msg=BattleMsg("強い攻撃")
    #             result=target.receveDamage(self.strongPower)
    #             return [msg,result]
    #     return BattleMsg(self.missSkill)

    # def _oneHitKill(self, target: Charactor):
    #     msg=BattleMsg(f"{self.role.nickname}の一撃必殺!!")
    #     result=target.receveDamage(target.status.hp)
    #     return [msg,result]

    # def weakAttack(self, target: Charactor):
    #     result=target.receveDamage(self.status.attack)
    #     return [BattleMsg(self.weakattackmsg),result]
    def skill1(self):
        pass
    def avoidance(self):
        self.avoidAct = True
        return [BattleMotionMsg(f"{self.role.nickname}は身構えている",BattleMotionMsg("",BattleMotion.none))]
        pass

    def penetrationAttack(self, target: Charactor):
        msg = f"{self.role.nickname}の貫通攻撃!!"
        resultmsg,result = target.receveDamage(self.status.attack, True)
        return [BattleMsg(f"{msg}\n{resultmsg}",BattleMotionMsg("",BattleMotion.none))]


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
        self.avoidPer = 0.5
        self.skills.extend(
            [
                [
                    SkillStatus(
                        name="Heal",
                        nickname="回復",
                        ex="選んだ相手を回復させる事ができます。",
                        lookturn=0,
                        nowlooktime=0,
                        usetimes=-1,
                        target_exist=True,
                    ),
                    self.Heal,
                ],
                [
                    SkillStatus(
                        "avoidance",
                        "回避",
                        "50%の確率で回避できます。",
                        0,
                        0,
                        -1,
                        False,
                    ),
                    self.avoidance,
                ],
                [
                    SkillStatus(
                        "debuff",
                        "デバフ",
                        "選択した相手にデバフを2ターン継続する",
                        0,
                        0,
                        -1,
                        True,
                    ),
                    self.debuff,
                ],
            ]
        )

    # TODO:show my skills
    def Heal(self, target: Charactor):
        msg = f"{self.role.chara_name}は{target.role.chara_name}を回復させた。"
        result_,result = target.receveBuff(self.powerfulRecoveryPower)
        return [BattleMsg(f"{msg}\n{result_}",BattleMotionMsg("",BattleMotion.none))]

    def avoidance(self):
        self.avoidAct = True
        return [BattleMotionMsg(f"{self.role.nickname}は身構えている",BattleMotionMsg("",BattleMotion.none))]
        pass

    def debuff(self, target: Charactor):
        msg = f"{self.role.chara_name}は{self.role.chara_name}にデバフをかけた。"
        target.receveDeBuff(CharactorStatus(1, 1, 0, 1), 2, False, "*")
        return [BattleMsg(f"{msg}")]


class Guard(Charactor):
    def __init__(self, status: CharactorStatus, role: RoleStatus):
        super().__init__(status, role)
        self.skills.extend(
            [
                [
                    SkillStatus(
                        "normalGuard",
                        "通常ガード",
                        "選択した相手に2ターンだけ防御を5付与します",
                        0,
                        0,
                        -1,
                        True,
                    ),
                    self.normalGuard,
                ],
                [
                    SkillStatus("everyoneGurd", "防御付与", "防御力を付与します", 0, 0, 1, True),
                    self.everyoneGuard,
                ],
                # [
                #     SkillStatus(
                #         name="skill1",
                #         nickname="スキル1",
                #         ex="ex",
                #         lookturn=0,
                #         nowlooktime=0,
                #     ),
                #     self.skill1,
                # ],
            ]
        )


    def skill1(self):
        return BattleMsg("",BattleMotionMsg("",BattleMotion.none))
    # TODO:未完成
    def normalGuard(self, target: Charactor):
        target.receveBuff(CharactorStatus(0, 0, 5, 0), 2, False, "+")
        if self == target:
            return [
                BattleMsg(
                    f"{self.role.nickname}は身構えている。",
                    BattleMotionMsg(self.role.id_, BattleMotion.gurded),
                )
            ]
        return [
            BattleMsg(
                f"{self.role.nickname}は{target.role.nickname}を守っている",
                BattleMotionMsg(target.role.id_, BattleMotion.gurded),
            )
        ]

    def everyoneGuard(self, target: Charactor):
        target.receveBuff(CharactorStatus(0, 0, 1, 0), 0, False, "+")
        return [BattleMsg(f"{target.role.nickname}は防御力が1上がった", BattleMotionMsg("", BattleMotion.none))]



# # TODO:未完成
# class Speeder(Charactor):
#     def __init__(self, status, role):
#         super().__init__(status, role)
#         self.skills.append(
#             [SkillStatus("doubleAttack", "二回攻撃", 0, 0, -1, True), self.doubleAttack]
#         )
#         self.skills.append(
#             [SkillStatus("stealth", "ステルス", 0, 0, -1, True), self.stealth]
#         )

#     def doubleAttack(self, target: Charactor):
#         # ダブルダメージ
#         target.receveDamage(self.status.attack * 2)
#         pass

#     def stealth(self, target: Charactor):

#         pass


# class Magician(Charactor):
#     def __init__(
#         self,
#         status,
#         role,
#         maindCntrolPr: float,
#         debuffPower: CharactorStatus,
#         debuffLifeTime: int,
#         debuffPr: float,  # 自分も被弾する確率
#     ):

#         super().__init__(status, role)
#         self.maindControl = maindCntrolPr
#         self.deBuffPower = debuffPower
#         self.debuffLifeTime = debuffLifeTime
#         self.debuffPr = debuffPr
#         self.mindControlmsg = "マインドコントロール"
#         self.unmindControle = "マインドコントロールにしっぱい"

#         self.skills.append(
#             [
#                 SkillStatus("mindControl", "マインドコントロール", 0, 0, 3, True),
#                 self.mindControl,
#             ]
#         )
#         self.skills.append([SkillStatus("giveDebuff", "デバフ", 0, 0, -1, True)])

#     def showTargetSkill(self, target: Charactor):
#         # TODO:ここもっとちゃんと作る
#         return target.skills

#     def mindControl(
#         self,
#         target: Charactor,
#         targetSkill: tuple[SkillStatus, Callable],
#         SkillTarget: Charactor,
#     ):
#         if random.random() <= self.maindControl:
#             target.receveMind(targetSkill, SkillTarget)
#             return self.mindControlmsg
#         return self.unmindControle

#     def giveDebuff(self, target: Charactor):
#         target.receveDeBuff(self.deBuffPower, self.debuffLifeTime)
#         if random.random() <= self.debuffPr:
#             self.receveDeBuff(self.deBuffPower, self.debuffLifeTime)


if __name__ == "__main__":
    # m = Magician(
    #     CharactorStatus(10, 1, 0, 0),
    #     RoleStatus("aa", "aa"),
    #     1,
    #     CharactorStatus(0, -1, 0, 0),
    #     1,
    #     0,
    # )
    a = Attacker(
        CharactorStatus(hp=10, attack=1, defence=2, speed=3),
        RoleStatus("attacker", "pipi"),
        10,
        15,
        20,
    )
    # print(m.mindControl(a, a.skills[0], a))
    a.execSkill()
    print(a.status)
