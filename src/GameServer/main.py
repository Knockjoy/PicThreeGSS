# copyright (c) 2025 Yuuki Furuta

import sys
import json
import base64
from io import BytesIO
import asyncio
from typing import List, Union, Tuple
from dataclasses import dataclass, asdict

from PIL import Image
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect

# add import path
sys.path.append("/root/picthree/PicThreeGSS/src/GameServer")
from loadImage import *

sys.path.append("/root/picthree/PicThreeAI/src/AI")
sys.path.append("/root/picthree/PicThreeGSS/src/GameSys")
from Charactor import *
from Battle import *
import RoleAnalyze
import StatusAnalyze


# TODO:バトルの進行(ターン実行のみ)


@dataclass
class BTPlayer:
    userid: str
    socket: WebSocket
    playerinstance: Player
    cardids: List[str]
    thisTurn: bool


@dataclass
class BTManager:
    battleid: str
    battle: Battle1v1
    player1: BTPlayer
    player2: BTPlayer


connectionID: int = 0
cardid: int = 0
battleid = 0
all_battle: List[BTManager] = []
path = "/root/picthree/PicThreeGSS/src/GameServer/db/imgs/"

# TODO:typing 変更　union(,)＝＞type[userid]に置き換え
# List[Tuple(Union[int,str],WebSocket,List[Union[int,str]])]
waiting_users = []


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:19009", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "Access-Control-Allow-Origin",
    ],
)

# TODO:List[Battle]
BattleMatchs: List = []


def createid():
    global connectionID
    connectionID += 1
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, "JST")
    now = datetime.datetime.now(JST)
    d = now.strftime("%Y%m%d%H%M%S")
    id = f"{d}{connectionID}"
    return id


def createBattleid():
    global battleid
    battleid += 1
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, "JST")
    now = datetime.datetime.now(JST)
    d = now.strftime("%Y%m%d%H%M%S")
    id = f"{d}{battleid}"
    return id


def CardPacking(cardids):
    res = []
    resinstance = []
    for i in cardids:
        card = getCard(i)
        # id,userid,cardid,imgid,cardname,role,hp,attack,defence,speed
        temp_userid = card[1]
        temp_cardid = card[2]
        temp_imgid = card[3]
        temp_cardname = card[4]
        temp_hp = card[6]
        user = getUser(temp_userid)
        # id,userid,username
        temp_username = user[2]
        imgpath = path + f"sketch{temp_imgid}.png"

        # システム用インスタンス
        cstatus = CharactorStatus(
            hp=card[6], attack=card[7], defence=card[8], speed=card[9]
        )
        temp_chara = None
        if card[5] == "Attack":
            temp_chara = Attacker(
                cstatus,
                RoleStatus("attacker", temp_cardname,id_=temp_cardid),
                storngPower=10,
                strongHitPr=15,
                oneHitKillPr=20,
            )
            pass
        if card[5] == "Guard":
            # TODO:未完成に注意
            temp_chara = Guard(cstatus, RoleStatus("guard", temp_cardname,id_=temp_cardid))
            pass
        if card[5] == "Healer":
            temp_chara = Healer(
                cstatus,
                RoleStatus("healer", temp_cardname,id_=temp_cardid),
                10,
                CharactorStatus(hp=10, attack=10, defence=10, speed=10),
                CharactorStatus(-10, 0, 0, 0),
            )
        # if card[5] == "Speeder":
        #     # TODO:未完成に注意
        #     temp_chara = Speeder(
        #         cstatus,
        #         RoleStatus("speeder", temp_cardname,id_=temp_cardid),
        #     )
        #     pass
        # if card[5] == "Magician":
        #     temp_chara = Magician(
        #         cstatus,
        #         RoleStatus("magician", temp_cardname,id_=temp_cardid),
        #         0.5,
        #         CharactorStatus(0, -1, 0, 0),  # TODO:ここの設定をちゃんと作る
        #         1,
        #         0.3,
        #     )
        resinstance.append(temp_chara)
        res.append(
            {
                "userid": temp_userid,
                "username": temp_username,
                "img": createImageURL(imgpath),
                "cardid": temp_cardid,
                "charaname": temp_cardname,
                "hp": temp_hp,
            }
        )

    return res, temp_username, resinstance


