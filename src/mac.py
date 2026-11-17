# 요구사항 05: MAC 연산 (외부 라이브러리 없이 반복문으로)


def mac(pattern, filt):
    """패턴과 필터의 같은 칸끼리 곱해서 모두 더한 점수를 돌려준다."""
    total = 0
    n = len(pattern)
    for i in range(n):          # 줄
        for j in range(n):      # 칸
            total += pattern[i][j] * filt[i][j]   # 곱하고(M) 더해 쌓기(AC)
    return total