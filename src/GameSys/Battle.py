# copyright (c) 2025 Yuuki Furuta

################
# Battle.py #
################
#
# Battle.pyではバトル整理の定義に関するプログラムを書いていきます。

from Player import Player
from Charactor import *
from typing import Tuple, List
import copy
import dataclasses


class Battle1v1:
    def __init__(self, p1: Player, p2: Player):
        # players
        self.p1 = p1
        self.p2 = p2
        # ターン数
        self.turn = 0

        # 一ターンに付与するMP量
        self.grant_mp = 0

        self._first_check_exception()

    def _first_check_exception(self):
        # initの例外チェック
        pass

    def exec_battle(self):
        # self._check_exception()  # TODO:すべてのカードにスキルがセットされているか
        queue = self.sortCardsQueue()
        # TODO:Tryさせる
        thisturnHistory = []
        for i in queue:
            
            res= i.execSkill()
            if (res==None) :continue
            executor=res[0]
            target=res[1]
            msg=res[2]
            if msg == None:
                continue

            thisturnHistory.append(
                {
                    "status": "skill",
                    "msg": msg,
                    "executor":executor,
                    "target":target,
                    "cards": {
                        "player1": [
                            {
                                "charactorStatus": dataclasses.asdict(i.status),
                                "skillStatus": [
                                    dataclasses.asdict(j[0]) for j in i.skills
                                ],
                                "rolestatus": dataclasses.asdict(i.role),
                            }
                            for i in self.p1.cards
                        ],
                        "player2": [
                            {
                                "charactorStatus": dataclasses.asdict(i.status),
                                "skillStatus": [
                                    dataclasses.asdict(j[0]) for j in i.skills
                                ],
                                "rolestatus": dataclasses.asdict(i.role),
                            }
                            for i in self.p2.cards
                        ],
                    },
                }
            )
            result = self.check_finish()

            if result != None:
                break

        if result == None:
            thisturnHistory.append({"status":"::nextturn::","msg":"Next turn"})
        # Next Turn
        # TODO:MP付与,付与メッセージ
        for i in [self.p1, self.p2]:
            if i.mp_inheritance:
                i.add_mp(self.grant_mp)
            else:
                for j in i.cards:
                    j.status.add_mp(j.status.grant_mp)

        for i in queue:
            if result != None:
                break
            msg = i.nextTurn()
            if msg == None:
                continue
            thisturnHistory.append(
                {
                    "status": "nextTurn",
                    "msg": msg,
                    "cards": {
                        "player1": [
                            {
                                "charactorStatus": dataclasses.asdict(i.status),
                                "skillStatus": [
                                    dataclasses.asdict(j[0]) for j in i.skills
                                ],
                            }
                            for i in self.p1.cards
                        ],
                        "player2": [
                            {
                                "charactorStatus": dataclasses.asdict(i.status),
                                "skillStatus": [
                                    dataclasses.asdict(j[0]) for j in i.skills
                                ],
                            }
                            for i in self.p2.cards
                        ],
                    },
                }
            )

        if result != None:
            return {"game_status": "finish", "msg": result, "history": thisturnHistory}
        return {"game_status": "continue", "history": thisturnHistory}

    def check_finish(self):
        p1flag = False
        p2flag = False
        if []==list(filter(lambda x:x.status.isdeath==False,self.p1.cards)):
            p1flag = True
        if []==list(filter(lambda x:x.status.isdeath==False,self.p2.cards)):
            p2flag = True

        if p1flag and p2flag:
            # 引き分け
            return {"game_finish": "draw"}
        if not p1flag and p2flag:
            # p1勝ち
            return {"game_finish": "win", "player": "p2"}
        if not p2flag and p1flag:
            # p2勝ち
            return {"game_finish": "win", "player": "p1"}
        return None

    def sortCardsQueue(self) -> List[Charactor]:
        allCards: List[Charactor] = list()
        for i in [self.p1, self.p2]:
            allCards.extend(i.cards)  # すべてのカードを格納
        randomBox = list(range(len(allCards)))  # 乱数用
        cardAspeed = list()
        for i in allCards:
            rn = random.choice(randomBox)  # スピードが一致した時用の乱数
            cardAspeed.append([i, i.status.speed, rn])
            randomBox.remove(rn)

        result: List[Tuple[Charactor, int, int]] = sorted(
            cardAspeed, key=lambda x: (x[1], x[2])
        )

        return [i[0] for i in result]

    def _check_exception(self):
        # TODO:例外を投げずにreturnし、APIを発行
        pass


if __name__ == "__main__":

    my1 = Attacker(
        CharactorStatus(hp=10, attack=1, defence=2, speed=3),
        RoleStatus("attacker", "pipi"),
        storngPower=10,
        strongHitPr=15,
        oneHitKillPr=20,
    )
    my2 = Healer(
        CharactorStatus(hp=10, attack=0, defence=10, speed=10),
        RoleStatus("healer", "qiqi"),
        10,
        CharactorStatus(hp=10, attack=10, defence=10, speed=10),
        CharactorStatus(-10, 0, 0, 0),
    )
    my = Player("yuki", [my1, my2])
    you1 = Attacker(
        CharactorStatus(hp=10, attack=1, defence=2, speed=3),
        RoleStatus("attacker", "pipi"),
        10,
        15,
        20,
    )
    you2 = Healer(
        CharactorStatus(hp=10, attack=0, defence=10, speed=10),
        RoleStatus("healer", "qiqi"),
        10,
        CharactorStatus(hp=10, attack=10, defence=10, speed=10),
        CharactorStatus(hp=-10, attack=0, defence=0, speed=0),
    )
    you = Player("yuki", [you1, you2])
    bt = Battle1v1(my, you)
    my1.setThisTurnSkill(my1.skills[0], you1)
    my2.setThisTurnSkill(my2.skills[1], my1)
    you1.setThisTurnSkill(my1.skills[0], my1)
    you2.setThisTurnSkill(my2.skills[1], you1)
    bt.exec_battle()
    print(bt.p1.cards[0].status)
