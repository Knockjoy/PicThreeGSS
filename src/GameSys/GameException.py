# copyright (c) 2025 Yuuki Furuta

class GamesysError(Exception):
    pass

class NotSelectedTarget(Exception):
    def __str__(self):
        return "ターゲットが選択されていません。"

class NoSkillCredit(Exception):
    def __str__(self):
        return "使用制限超過です。"

class NoselectedSkill(Exception):
    def __str__(self):
        return "スキルが選択されていません"

class DontUseSkill(Exception):
    def __str__(self):
        return "スキルが使用できません。"

class DontReselect(Exception):
    def __str__(self):
        return "技のリセレクトはできません。"

class NoMP(Exception):
    def __str__(self):
        return "MPが足りません"