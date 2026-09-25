import json
import os
import re


# ============================================================
# 설정
# ============================================================

FILES_DIR = os.path.join("entryuser", "files")
OUTPUT_FILE = "entry-user.json"


# ============================================================
# 청크 파일 정렬
# ============================================================

def chunk_sort_key(filename):
    """
    users_chunk_001.json
    users_chunk_002.json
    ...
    users_chunk_055.json

    파일 번호를 기준으로 정렬합니다.
    """
    match = re.search(r"users_chunk_(\d+)\.json$", filename)

    if match:
        return int(match.group(1))

    return float("inf")


# ============================================================
# 청크 병합
# ============================================================

def merge_chunks():
    print("=" * 60)
    print("EntryUser 청크 병합 프로그램")
    print("=" * 60)

    # --------------------------------------------------------
    # 폴더 확인
    # --------------------------------------------------------

    if not os.path.isdir(FILES_DIR):
        print()
        print(f"❌ 폴더를 찾을 수 없습니다:")
        print(f"   {FILES_DIR}")
        print()
        return

    # --------------------------------------------------------
    # users_chunk_XXX.json 찾기
    # --------------------------------------------------------

    chunk_files = []

    for filename in os.listdir(FILES_DIR):
        if re.fullmatch(r"users_chunk_\d+\.json", filename):
            chunk_files.append(filename)

    chunk_files.sort(key=chunk_sort_key)

    if not chunk_files:
        print()
        print("❌ users_chunk_XXX.json 파일을 찾을 수 없습니다.")
        print()
        return

    print()
    print(f"📁 청크 폴더: {FILES_DIR}")
    print(f"📦 발견된 청크: {len(chunk_files)}개")
    print()

    # --------------------------------------------------------
    # 발견된 파일 목록
    # --------------------------------------------------------

    print("발견된 파일:")

    for filename in chunk_files:
        print(f"  - {filename}")

    print()

    # --------------------------------------------------------
    # 데이터 병합
    # --------------------------------------------------------

    all_data = {}

    total_users = 0
    duplicate_ids = []

    for index, filename in enumerate(chunk_files, 1):
        file_path = os.path.join(FILES_DIR, filename)

        print(f"[{index}/{len(chunk_files)}] 읽는 중: {filename}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError as e:
            print()
            print(f"  ❌ JSON 형식 오류: {filename}")
            print(f"     {e}")
            print()
            continue

        except Exception as e:
            print()
            print(f"  ❌ 파일 읽기 실패: {filename}")
            print(f"     {e}")
            print()
            continue

        if not isinstance(data, dict):
            print(f"  ⚠️ 객체(Object) 형식이 아니므로 건너뜁니다.")
            continue

        chunk_count = len(data)

        # ----------------------------------------------------
        # 데이터 추가
        # ----------------------------------------------------

        for uid, user_info in data.items():

            # 중복 ID 확인
            if uid in all_data:
                duplicate_ids.append({
                    "id": uid,
                    "file": filename
                })

            all_data[uid] = user_info

        total_users += chunk_count

        print(f"  ✓ {chunk_count:,}명")

    # --------------------------------------------------------
    # 결과 확인
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("병합 완료")
    print("=" * 60)

    print(f"📦 읽은 청크: {len(chunk_files):,}개")
    print(f"👥 읽은 데이터: {total_users:,}개")
    print(f"👤 최종 유저 수: {len(all_data):,}명")

    # --------------------------------------------------------
    # 중복 ID 출력
    # --------------------------------------------------------

    if duplicate_ids:
        print()
        print(f"⚠️ 중복된 ID: {len(duplicate_ids):,}개")
        print()
        print("중복된 ID는 마지막으로 읽은 데이터로 덮어씌워졌습니다.")

        # 너무 많으면 전부 출력하지 않음
        display_limit = 20

        for item in duplicate_ids[:display_limit]:
            print(f"  - {item['id']} ({item['file']})")

        if len(duplicate_ids) > display_limit:
            print(
                f"  ... 외 {len(duplicate_ids) - display_limit:,}개"
            )

    else:
        print()
        print("✓ 중복된 유저 ID가 없습니다.")

    # --------------------------------------------------------
    # 닉네임 기준 정렬
    # --------------------------------------------------------

    print()
    print("🔄 닉네임 기준으로 정렬 중...")

    sorted_data = dict(
        sorted(
            all_data.items(),
            key=lambda item: (
                str(
                    item[1].get("nickname", "")
                    if isinstance(item[1], dict)
                    else ""
                )
            ).lower()
        )
    )

    # --------------------------------------------------------
    # 저장
    # --------------------------------------------------------

    print(f"💾 저장 중: {OUTPUT_FILE}")

    try:
        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                sorted_data,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:
        print()
        print("❌ 저장 실패")
        print(f"   {e}")
        print()
        return

    # --------------------------------------------------------
    # 파일 크기
    # --------------------------------------------------------

    try:
        file_size = os.path.getsize(OUTPUT_FILE)

        if file_size >= 1024 * 1024:
            size_text = f"{file_size / (1024 * 1024):.2f} MB"
        else:
            size_text = f"{file_size / 1024:.2f} KB"

    except Exception:
        size_text = "알 수 없음"

    # --------------------------------------------------------
    # 최종 결과
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("✅ 모든 작업이 완료되었습니다.")
    print("=" * 60)
    print()
    print(f"출력 파일 : {OUTPUT_FILE}")
    print(f"유저 수   : {len(sorted_data):,}명")
    print(f"파일 크기 : {size_text}")
    print()


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":
    try:
        merge_chunks()

    except KeyboardInterrupt:
        print()
        print("⚠️ 사용자가 작업을 중단했습니다.")

    except Exception as e:
        print()
        print("❌ 예상하지 못한 오류가 발생했습니다.")
        print(f"   {e}")
