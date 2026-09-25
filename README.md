# EntryUser

엔트리(Entry) 유저 데이터를 수집하고 저장하는 저장소입니다.

## 목차

- [데이터 형식](#데이터-형식)
  - [1. 청크형 — `entryuser/files/`](#1-청크형--entryuserfiles)
    - [데이터 필드](#데이터-필드)
  - [2. 통합형 — `entry-user.json`](#2-통합형--entry-userjson)
    - [`null` 값에 대하여](#null-값에-대하여)
    - [날짜 형식](#날짜-형식)
  - [3. 간단형 — `data.json`](#3-간단형--datajson)
- [데이터 형식 비교](#데이터-형식-비교)
- [청크형을 통합형으로 합치기](#청크형을-통합형으로-합치기)
- [저장소 구조](#저장소-구조)
- [주의사항](#주의사항)
- [저장소 비공개 또는 삭제 요청](#저장소-비공개-또는-삭제-요청)

---

## 데이터 형식

### 1. 청크형 — `entryuser/files/`

대량의 유저 데이터를 여러 JSON 파일로 나누어 저장한 형식입니다.

현재 저장소에서 주로 사용하는 데이터 형식입니다.

```text
entryuser/
└── files/
    ├── users_chunk_001.json
    ├── users_chunk_002.json
    ├── users_chunk_003.json
    ├── ...
    └── users_chunk_055.json
```

청크 파일은 모두 같은 구조를 사용합니다.

```json
{
  "000000000000000000000000": {
    "id": "000000000000000000000000",
    "nickname": "가상의유저",
    "profileImage": "https://playentry.org/uploads/00/00/000000000000000000000000.png",
    "follower": 100,
    "following": 50,
    "created": "2026-01-01T00:00:00.000Z",
    "lastUpdated": "2026-09-13T10:00:00"
  }
}
```

청크 번호는 반드시 연속적일 필요가 없습니다. 실제로 존재하는 `users_chunk_*.json` 파일만 사용하면 됩니다.

#### 데이터 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | String | 유저의 고유 ID (24자리 문자열) |
| `nickname` | String | 유저 닉네임 |
| `profileImage` | String / null | 프로필 이미지 URL |
| `follower` | Integer / null | 팔로워 수 |
| `following` | Integer / null | 팔로잉 수 |
| `created` | String / null | 계정 생성 날짜 |
| `lastUpdated` | String / null | 마지막 데이터 갱신 시각 |

---

### 2. 통합형 — `entry-user.json`

모든 유저 데이터를 하나의 JSON 파일에 저장한 형식입니다.

구조는 청크형과 동일하며, 청크 파일들을 하나로 합쳐 사용할 수 있습니다.

```json
{
  "000000000000000000000000": {
    "id": "000000000000000000000000",
    "nickname": "가상의유저",
    "profileImage": "https://playentry.org/uploads/00/00/000000000000000000000000.png",
    "follower": 100,
    "following": 50,
    "created": "2026-01-01T00:00:00.000Z",
    "lastUpdated": "2026-09-13T10:00:00"
  }
}
```

#### `null` 값에 대하여

일부 필드는 `null`일 수 있습니다.

- 새로 발견된 유저는 처음 발견될 당시 `id`와 `nickname`만 가지고 있을 수 있습니다.
- 프로필 사진이 없는 경우 `profileImage`가 `null`일 수 있습니다.
- 삭제되었거나 존재하지 않거나 정보를 조회할 수 없는 계정은 일부 정보가 `null`로 남을 수 있습니다.

새로운 유저는 이후 상세 정보가 조회되면 데이터가 갱신됩니다.

#### 날짜 형식

`created`는 ISO 8601 UTC 형식을 사용합니다.

```text
2026-01-01T00:00:00.000Z
```

`lastUpdated`는 다음 형식을 사용합니다.

```text
YYYY-MM-DDTHH:mm:ss
```

---

### 3. 간단형 — `data.json`

닉네임과 고유 공개 ID만 저장하는 간단한 형식입니다.

```json
{
  "닉네임": "고유공개아이디"
}
```

예:

```json
{
  "가상의유저": "000000000000000000000000",
  "테스트유저": "111111111111111111111111"
}
```

Key는 닉네임이고 Value는 해당 유저의 고유 공개 ID입니다.

---

## 데이터 형식 비교

| | 청크형 | `entry-user.json` | `data.json` |
|---|---|---|---|
| 상세 유저 정보 | O | O | X |
| 프로필 이미지 | O | O | X |
| 팔로워 / 팔로잉 | O | O | X |
| 계정 생성일 | O | O | X |
| 마지막 갱신일 | O | O | X |
| 여러 파일로 분할 | O | X | X |
| 닉네임 → ID 조회 | 가능 | 가능 | O |

---

## 청크형을 통합형으로 합치기

`entryuser/files/`의 `users_chunk_*.json` 파일들을 하나의 `entry-user.json`으로 합칠 수 있습니다.

저장소 루트에 아래 Python 파일을 만들고 실행하면 됩니다.

```python
import json
import os
import re


FILES_DIR = os.path.join("entryuser", "files")
OUTPUT_FILE = "entry-user.json"


def chunk_sort_key(filename):
    match = re.fullmatch(r"users_chunk_(\d+)\.json", filename)
    return int(match.group(1)) if match else float("inf")


def main():
    if not os.path.isdir(FILES_DIR):
        print(f"폴더를 찾을 수 없습니다: {FILES_DIR}")
        return

    chunk_files = [
        filename
        for filename in os.listdir(FILES_DIR)
        if re.fullmatch(r"users_chunk_\d+\.json", filename)
    ]

    chunk_files.sort(key=chunk_sort_key)

    if not chunk_files:
        print("청크 파일을 찾을 수 없습니다.")
        return

    all_data = {}

    for filename in chunk_files:
        path = os.path.join(FILES_DIR, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print(f"[건너뜀] JSON 객체가 아닙니다: {filename}")
                continue

            all_data.update(data)
            print(f"[로드] {filename}: {len(data):,}명")

        except Exception as e:
            print(f"[오류] {filename}: {e}")

    # 닉네임 기준 정렬
    all_data = dict(
        sorted(
            all_data.items(),
            key=lambda item: (
                str(item[1].get("nickname", "")).lower()
                if isinstance(item[1], dict)
                else ""
            )
        )
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            all_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("병합 완료")
    print(f"청크 파일: {len(chunk_files):,}개")
    print(f"전체 유저: {len(all_data):,}명")
    print(f"출력 파일: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

실행:

```powershell
python merge_chunks.py
```

이 코드는 `users_chunk_001.json`, `users_chunk_002.json`처럼 번호가 붙은 파일을 자동으로 찾기 때문에 중간 번호가 빠져 있어도 사용할 수 있습니다.

---

## 저장소 구조

```text
Entryuser/
├── README.md
├── data.json
├── entry-user.json
└── entryuser/
    └── files/
        ├── users_chunk_001.json
        ├── users_chunk_002.json
        ├── ...
        └── users_chunk_055.json
```

---

## 주의사항

이 저장소의 데이터는 수집 및 갱신 시점에 따라 실제 Entry의 현재 정보와 차이가 있을 수 있습니다.

특히 다음 정보는 변경될 수 있습니다.

- 닉네임
- 프로필 이미지
- 팔로워 수
- 팔로잉 수
- 계정 상태

따라서 이 저장소의 데이터를 Entry의 실시간 데이터베이스와 동일한 것으로 간주해서는 안 됩니다.

---

# 저장소 비공개 또는 삭제 요청

엔트리 운영자 분들 중 만약 이 Entryuser 저장소를 비공개 또는 삭제를 원하시는 분들은  
**ddotentry@gmail.com**으로 메일을 보내주세요. (자신이 엔트리 운영자인 것을 밝힐 수 있어야 합니다.)
