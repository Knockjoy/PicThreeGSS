import sqlite3
from PIL import Image
import datetime

imgDB = "/root/picthree/PicThreeGSS/src/GameServer/db/SketchCardBattle.db"
# TODO:画像返却関数の実装
# TODO:バトルマッチングの実装
# TODO:バトルの進行

def wakeupDB():
    db = sqlite3.connect(imgDB)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS images(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            imgid INTEGER NOT NULL
        )
        """
    )
    db.commit()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        )
        """
    )
    db.commit()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cards(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            cardid INTEGER NOT NULL,
            imgid INTEGER NOT NULL,
            charaname TEXT NOT NULL,
            typeid TEXT NOT NULL,
            hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defence INTEGER NOT NUll,
            speed INTEGER NOT NULL
        )
        """
    )
    db.commit()

    db.close()
    pass


def createCard(userId, ImgId, charaName, role, hp, attack, defence, speed):

    db = sqlite3.connect(imgDB)
    cursor = db.cursor()
    tdate = datetime.date.today()
    dataid = tdate.strftime("%Y%m%d%H%M%S")
    try:
        cursor.execute("SELECT COUNT(id) from cards")
        res=cursor.fetchall()
        num=res[0][0]
        cursor.execute(
            "INSERT INTO cards(userid,cardid,imgid,charaname,typeid,hp,attack,defence,speed) VALUES (?,?,?,?,?,?,?,?,?)",
            (userId, dataid + str(num),ImgId,charaName,role,hp,attack,defence,speed),
        )
        db.commit()
        
        return dataid + str(num)
    except sqlite3.Error as e:
        print(f"An Error occurred {e}")
        db.rollback()
    db.close()


async def saveImg(userId, img: Image):

    db = sqlite3.connect(imgDB)
    cursor = db.cursor()
    tdate = datetime.date.today()
    dataid = tdate.strftime("%Y%m%d%H%M%S")
    try:
        cursor.execute("SELECT COUNT(id) from images")
        res = cursor.fetchall()
        num = res[0][0] + 1
        cursor.execute(
            "INSERT INTO images(userid,imgid) VALUES (?,?)",
            (userId, dataid + str(num)),
        )
        db.commit()
        # TODO:path管理
        img.save(f"/root/picthree/PicThreeGSS/src/GameServer/db/imgs/sketch{dataid}{num}.png")

        return dataid + str(num)
    except sqlite3.Error as e:
        print(f"An Error occurred {e}")
        db.rollback()

    db.close()
    pass


if __name__ == "__main__":
    wakeupDB()
    # saveImg(-1, "6e9f01")
