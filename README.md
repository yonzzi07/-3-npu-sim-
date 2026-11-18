
# Mini NPU Simulator

숫자 격자(패턴)와 필터를 같은 칸끼리 곱해 모두 더하는 MAC 연산으로 십자가(Cross)와 X를 판별하는 Python 콘솔 프로그램입니다.

## 목차

1. 핵심 개념
2. 실행 방법 (main.py)
3. 구현 요약 (matrix.py, mac.py, judge.py, perf.py)
4. 실행 확인: 모드 1 (mode_input.py)
5. 실행 확인: 모드 2와 오류 처리 (mode_json.py)
6. 결과 리포트 (FAIL 원인 분석, 시간 복잡도 분석)
7. 파일 구조와 data.json 구조

## 1. 핵심 개념

- **MAC(Multiply-Accumulate)**: 두 숫자 표의 같은 위치 값을 곱하고(Multiply) 그 결과를 계속 더하는(Accumulate) 연산입니다. 결과(점수)가 클수록 패턴이 그 필터와 닮았다는 뜻이며, 두 필터 중 점수가 높은 쪽으로 판정합니다.
- **AI에서 중요한 이유**: AI 모델은 이미지 한 장을 처리할 때 이 곱셈·덧셈을 수억 번 반복합니다. 그래서 MAC 연산을 동시에 대량으로 처리하는 전용 칩(NPU)이 쓰이며, 이 프로그램은 그 계산을 Python 반복문으로 흉내 낸 시뮬레이터입니다.

## 2. 실행 방법

- Python 3.8 이상에서 실행합니다(Python 3.14, Windows에서 실행 확인). 외부 라이브러리는 설치하지 않아도 됩니다.
- 프로젝트 폴더에서 아래 명령을 입력합니다.

```text
python main.py
```

- 모드 선택 화면에서 `1`을 입력하면 사용자 입력 모드입니다. 3x3 필터 A, B와 패턴을 한 줄씩 공백으로 구분해 입력합니다(예: `0 1 0`).
- `2`를 입력하면 data.json 분석 모드입니다. data.json은 main.py와 같은 폴더에 있어야 합니다. main.py가 자기 위치를 기준으로 data.json을 찾기 때문에, 다른 폴더에서 실행해도 같은 파일을 읽습니다.
- 1, 2 말고 다른 값을 입력하면 "1 또는 2를 입력하세요."를 출력하고 다시 묻습니다.

### main.py (시작 파일, 모드 선택)

```python
# Mini NPU Simulator 시작 파일 (요구사항 09: 실행 흐름)

import os

from src.mode_input import run_mode1

# data.json은 main.py와 같은 폴더에 있어야 한다
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def main():
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    while True:
        choice = input("선택: ").strip()
        if choice in ("1", "2"):
            break
        print("1 또는 2를 입력하세요.")
    if choice == "1":
        run_mode1()
    else:
        from src.mode_json import run_mode2   # 모드 2 파일은 Step 5에서 만든다
        run_mode2(DATA_PATH)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("프로그램을 종료합니다.")
```

### 실행 화면 (모드 선택)

```text
=== Mini NPU Simulator ===
[모드 선택]
1. 사용자 입력 (3x3)
2. data.json 분석
선택: 1
```

## 3. 구현 요약

### 3-1. N×N 표 다루기 (matrix.py)

- 2차원 리스트로 N×N 표를 만들고, 칸 읽기·쓰기, 정사각형 크기 검사를 합니다.
- `[[0]*n]*n`처럼 만들면 모든 줄이 같은 리스트를 가리키는 문제가 있어서, 줄마다 새 리스트를 만듭니다.
- `make_cross(n)`, `make_x(n)`은 성능 측정용 십자가·X 패턴을 만듭니다(3x3은 data.json에 없어서 이 함수로 만듭니다).

```python
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
```

### 3-2. MAC 연산 (mac.py)

- 이중 for문으로 같은 위치의 값끼리 곱해 `total`에 누적합니다. NumPy 등 외부 라이브러리는 쓰지 않았습니다.
- 바깥 반복이 N번, 안쪽 반복이 N번이므로 곱셈·덧셈은 N×N = N²번 일어납니다.

```python
# 요구사항 05: MAC 연산 (외부 라이브러리 없이 반복문으로)


def mac(pattern, filt):
    """패턴과 필터의 같은 칸끼리 곱해서 모두 더한 점수를 돌려준다."""
    total = 0
    n = len(pattern)
    for i in range(n):          # 줄
        for j in range(n):      # 칸
            total += pattern[i][j] * filt[i][j]   # 곱하고(M) 더해 쌓기(AC)
    return total
```

