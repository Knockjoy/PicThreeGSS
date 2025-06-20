import sqlite3

imgDB = "PicThreeGSS/src/GameServer/db/images.db"


def wakeup():
    db = sqlite3.connect(imgDB)
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS images(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            username TEXT NOT NULL,
            imgid INTEGER NOT NULL
        )
        """
    )

    db.close()
    pass


def saveImg(userId, userName, img):
    db = sqlite3.connect(imgDB)

    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO images(userid,username,imgid) VALUES (?,?,?)",(-1,"yuki","6e9f01"))
        db.commit()
    except sqlite3.Error as e:
        print(f"An Error occurred {e}")
        db.rollback()

    db.close()
    pass


if __name__=="__main__":
    wakeup()