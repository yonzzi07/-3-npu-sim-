# 요구사항 04: 라벨 통일(정규화), 요구사항 06: 허용오차(epsilon) 판정

EPSILON = 1e-9   # 두 점수 차이가 이보다 작으면 같은 점수로 본다

CROSS = "Cross"
X = "X"
UNDECIDED = "UNDECIDED"


def normalize_label(raw):
    """'+', 'cross' -> Cross / 'x' -> X / 그 외 -> None (모르는 라벨)"""
    key = str(raw).strip().lower()
    if key in ("+", "cross"):
        return CROSS
    if key == "x":
        return X
    return None


def judge(score_a, score_b, name_a, name_b):
    """두 점수를 비교해서 더 큰 쪽 이름을 돌려준다. 거의 같으면 UNDECIDED."""
    if abs(score_a - score_b) < EPSILON:
        return UNDECIDED
    if score_a > score_b:
        return name_a
    return name_b