### 3-3. 라벨 정규화와 동점 처리 정책 (judge.py)

- **라벨 정규화**: `normalize_label`이 앞뒤 공백을 지우고 소문자로 바꾼 뒤, `+`와 `cross`는 `Cross`로, `x`는 `X`로 바꿉니다. 그 밖의 값은 `None`을 돌려주고, 해당 케이스는 FAIL로 처리합니다. 화면 출력과 PASS/FAIL 비교는 모두 표준 라벨(Cross, X)로 합니다.
- **동점 처리 정책(epsilon)**: 두 점수 차이의 절댓값이 `1e-9`보다 작으면 같은 점수로 봅니다. 모드 2에서는 `UNDECIDED`, 모드 1에서는 "판정 불가"로 출력합니다. 소수 계산은 아주 작은 오차가 생기기 때문에 `==`로 비교하지 않습니다.

```python
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
```

### 3-4. 시간 측정 (perf.py)

- `time.perf_counter`로 `mac()` 호출 구간만 10회 재서 평균(ms)을 냅니다. 입력, 출력, 파일 읽기 시간은 포함하지 않습니다.
- 표에는 크기, 평균 시간, 연산 횟수(N²)를 함께 출력합니다.

```python
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
```

### 3-5. 예외 처리 (mode_json.py, 5장 참고)

- 파일 없음과 JSON 손상은 안내 후 종료합니다.
- 키 규칙 위반, 크기 불일치, 알 수 없는 라벨은 해당 케이스만 FAIL로 기록하고 다음 케이스를 계속 처리합니다.
- 실패 원인은 데이터/스키마, 로직, 수치 비교 세 가지로 나눠 출력합니다.

## 4. 실행 확인: 모드 1 (사용자 입력)

### mode_input.py

- 한 줄에 숫자가 3개가 아니거나 빈 줄이면 "입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요."를 출력합니다.
- 숫자가 아닌 글자가 있으면 "입력 형식 오류: 숫자만 입력하세요. (예: 0 1 0)"을 출력합니다.
- 오류가 나면 프로그램을 끝내지 않고 해당 필터(또는 패턴)를 처음부터 다시 입력받습니다.
- 점수, 연산 시간, 판정, 3x3 성능 표를 출력합니다.

```python
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
```

### 시험 결과 요약

| 시험 | 필터 A | 필터 B | 패턴 | 결과 |
|---|---|---|---|---|
| 기본 | 십자가 | X | X | A 1, B 5, 판정 B |
| 반대 | 십자가 | X | 십자가 | A 5, B 1, 판정 A |
| 소수 동점 | 모든 칸 0.1 | 가운데만 0.9 | 모든 칸 1 | A 0.8999999999999999, B 0.9, 판정 불가 |
| 잘못 입력 | `1 0`, `1 a 0` 입력 | - | - | 각각 다른 안내 문구 출력 후 재입력 |

### 시험 1: 기본 (패턴이 X 모양)

입력한 값

```text
선택: 1
필터 A: 0 1 0 / 1 1 1 / 0 1 0   (십자가)
필터 B: 1 0 1 / 0 1 0 / 1 0 1   (X)
패턴:   1 0 1 / 0 1 0 / 1 0 1   (X)
```

실행 화면

```text
#----------------------------------------
# [1] 필터 입력
#----------------------------------------
필터 A (3줄 입력, 공백 구분)
  1줄: 0 1 0                
  2줄: 1 1 1
  3줄: 0 1 0
필터 B (3줄 입력, 공백 구분)
  1줄: 1 0 1
  2줄: 0 1 0
  3줄: 1 0 1
필터 A, B 저장 완료

#----------------------------------------
# [2] 패턴 입력
#----------------------------------------
패턴 (3줄 입력, 공백 구분)
  1줄: 1 0 1 
  2줄: 0 1 0
  3줄: 1 0 1

#----------------------------------------
# [3] MAC 결과
#----------------------------------------
A 점수: 1
B 점수: 5
연산 시간(평균/10회): 0.002290 ms
판정: B

#----------------------------------------
# [4] 성능 분석 (평균/10회)
#----------------------------------------
크기(NxN)    평균 시간(ms)    연산 횟수(N^2)
--------------------------------------------
3x3          0.002290         9
```

