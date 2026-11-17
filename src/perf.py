# 요구사항 07: 성능 분석 (MAC 계산 시간 측정)

import time

from src.mac import mac

REPEAT = 10   # 크기마다 10번 재서 평균을 낸다


def measure_mac_ms(pattern, filt):
    """MAC 계산만 10번 재서 평균 시간(ms)을 돌려준다. 입력·출력은 재지 않는다."""
    elapsed = 0.0
    for _ in range(REPEAT):
        start = time.perf_counter()
        mac(pattern, filt)                      # 이 사이에는 MAC 계산만!
        elapsed += time.perf_counter() - start
    return elapsed / REPEAT * 1000              # 초 -> 밀리초(ms)


def print_perf_table(rows):
    """rows = [(N, 평균 시간 ms), ...] 를 표로 출력한다."""
    print("크기(NxN)    평균 시간(ms)    연산 횟수(N^2)")
    print("-" * 44)
    for n, ms in rows:
        size = "%dx%d" % (n, n)
        print("%-12s %-16.6f %d" % (size, ms, n * n))