async def matching_loop():
    # マッチング処理＆バトル初期化
    print("wake up matching sys")
    while True:
        if len(waiting_users) >= 2:
            print("init bt")
            temp_battleid = createBattleid()
            # waiting_users -> userid websocket [cardsid]
            user1 = waiting_users.pop(0)
            user2 = waiting_users.pop(0)
            user1_cards, user1name, user1instance = CardPacking(user1[2])
            user2_cards, user2name, user2instance = CardPacking(user2[2])

            user1Player = Player(user1name, user1instance)
            user2Player = Player(user2name, user2instance)
            bt = Battle1v1(user1Player, user2Player)
            all_battle.append(
                BTManager(
                    battleid=temp_battleid,
                    battle=bt,
                    player1=BTPlayer(
                        userid=user1[0],
                        socket=user1[1],
                        playerinstance=user1Player,
                        cardids=user1[2],
                        thisTurn=False,
                    ),
                    player2=BTPlayer(
                        userid=user2[0],
                        socket=user2[1],
                        playerinstance=user2Player,
                        cardids=user2[2],
                        thisTurn=False,
                    ),
                )
            )
            print(all_battle)
            print(user1[1])
            # asyncio.sleep(1)
            await user1[1].send_json(
                {
                    "status": "match_found",
                    "battleid": temp_battleid,
                    "mycards": user1_cards,
                    "opponetname": user2name,
                    "opponet": user2[0],
                    "opponetcards": user2_cards,
                }
            )
            await user2[1].send_json(
                {
                    "status": "match_found",
                    "battleid": temp_battleid,
                    "mycards": user2_cards,
                    "opponetname": user1name,
                    "opponet": user2[0],
                    "opponetcards": user1_cards,
                }
            )
        temp_battleid = None
        user1 = None
        user1name = None
        user1_cards = None
        user1instance = None
        user1Player = None
        user2 = None
        user2name = None
        user2_cards = None
        user2instance = None
        user2Player = None

        await asyncio.sleep(1)


def findBattle(battleid) -> List[BTManager]:
    battle = [item for item in all_battle if item.battleid == battleid]
    return battle


def setSkill(userid, battleid, cardid, skillnum, targetcardid):
    # battleidからバトルを絞る
    # useridからplayerインスタンスを見つける
    battle = findBattle(battleid=battleid)
    if(battle==[]):
        # TODO:error処理
        return "error"
    battle=battle[0]
    
    player = ""

    # 自分自身がどちらか
    for i in [battle.player1,battle.player2]:
        if i.userid == userid:
            player = i

    assert(player!="")
    # ターゲットはどれか
    for i in [battle.player1,battle.player2]:
        if targetcardid in i.cardids:
            targetchara = i.cardids.index(targetcardid)
            targetchara = i.playerinstance.cards[targetchara]


    mychara = player.playerinstance.cards[player.cardids.index(cardid)]
    mychara.setThisTurnSkill(mychara.skills[int(skillnum)], targetchara)
    print(mychara.thisTurnSkill)
    pass


def showSkill(userid, battleid, cardid):
    # TODO:スキル開示を作る
    pass


async def checkBattle(battleid):
    # TODO:バトルを実行できるか
    # TODO:バトル終了
    battle = findBattle(battleid)
    if battle==[]:
        # TODO:none battle
        return ""
    if not (battle.player1.thisTurn and battle.player2.thisTurn):
        # TODO:実行できなかったとき
        for i in [battle.player1, battle.player2]:
            await i.socket.send_json(
                {"status": "exec_battle", "battleid": battleid, "msg": "faild"}
            )
        return
    result = battle.battle.exec_battle()
    # TODO:技の実行順ログ
    for i in [battle.player1, battle.player2]:
        await i.socket.send_json(
            {"status": "exec_battle", "battleid": battleid, "msg": "success"}
        )
    return