### 시험 2: 반대 (패턴이 십자가 모양)

입력한 값

```text
선택: 1
필터 A: 0 1 0 / 1 1 1 / 0 1 0   (십자가)
필터 B: 1 0 1 / 0 1 0 / 1 0 1   (X)
패턴:   0 1 0 / 1 1 1 / 0 1 0   (십자가)
```

실행 화면

```text
#----------------------------------------
# [1] 필터 입력
#----------------------------------------
필터 A (3줄 입력, 공백 구분)
  1줄: 0 1 0
  2줄: 1 1 1
  3줄: 0 1 0
필터 B (3줄 입력, 공백 구분)
  1줄: 1 0 1
  2줄: 0 1 0
  3줄: 1 0 1
필터 A, B 저장 완료

#----------------------------------------
# [2] 패턴 입력
#----------------------------------------
패턴 (3줄 입력, 공백 구분)
  1줄: 0 1 0
  2줄: 1 1 1
  3줄: 0 1 0    

#----------------------------------------
# [3] MAC 결과
#----------------------------------------
A 점수: 5
B 점수: 1
연산 시간(평균/10회): 0.001640 ms
판정: A

#----------------------------------------
# [4] 성능 분석 (평균/10회)
#----------------------------------------
크기(NxN)    평균 시간(ms)    연산 횟수(N^2)
--------------------------------------------
3x3          0.001640         9
```

### 시험 3: 소수 동점 (epsilon 확인)

입력한 값

```text
선택: 1
필터 A: 0.1 0.1 0.1 / 0.1 0.1 0.1 / 0.1 0.1 0.1
필터 B: 0 0 0 / 0 0.9 0 / 0 0 0
패턴:   1 1 1 / 1 1 1 / 1 1 1
```

실행 화면

```text
#----------------------------------------
# [1] 필터 입력
#----------------------------------------
필터 A (3줄 입력, 공백 구분)
  1줄: 0.1 0.1 0.1
  2줄: 0.1 0.1 0.1
  3줄: 0.1 0.1 0.1
필터 B (3줄 입력, 공백 구분)
  1줄: 0 0 0
  2줄: 0 0.9 0
  3줄: 0 0 0
필터 A, B 저장 완료

#----------------------------------------
# [2] 패턴 입력
#----------------------------------------
패턴 (3줄 입력, 공백 구분)
  1줄: 1 1 1
  2줄: 1 1 1
  3줄: 1 1 1

#----------------------------------------
# [3] MAC 결과
#----------------------------------------
A 점수: 0.8999999999999999
B 점수: 0.9
연산 시간(평균/10회): 0.001540 ms
판정: 판정 불가 (|A-B| < 1e-09)

#----------------------------------------
# [4] 성능 분석 (평균/10회)
#----------------------------------------
크기(NxN)    평균 시간(ms)    연산 횟수(N^2)
--------------------------------------------
3x3          0.001540         9
```

0.1을 아홉 번 더한 A 점수는 0.8999999999999999로 B 점수 0.9와 아주 조금 다르지만, 차이가 1e-9보다 작아서 "판정 불가"로 나옵니다.

### 시험 4: 잘못 입력

입력한 값

```text
선택: 1
필터 A 1줄: 1 0       (숫자 2개)
필터 A 1줄: 1 a 0     (숫자가 아닌 글자)
```

실행 화면

```text
#----------------------------------------
# [1] 필터 입력
#----------------------------------------
필터 A (3줄 입력, 공백 구분)
  1줄: 1 0
입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.
필터 A를 처음부터 다시 입력하세요.
  1줄: 1 a 0
입력 형식 오류: 숫자만 입력하세요. (예: 0 1 0)
필터 A를 처음부터 다시 입력하세요.
  1줄: 
```

## 5. 실행 확인: 모드 2와 오류 처리

### mode_json.py

- `[1] 필터 로드`: `size_N` 키에서 N을 꺼내고, `cross`, `x` 필터 이름을 표준 라벨로 바꿔 크기를 검사한 뒤 저장합니다.
- `[2] 패턴 분석`: `size_N_번호` 키에서 N을 꺼내 같은 크기의 필터를 고르고, 크기와 라벨을 검사한 뒤 MAC 점수로 판정합니다. 문제가 있으면 오류로 멈추지 않고 그 케이스만 FAIL로 기록합니다.
- `[3] 성능 분석`: 3x3, 5x5, 13x13, 25x25의 MAC 평균 시간을 표로 출력합니다.
- `[4] 결과 요약`: 전체·통과·실패 개수와 실패 케이스 목록을 출력합니다.

