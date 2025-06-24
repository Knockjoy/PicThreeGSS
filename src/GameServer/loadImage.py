import sqlite3
from PIL import Image
import datetime

imgDB = "/root/picthree/PicThreeGSS/src/GameServer/db/SketchCardBattle.db"

def timeid():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = now.strftime('%Y%m%d%H%M%S')
    return f"{d}"
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
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
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


def createCard(userId, ImgId, charaName, role, hp, attack, defence, speed)->str:
    """
    カード情報をDBに保存した後、cardidを発行します(str)
    """
    db = sqlite3.connect(imgDB)
    cursor = db.cursor()
    dataid = timeid()
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
    dataid = timeid()
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

def saveUserName(userid,username):
    db = sqlite3.connect(imgDB)
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users(userid,username) VALUES (?,?)",(userid,username))
        db.commit()
    except sqlite3.Error as e:
        print(e)
        db.rollback()
    db.close()
    pass

def getCard(cardid):
    db = sqlite3.connect(imgDB)
    cursor = db.cursor()
    try:
        cursor.execute(f"SELECT * FROM cards where cardid='{cardid}'")
        res=cursor.fetchall()
        res=res[0]
        # cardname=res[4]
        return res
    except sqlite3.Error as e:
        print(e)
    db.close()

def getUser(userid):
    db = sqlite3.connect(imgDB)
    cursor = db.cursor()
    try:
        cursor.execute(f"SELECT * FROM users where userid='{userid}'")
        res=cursor.fetchall()
        res=res[0]
        # cardname=res[4]
        return res
    except sqlite3.Error as e:
        print(e)
    db.close()


if __name__ == "__main__":
    wakeupDB()
    # getCard("20250623000000138")
    # saveImg(-1, "6e9f01")
