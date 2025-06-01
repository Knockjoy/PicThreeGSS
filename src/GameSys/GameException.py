# copyright (c) 2025 Yuuki Furuta

class GamesysError(Exception):
    pass

class NotSelectedTarget(Exception):
    def __str__(self):
        return "ターゲットが選択されていません。"