```python
# 요구사항 03, 06, 08: 모드 2 - data.json 분석

import json

from src.mac import mac
from src.matrix import is_square, make_cross, make_x
from src.judge import normalize_label, judge, CROSS, X, UNDECIDED, EPSILON
from src.perf import measure_mac_ms, print_perf_table

# 실패 원인 분류
CAT_DATA = "데이터/스키마"
CAT_LOGIC = "로직"
CAT_NUMBER = "수치 비교"


def line(title):
    print()
    print("#" + "-" * 40)
    print("# " + title)
    print("#" + "-" * 40)


def load_data(path):
    """data.json을 읽는다. 파일이 없거나 깨졌으면 안내하고 None을 돌려준다."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다. main.py와 같은 폴더에 있는지 확인하세요.")
    except json.JSONDecodeError as e:
        print("오류: data.json 형식이 잘못되었습니다.", e)
    return None


def parse_size_from_key(key, parts_needed):
    """'size_13' 또는 'size_13_1'에서 13을 꺼낸다. 규칙에 안 맞으면 None."""
    parts = str(key).split("_")
    if len(parts) != parts_needed or parts[0] != "size":
        return None
    try:
        n = int(parts[1])
    except ValueError:
        return None
    return n if n > 0 else None


def load_filters(data):
    """filters를 {N: {"Cross": 표, "X": 표}} 모양으로 정리한다."""
    filters = {}
    raw = data.get("filters")
    if not isinstance(raw, dict):
        print("오류: data.json에 filters가 없습니다.")
        return filters
    for key, group in raw.items():
        n = parse_size_from_key(key, 2)
        if n is None or not isinstance(group, dict):
            print("x %s: 이름 규칙(size_N) 위반으로 건너뜀" % key)
            continue
        pair = {}
        for label_key, table in group.items():
            label = normalize_label(label_key)
            if label is None:
                print("x %s: 알 수 없는 필터 이름 '%s'" % (key, label_key))
            elif not is_square(table, n):
                print("x %s: %s 필터가 %dx%d가 아님" % (key, label, n, n))
            else:
                pair[label] = table
        if CROSS in pair and X in pair:
            filters[n] = pair
            print("v %s 필터 로드 완료 (Cross, X)" % key)
        else:
            print("x %s: Cross/X 필터가 모두 있어야 합니다" % key)
    return filters


def run_case(key, case, filters):
    """문제 하나를 채점한다. 문제가 있어도 오류를 내지 않고 FAIL로 기록한다."""
    result = {"id": key, "status": "FAIL", "reason": "", "category": CAT_DATA}

    n = parse_size_from_key(key, 3)
    if n is None:
        result["reason"] = "이름 규칙(size_N_번호) 위반"
        return result
    if n not in filters:
        result["reason"] = "size_%d 필터 없음" % n
        return result
    if not isinstance(case, dict):
        result["reason"] = "문제 형식 오류"
        return result
    pattern = case.get("input")
    if not is_square(pattern, n):
        result["reason"] = "패턴 크기 불일치 (%dx%d가 아님)" % (n, n)
        return result
    expected = normalize_label(case.get("expected"))
    if expected is None:
        result["reason"] = "알 수 없는 정답 라벨 '%s'" % case.get("expected")
        return result

    try:
        score_cross = mac(pattern, filters[n][CROSS])
        score_x = mac(pattern, filters[n][X])
    except TypeError:
        result["reason"] = "숫자가 아닌 값이 들어 있음"
        return result

    verdict = judge(score_cross, score_x, CROSS, X)
    result.update({"cross": score_cross, "x": score_x,
                   "verdict": verdict, "expected": expected})
    if verdict == expected:
        result["status"] = "PASS"
        result["category"] = ""
    elif verdict == UNDECIDED:
        result["category"] = CAT_NUMBER
        result["reason"] = "동점 (|%s - %s| < %g)" % (score_cross, score_x, EPSILON)
    else:
        result["category"] = CAT_LOGIC
        result["reason"] = "판정 %s, 정답 %s" % (verdict, expected)
    return result


def run_mode2(path):
    line("[1] 필터 로드")
    data = load_data(path)
    if data is None:
        return
    filters = load_filters(data)

    line("[2] 패턴 분석 (라벨 정규화 적용)")
    patterns = data.get("patterns")
    if not isinstance(patterns, dict):
        print("오류: data.json에 patterns가 없습니다.")
        patterns = {}
    results = []
    for key, case in patterns.items():
        r = run_case(key, case, filters)
        results.append(r)
        print("--- %s ---" % key)
        if "verdict" in r:
            print("Cross 점수:", r["cross"])
            print("X 점수:", r["x"])
            line_text = "판정: %s | expected: %s | %s" % (r["verdict"], r["expected"], r["status"])
            if r["status"] == "FAIL":
                line_text += " [%s] %s" % (r["category"], r["reason"])
            print(line_text)
        else:
            print("FAIL [%s] %s" % (r["category"], r["reason"]))

    line("[3] 성능 분석 (평균/10회)")
    rows = [(3, measure_mac_ms(make_cross(3), make_x(3)))]
    for n in (5, 13, 25):
        filt = filters.get(n, {}).get(CROSS, make_x(n))
        rows.append((n, measure_mac_ms(make_cross(n), filt)))
    print_perf_table(rows)

    line("[4] 결과 요약")
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    print("총 테스트: %d개" % len(results))
    print("통과: %d개" % passed)
    print("실패: %d개" % failed)
    if failed:
        print("실패 케이스:")
        for r in results:
            if r["status"] == "FAIL":
                print("- %s [%s] %s" % (r["id"], r["category"], r["reason"]))
    else:
        print("실패 케이스 없음")
```

