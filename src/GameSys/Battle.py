# copyright (c) 2025 Yuuki Furuta

################
# Battle.py #
################
#
# Battle.pyではバトル整理の定義に関するプログラムを書いていきます。

from Player import Player
from Charactor import *


class Battle1v1:
    def __init__(self, p1: Player, p2: Player):
        # players
        self.p1 = p1
        self.p2 = p2
        # ターン数
        self.turn = 0

        self._first_check_exception()

    def _first_check_exception(self):
        # initの例外チェック
        # TODO:例外を投げずにreturnし、APIを発行
        pass

    def exec_battle(self):
        self._check_exception()  # TODO:すべてのカードにスキルがセットされているか
        queue = self.sortCardsQueue()
        # TODO:Tryさせる
        for i in queue:
            i[0].execSkill()

    def sortCardsQueue(self):
        allCards: List[Charactor] = list()
        for i in [self.p1, self.p2]:
            allCards.extend(i.cards)  # すべてのカードを格納
        randomBox = list(range(len(allCards)))  # 乱数用
        cardAspeed = list()
        for i in allCards:
            rn = random.choice(randomBox)  # スピードが一致した時用の乱数
            cardAspeed.append([i, i.status.sum().speed, rn])
            randomBox.remove(rn)

        result: List[Union[Charactor, int, int]] = sorted(
            cardAspeed, key=lambda x: (x[1], x[2])
        )

        return result

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
