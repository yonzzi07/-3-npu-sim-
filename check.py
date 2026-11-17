from src.matrix import make_matrix, set_value, get_value, make_cross, make_x
from src.mac import mac
from src.judge import normalize_label, judge
from src.perf import measure_mac_ms

m = make_matrix(3)
set_value(m, 0, 0, 7)
print("1) 한 칸만 바뀌나:", m, "->", get_value(m, 0, 0))
print("2) 십자가 vs 십자가 =", mac(make_cross(3), make_cross(3)))
print("   십자가 vs X     =", mac(make_cross(3), make_x(3)))
print("3) 라벨 통일:", normalize_label("+"), normalize_label(" x "), normalize_label("abc"))
print("4) 판정 0.9 vs 0.8999999999999999 ->", judge(0.9, 0.8999999999999999, "Cross", "X"))
print("5) 25x25 계산 시간(ms):", measure_mac_ms(make_cross(25), make_x(25)))