### 모드 2 실행 화면 ([1] 필터 로드, [2] 패턴 분석)

```text
=== Mini NPU Simulator ===
[모드 선택]
1. 사용자 입력 (3x3)
2. data.json 분석
선택: 2

#----------------------------------------
# [1] 필터 로드
#----------------------------------------
v size_5 필터 로드 완료 (Cross, X)
v size_13 필터 로드 완료 (Cross, X)
v size_25 필터 로드 완료 (Cross, X)

#----------------------------------------
# [2] 패턴 분석 (라벨 정규화 적용)
#----------------------------------------
--- size_5_1 ---
Cross 점수: 0.9
X 점수: 0.8999999999999999
판정: UNDECIDED | expected: X | FAIL [수치 비교] 동점 (|0.9 - 0.8999999999999999| < 1e-09)
--- size_5_2 ---
Cross 점수: 8.9
X 점수: 0.1
판정: Cross | expected: Cross | PASS
--- size_13_1 ---
Cross 점수: 0.3
X 점수: 14.700000000000008
판정: X | expected: X | PASS
--- size_13_2 ---
Cross 점수: 7.499999999999997
X 점수: 7.5
판정: UNDECIDED | expected: Cross | FAIL [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
--- size_25_1 ---
Cross 점수: 4.9
X 점수: 4.899999999999999
판정: UNDECIDED | expected: X | FAIL [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
--- size_25_2 ---
Cross 점수: 52.9
X 점수: 0.1
판정: Cross | expected: Cross | PASS
```

([3] 성능 분석 화면은 6장 시간 복잡도 분석에, [4] 결과 요약 화면은 6장 실행 결과 요약에 있습니다.)

### 오류 처리 (data.json을 일부러 고쳐 시험)

| 시험 | 바꾼 내용 | 결과 |
|---|---|---|
| 파일 없음 | data.json 이름 변경 | "data.json 파일을 찾을 수 없습니다" 안내 후 종료 |
| JSON 손상 | 쉼표 하나 삭제 | "data.json 형식이 잘못되었습니다" 안내 후 종료 |
| 크기 불일치 | size_5_1 input에서 한 줄 삭제 | size_5_1만 FAIL [데이터/스키마] 패턴 크기 불일치 (5x5가 아님), 전체 6 / 통과 3 / 실패 3 |
| 키 규칙 위반 | size_5_1을 size_x_1로 변경 | size_x_1만 FAIL [데이터/스키마] 이름 규칙(size_N_번호) 위반, 전체 6 / 통과 3 / 실패 3 |
| 알 수 없는 라벨 | size_5_2의 expected를 "o"로 변경 | size_5_2만 FAIL [데이터/스키마] 알 수 없는 정답 라벨 'o', 전체 6 / 통과 2 / 실패 4 |

모든 경우 프로그램이 비정상 종료(Traceback) 없이 끝까지 실행되었습니다. 크기 불일치와 키 규칙 위반은 원래도 FAIL이던 size_5_1을 바꿨기 때문에 실패 수가 3개 그대로이고, 원인 분류만 수치 비교에서 데이터/스키마로 바뀌었습니다. 알 수 없는 라벨은 원래 PASS이던 size_5_2를 바꿨기 때문에 실패가 4개로 늘었습니다.

