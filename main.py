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