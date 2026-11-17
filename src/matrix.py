# 요구사항 01: N×N 숫자 표(2차원 리스트)를 다루는 기능


def make_matrix(n, fill=0):
    """n×n 표를 만든다. 모든 칸은 fill 값으로 채운다."""
    # [[0]*n]*n 으로 만들면 모든 줄이 같은 리스트를 가리켜서
    # 한 칸을 바꾸면 모든 줄이 같이 바뀐다. 그래서 줄마다 새로 만든다.
    return [[fill for _ in range(n)] for _ in range(n)]


def get_value(m, i, j):
    """i번째 줄, j번째 칸의 값을 읽는다. (0부터 셈)"""
    return m[i][j]


def set_value(m, i, j, value):
    """i번째 줄, j번째 칸에 값을 넣는다."""
    m[i][j] = value


def is_square(m, n):
    """m이 정확히 n×n 표인지 검사한다."""
    if not isinstance(m, list) or len(m) != n:
        return False
    for row in m:
        if not isinstance(row, list) or len(row) != n:
            return False
    return True


def make_cross(n):
    """n×n 십자가 모양 표를 만든다. 가운데 줄과 가운데 칸이 1."""
    m = make_matrix(n)
    mid = n // 2
    for k in range(n):
        set_value(m, mid, k, 1)
        set_value(m, k, mid, 1)
    return m


def make_x(n):
    """n×n X 모양 표를 만든다. 두 대각선이 1."""
    m = make_matrix(n)
    for k in range(n):
        set_value(m, k, k, 1)
        set_value(m, k, n - 1 - k, 1)
    return m