시험이 끝난 뒤 data.json은 원래대로 되돌렸습니다.

#### 오류 시험 1: 파일 없음

```text
#----------------------------------------
# [1] 필터 로드
#----------------------------------------
오류: data.json 파일을 찾을 수 없습니다. main.py와 같은 폴더에 있는지 확인하세요.
```

#### 오류 시험 2: JSON 손상

```text
#----------------------------------------
# [1] 필터 로드
#----------------------------------------
오류: data.json 형식이 잘못되었습니다. Expecting ',' delimiter: line 4 column 9 (char 49)
```

#### 오류 시험 3: 크기 불일치

```text
#----------------------------------------
# [2] 패턴 분석 (라벨 정규화 적용)
#----------------------------------------
--- size_5_1 ---
FAIL [데이터/스키마] 패턴 크기 불일치 (5x5가 아님)
--- size_5_2 ---
Cross 점수: 8.9
X 점수: 0.1
판정: Cross | expected: Cross | PASS
--- size_13_1 ---
Cross 점수: 0.3
X 점수: 14.700000000000008
판정: X | expected: X | PASS
--- size_13_2 ---
Cross 점수: 7.499999999999997
X 점수: 7.5
판정: UNDECIDED | expected: Cross | FAIL [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
--- size_25_1 ---
Cross 점수: 4.9
X 점수: 4.899999999999999
판정: UNDECIDED | expected: X | FAIL [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
--- size_25_2 ---
Cross 점수: 52.9
X 점수: 0.1
판정: Cross | expected: Cross | PASS

#----------------------------------------
# [3] 성능 분석 (평균/10회)
#----------------------------------------
크기(NxN)    평균 시간(ms)    연산 횟수(N^2)
--------------------------------------------
3x3          0.001530         9
5x5          0.003050         25
13x13        0.013130         169
25x25        0.045060         625

#----------------------------------------
# [4] 결과 요약
#----------------------------------------
총 테스트: 6개
통과: 3개
실패: 3개
실패 케이스:
- size_5_1 [데이터/스키마] 패턴 크기 불일치 (5x5가 아님)
- size_13_2 [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
- size_25_1 [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
```

#### 오류 시험 4: 키 규칙 위반

```text
#----------------------------------------
# [2] 패턴 분석 (라벨 정규화 적용)
#----------------------------------------
--- size_x_1 ---
FAIL [데이터/스키마] 이름 규칙(size_N_번호) 위반
--- size_5_2 ---
Cross 점수: 8.9
X 점수: 0.1
판정: Cross | expected: Cross | PASS
--- size_13_1 ---
Cross 점수: 0.3
X 점수: 14.700000000000008
판정: X | expected: X | PASS
--- size_13_2 ---
Cross 점수: 7.499999999999997
X 점수: 7.5
판정: UNDECIDED | expected: Cross | FAIL [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
--- size_25_1 ---
Cross 점수: 4.9
X 점수: 4.899999999999999
판정: UNDECIDED | expected: X | FAIL [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
--- size_25_2 ---
Cross 점수: 52.9
X 점수: 0.1
판정: Cross | expected: Cross | PASS

#----------------------------------------
# [3] 성능 분석 (평균/10회)
#----------------------------------------
크기(NxN)    평균 시간(ms)    연산 횟수(N^2)
--------------------------------------------
3x3          0.002420         9
5x5          0.004630         25
13x13        0.206830         169
25x25        0.211800         625

#----------------------------------------
# [4] 결과 요약
#----------------------------------------
총 테스트: 6개
통과: 3개
실패: 3개
실패 케이스:
- size_x_1 [데이터/스키마] 이름 규칙(size_N_번호) 위반
- size_13_2 [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
- size_25_1 [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
```

#### 오류 시험 5: 알 수 없는 라벨

