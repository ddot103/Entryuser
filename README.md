# `entry-user.json` 구조 안내

`entry-user.json`은 수집된 엔트리 유저 정보가 저장되는 JSON 데이터베이스입니다.

---

## 📌 전체 구조

유저의 24자리 고유 ID(`uid`)가 Key가 되며, 해당 유저의 정보가 Object 형태로 저장됩니다.

~~~json
{
  "000000000000000000000000": {
    "id": "000000000000000000000000",
    "nickname": "가상의유저",
    "profileImage": "[https://playentry.org/uploads/00/00/000000000000000000000000.png](https://playentry.org/uploads/00/00/000000000000000000000000.png)",
    "follower": 100,
    "following": 50,
    "created": "2026-01-01T00:00:00.000Z",
    "lastUpdated": "2026-09-13T10:00:00"
  }
}
~~~

---

## ⚠️ `null` 값 발생 원인 및 의미

특정 필드가 `null`로 표시되는 원인은 다음과 같습니다.

1. **신규 유저 탐색 직후 (미업데이트 상태)**
   * 팔로워/팔로잉 목록이나 엔트리 이야기 피드에서 새로운 유저를 **최초 발견했을 때**는 `id`와 `nickname`만 우선 수집됩니다.
   * 따라서 상세 조회를 거치기 전까지 **`profileImage`, `follower`, `following`, `created`, `lastUpdated` 필드는 기본값인 `null`**로 저장됩니다.
   * 이후 순차 업데이트 루프에서 해당 유저의 순서가 오면 실제 데이터로 갱신됩니다.

2. **기본 프로필 이미지 / 설정 미비**
   * 유저가 프로필 사진을 따로 등록하지 않은 경우 `profileImage`는 계속 `null`로 유지됩니다.

3. **탈퇴 / 삭제 / 비공개 계정**
   * 존재하지 않거나 서버에서 정보를 불러올 수 없는 계정의 경우 일부 필드가 `null`로 남아있을 수 있습니다.

---

## 🏷️ 필드 규격

* **`id`** (`String`): 유저의 고유 ObjectID (24자리 문자열)
* **`nickname`** (`String`): 유저 닉네임
* **`profileImage`** (`String` | `null`): 프로필 이미지 전체 URL (미설정 또는 미수집 시 `null`)
* **`follower`** (`Integer` | `null`): 팔로워 수 (미수집 시 `null`)
* **`following`** (`Integer` | `null`): 팔로잉 수 (미수집 시 `null`)
* **`created`** (`String` | `null`): 계정 생성 날짜 (ISO 8601 UTC, 미수집 시 `null`)
* **`lastUpdated`** (`String` | `null`): 마지막 정보 갱신 시각 (YYYY-MM-DDTHH:mm:ss, KST, 미수집 시 `null`)