def createImageURL(imgpath):
    with open(imgpath, "rb") as f:
        data = base64.b64encode(f.read())
    return "data:image/jpeg;base64," + data.decode("utf-8")


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(matching_loop())


@app.get("/")
async def root():
    return {"message": "Can't use this page"}


@app.get("/home")
async def home():
    return "<div>sample</div>"


@app.post("/uplaodfile")
async def uploadfile():

    pass


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            status = data["status"]
            print(data)
            if status == "::connect::":
                await websocket.send_json(
                    {"status": "firstConnect", "userid": createid()}
                )
            if status == "usersetup":
                userid = data["userid"]
                saveUserName(userid, data["nickname"])
                pass
            if status == "createCard":
                sketch = Image.open(
                    BytesIO(base64.b64decode(data["sketch"].split(",")[1]))
                )
                userid = data["userID"]
                charaname = data["charaname"]
                imgid = await saveImg(userid, sketch)
                imgpath = path + f"sketch{imgid}.png"
                role = RoleAnalyze.analyze(imgpath)
                skills=None
                temp_c=CharactorStatus(0,0,0,0)
                temp_r=RoleStatus("","","")
                if role == "Attacker":
                    skills=Attacker(temp_c,temp_r,0,0,0).show_my_skill()
                if role == "Guard":
                    skills=Guard(temp_c,temp_r).show_my_skill()
                if role == "Healer":
                    skills=Healer(temp_c,temp_r,0,temp_c,temp_c).show_my_skill()
                # if role == "speeder":
                #     role = 3
                # if role == "magician":
                #     role = 4

                del temp_c
                del temp_r

                hp, attack, defence, speed = StatusAnalyze.analyze(imgpath)
                hp *= 1000
                attack *= 100
                defence *= 100
                speed *= 100
                hp = int(hp)
                attack = int(attack)
                defence = int(defence)
                speed = int(speed)

                cardid = createCard(
                    userid, imgid, charaname, role, hp, attack, defence, speed
                )
                print((userid, imgid, charaname, role, hp, attack, defence, speed))
                # await websocket.send_json({"status":"test","data":role})
                await websocket.send_json(
                    {
                        "status": "cardCreated",
                        "careateStatus": "success",
                        "cardid": cardid,
                        "charaname": charaname,
                        "sketch": data["sketch"],
                        "cardstatus": {
                            "role": role,
                            "hp": hp,
                            "attack": attack,
                            "defence": defence,
                            "speed": speed,
                            "skills":skills
                        },
                    }
                )
            if status == "battle_in":
                print(all_battle)
                # ユーザーid、websocket,試合で使うカードid
                waiting_users.append((userid, websocket, data["cardids"]))
                await websocket.send_json({"status": "matching_wait"})
            if status == "get_card":
                await websocket.send_json(
                    {
                        "status": "res_get_card",
                        "cardid": data["cardid"],
                        "carddata": getCard(data["cardid"]),
                    }
                )
            if status == "set_skill":
                setSkill(
                    data["userid"],
                    data["battleid"],
                    data["cardid"],
                    data["skillnum"],
                    data["targetcardid"],
                )
                checkBattle(data["battleid"])
                pass
            # await websocket.send_text(f"your msg is {data}")
    except WebSocketDisconnect:
        websocket.close()


if __name__ == "__main__":
    print(RoleAnalyze.analyze("/root/picthree/PicThreeAI/Apple.png"))
    wakeupDB()
    # loop=asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(matching_loop())
    uvicorn.run("main:app", host="0.0.0.0", port=19004, lifespan="on", reload=True)
    # loop.close()
    pass