```text
#----------------------------------------
# [2] 패턴 분석 (라벨 정규화 적용)
#----------------------------------------
--- size_5_1 ---
Cross 점수: 0.9
X 점수: 0.8999999999999999
판정: UNDECIDED | expected: X | FAIL [수치 비교] 동점 (|0.9 - 0.8999999999999999| < 1e-09)
--- size_5_2 ---
FAIL [데이터/스키마] 알 수 없는 정답 라벨 'o'
--- size_13_1 ---
Cross 점수: 0.3
X 점수: 14.700000000000008
판정: X | expected: X | PASS
--- size_13_2 ---
Cross 점수: 7.499999999999997
X 점수: 7.5
판정: UNDECIDED | expected: Cross | FAIL [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
--- size_25_1 ---
Cross 점수: 4.9
X 점수: 4.899999999999999
판정: UNDECIDED | expected: X | FAIL [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
--- size_25_2 ---
Cross 점수: 52.9
X 점수: 0.1
판정: Cross | expected: Cross | PASS

#----------------------------------------
# [3] 성능 분석 (평균/10회)
#----------------------------------------
크기(NxN)    평균 시간(ms)    연산 횟수(N^2)
--------------------------------------------
3x3          0.001550         9
5x5          0.002820         25
13x13        0.011910         169
25x25        0.043300         625

#----------------------------------------
# [4] 결과 요약
#----------------------------------------
총 테스트: 6개
통과: 2개
실패: 4개
실패 케이스:
- size_5_1 [수치 비교] 동점 (|0.9 - 0.8999999999999999| < 1e-09)
- size_5_2 [데이터/스키마] 알 수 없는 정답 라벨 'o'
- size_13_2 [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
- size_25_1 [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
```

## 6. 결과 리포트

### 6-1. 실행 결과 요약

전체 6개 중 통과 3개, 실패 3개입니다.

| 케이스 | Cross 점수 | X 점수 | 판정 | 정답 | 결과 | 원인 분류 |
|---|---|---|---|---|---|---|
| size_5_1 | 0.9 | 0.8999999999999999 | UNDECIDED | X | FAIL | 수치 비교 |
| size_5_2 | 8.9 | 0.1 | Cross | Cross | PASS | - |
| size_13_1 | 0.3 | 14.700000000000008 | X | X | PASS | - |
| size_13_2 | 7.499999999999997 | 7.5 | UNDECIDED | Cross | FAIL | 수치 비교 |
| size_25_1 | 4.9 | 4.899999999999999 | UNDECIDED | X | FAIL | 수치 비교 |
| size_25_2 | 52.9 | 0.1 | Cross | Cross | PASS | - |

실행 화면 ([4] 결과 요약)

```text
#----------------------------------------
# [4] 결과 요약
#----------------------------------------
총 테스트: 6개
통과: 3개
실패: 3개
실패 케이스:
- size_5_1 [수치 비교] 동점 (|0.9 - 0.8999999999999999| < 1e-09)
- size_13_2 [수치 비교] 동점 (|7.499999999999997 - 7.5| < 1e-09)
- size_25_1 [수치 비교] 동점 (|4.9 - 4.899999999999999| < 1e-09)
```

### 6-2. FAIL 케이스 원인 분석

실패 3건은 모두 수치 비교 문제이고, 데이터/스키마 문제와 로직 문제로 인한 실패는 0건입니다.

세 케이스는 필터 값이 두 점수가 수학적으로 같아지도록 만들어져 있습니다. 예를 들어 size_5_1은 X 모양 입력의 9칸이 X 필터의 0.1과 겹쳐 0.1 × 9 = 0.9가 되고, 십자가 필터와는 가운데 한 칸(0.9)만 겹쳐 역시 0.9가 됩니다.

그런데 컴퓨터는 0.1을 2진수로 정확히 저장하지 못해서, 0.1을 아홉 번 더한 값이 0.8999999999999999처럼 아주 조금 작게 나옵니다.

만약 `==`나 `>`로만 비교했다면 size_5_1과 size_25_1은 Cross, size_13_2는 X로 판정되었을 것입니다. 정답과 달라 여전히 FAIL이지만, 원인이 로직 오류처럼 보였을 것입니다.

허용오차 1e-9를 둔 덕분에 세 케이스는 동점(UNDECIDED)으로 올바르게 분류되었습니다. 정답이 X 또는 Cross이므로 규칙에 따라 FAIL이며, 이는 프로그램 결함이 아니라 의도된 동점 데이터입니다.

1e-9는 이 계산 오차(1e-16 수준)보다 충분히 크고, PASS한 케이스들의 점수 차이(8.8 이상)보다 충분히 작아서 '같은 점수'와 '다른 점수'를 구별할 수 있습니다.

데이터 표기도 섞여 있습니다. expected는 `+`와 `x`, 필터 키는 `cross`와 `x`로 적혀 있습니다. 라벨 정규화가 없었다면 판정 `Cross`와 정답 `+`가 문자열로 달라서, 통과한 3건도 FAIL이 되었을 것입니다.

