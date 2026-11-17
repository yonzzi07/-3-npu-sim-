# 요구사항 02: 모드 1 - 사용자가 3x3을 직접 입력

from src.mac import mac
from src.judge import judge, UNDECIDED, EPSILON
from src.perf import measure_mac_ms, print_perf_table

SIZE = 3
ERR_COUNT = "입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요."
ERR_NUMBER = "입력 형식 오류: 숫자만 입력하세요. (예: 0 1 0)"


def parse_number(text):
    """'1'은 정수 1로, '0.5'는 소수 0.5로 바꾼다. 숫자가 아니면 ValueError."""
    try:
        return int(text)
    except ValueError:
        return float(text)


def read_matrix(name):
    """3줄을 입력받아 3x3 표를 돌려준다. 잘못 입력하면 처음부터 다시 받는다."""
    print("%s (3줄 입력, 공백 구분)" % name)
    while True:
        rows = []
        ok = True
        for i in range(SIZE):
            parts = input("  %d줄: " % (i + 1)).split()
            if len(parts) != SIZE:          # 숫자 개수가 3개가 아님 (빈 줄 포함)
                print(ERR_COUNT)
                ok = False
                break
            try:
                rows.append([parse_number(p) for p in parts])
            except ValueError:              # 숫자가 아닌 글자가 있음
                print(ERR_NUMBER)
                ok = False
                break
        if ok:
            return rows
        print("%s를 처음부터 다시 입력하세요." % name)


def run_mode1():
    print()
    print("#" + "-" * 40)
    print("# [1] 필터 입력")
    print("#" + "-" * 40)
    filter_a = read_matrix("필터 A")
    filter_b = read_matrix("필터 B")
    print("필터 A, B 저장 완료")

    print()
    print("#" + "-" * 40)
    print("# [2] 패턴 입력")
    print("#" + "-" * 40)
    pattern = read_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    ms = measure_mac_ms(pattern, filter_a)
    result = judge(score_a, score_b, "A", "B")

    print()
    print("#" + "-" * 40)
    print("# [3] MAC 결과")
    print("#" + "-" * 40)
    print("A 점수:", score_a)
    print("B 점수:", score_b)
    print("연산 시간(평균/10회): %.6f ms" % ms)
    if result == UNDECIDED:
        print("판정: 판정 불가 (|A-B| < %g)" % EPSILON)
    else:
        print("판정:", result)

    print()
    print("#" + "-" * 40)
    print("# [4] 성능 분석 (평균/10회)")
    print("#" + "-" * 40)
    print_perf_table([(SIZE, ms)])