# copyright (c) 2025 Yuuki Furuta

class GamesysError(Exception):
    pass

class NotSelectedTarget(Exception):
    def __str__(self):
        return "ターゲットが選択されていません。"

class NoSkillCredit(Exception):
    def __str__(self):
        return "使用制限超過です。"