크기 불일치, 키 규칙 위반, 알 수 없는 라벨은 공식 데이터에는 없었습니다. data.json을 일부러 고쳐 시험했을 때 해당 케이스만 FAIL로 기록되고 프로그램은 끝까지 실행되었습니다(5장 오류 처리 참고).

### 6-3. 시간 복잡도 분석 (성능 표 해석과 O(N²) 근거)

실행 화면 ([3] 성능 분석)

```text
#----------------------------------------
# [3] 성능 분석 (평균/10회)
#----------------------------------------
크기(NxN)    평균 시간(ms)    연산 횟수(N^2)
--------------------------------------------
3x3          0.004270         9
5x5          0.004540         25
13x13        0.018000         169
25x25        0.060490         625
```

| 크기 | 평균 시간(ms) | 연산 횟수(N²) | 3x3 대비 시간 |
|---|---|---|---|
| 3x3 | 0.004270 | 9 | 1배 |
| 5x5 | 0.004540 | 25 | 약 1.1배 |
| 13x13 | 0.018000 | 169 | 약 4.2배 |
| 25x25 | 0.060490 | 625 | 약 14.2배 |

MAC 연산은 N×N의 모든 칸을 한 번씩 곱하고 더하므로(3-2의 이중 for문) 연산 횟수가 N²이고, 시간 복잡도는 O(N²)입니다.

연산 횟수는 3x3의 9회에서 25x25의 625회로 약 69배 늘어나고, 측정 시간도 크기가 커질수록 꾸준히 늘어났습니다.

다만 시간은 69배가 아니라 약 14.2배만 늘었습니다. 함수 호출과 반복문 시작 같은 고정 비용은 크기와 상관없이 매번 들기 때문에, 계산량이 적은 작은 크기에서 그 비중이 커지기 때문입니다. 실제로 3x3(9회)과 5x5(25회)는 연산 횟수가 약 2.8배 차이 나지만 시간은 약 1.1배로 거의 같았고, 크기가 커질수록(13x13 → 25x25에서 연산 3.7배, 시간 3.4배) 시간 증가가 연산 횟수 증가에 가까워졌습니다.

측정은 `time.perf_counter`로 `mac()` 호출 구간만 10회 반복해 평균을 냈고(3-4 참고), 입력·출력·파일 읽기 시간은 포함하지 않았습니다. 3x3은 data.json에 없어서 패턴 생성 함수로 만들어 측정했습니다. 절대 시간은 컴퓨터와 실행 시점마다 다릅니다. 실제로 같은 컴퓨터에서 다시 실행한 오류 시험 3과 5에서는 3x3이 0.00153 ~ 0.00155ms, 25x25가 0.04330 ~ 0.04506ms로 위 표와 다른 값이 나왔습니다. 오류 시험 4에서는 13x13이 0.206830ms로 다른 실행보다 10배 이상 크게 나왔는데, 측정 중 다른 프로그램이 컴퓨터를 함께 사용하면 이렇게 한 번씩 튀는 값이 생길 수 있습니다. 그래도 모든 실행에서 3x3 < 5x5 < 13x13 < 25x25 순서는 같았습니다. 그래서 숫자 하나하나보다 크기에 따라 시간이 꾸준히 늘어나는 추세를 기준으로 해석했습니다.

## 7. 파일 구조와 data.json 구조

### 파일 구조

| 파일 | 역할 |
|---|---|
| main.py | 모드 선택, 실행 흐름 |
| data.json | 필터와 패턴 데이터 |
| src/__init__.py | src 폴더를 패키지로 인식시키는 빈 파일 |
| src/matrix.py | N×N 표 만들기·읽기·쓰기, 크기 검사, 십자가·X 생성 |
| src/mac.py | MAC 연산 |
| src/judge.py | 라벨 정규화, epsilon 판정 |
| src/perf.py | 시간 측정, 성능 표 출력 |
| src/mode_input.py | 모드 1 (사용자 입력) |
| src/mode_json.py | 모드 2 (data.json 분석, 결과 요약) |

### data.json 구조

- `filters`: `size_5`, `size_13`, `size_25` 아래에 `cross`, `x` 필터(N×N 실수 배열)가 있습니다.
- `patterns`: `size_{N}_{idx}` 키 아래에 `input`(N×N 배열)과 `expected`(`+` 또는 `x`)가 있습니다.
- 패턴 키에서 N을 꺼내 같은 크기의 필터를 고릅니다.