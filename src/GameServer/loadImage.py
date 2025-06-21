import sqlite3
from PIL import Image
import datetime

imgDB = "src/GameServer/db/SketchCardBattle.db"


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
            cardid TEXT NOT NULL,
            imgid INTEGER NOT NULL,
            charactername TEXT NOT NULL,
            typeid INTEGER NOT NULL,
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


async def saveImg(userId,img: Image):

    db = sqlite3.connect(imgDB)

    cursor = db.cursor()
    try:
        tdate = datetime.date.today()
        cursor.execute("SELECT COUNT(id) from images")
        res=cursor.fetchall()
        print(res[0][0])
        
        num = res[0][0] + 1
        img.save(f"src/GameServer/db/imgs/sketch{tdate.strftime("%y%m%d")}{num}.png")
        cursor.execute(
            "INSERT INTO images(userid,imgid) VALUES (?,?)",
            (userId,  tdate.strftime("%y%m%d") + str(num)),
        )
        db.commit()
        return  tdate.strftime("%y%m%d") + str(num)
    except sqlite3.Error as e:
        print(f"An Error occurred {e}")
        db.rollback()

    db.close()
    pass


if __name__ == "__main__":
    wakeupDB()
    saveImg(-1, "6e9f01")
