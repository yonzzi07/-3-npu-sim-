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