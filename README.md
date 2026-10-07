# mind_test_contents

심리테스트 앱(mind_test)이 받아 쓰는 테스트 콘텐츠 저장소입니다.
`main` 브랜치에 push하면 GitHub Pages로 몇 분 안에 모든 사용자에게 반영됩니다. **앱 업데이트·심사가 필요 없습니다.**

- 목록: https://dhsthdwjd.github.io/mind_test_contents/index.json
- 테스트: `https://dhsthdwjd.github.io/mind_test_contents/tests/<테스트id>.json`
- 이미지: `https://dhsthdwjd.github.io/mind_test_contents/images/<테스트id>/<파일명>.webp`

## 폴더 구성

```
index.json            앱 메인 화면의 테스트 목록 (순서 = 화면 순서)
tests/<id>.json       테스트 하나의 문항·보기·점수·결과
source/<id>/          원본 이미지 (png/jpg/webp 아무거나)
images/<id>/          앱이 실제로 받는 이미지 (scripts/build_images.py가 만듦, 직접 넣지 않기)
scripts/              이미지 변환·검사 스크립트
```

## 새 테스트 추가하기

1. **id 정하기**: 영문 소문자와 `_`만 (예: `love_style`). 한 번 정하면 바꾸지 않습니다.
2. **원본 이미지 넣기**: `source/<id>/` 에 넣습니다. 이름 규칙은 아래 표를 따릅니다.
3. **이미지 변환**
   ```bash
   python3 scripts/build_images.py <id>
   ```
4. **`tests/<id>.json` 작성**: 기존 파일을 복사해서 고치는 게 가장 쉽습니다. (형식은 아래)
5. **`index.json`에 한 줄 추가**: 넣은 위치가 앱 목록 순서입니다.
6. **검사**
   ```bash
   python3 scripts/validate.py
   ```
   `검사 통과`가 나와야 합니다. 오류가 있으면 **절대 push하지 않습니다.**
7. commit → push. 몇 분 뒤 앱에 나타납니다.

숨기기만 하려면 `index.json`에서 해당 테스트의 `"visible": false`로 바꿉니다. (파일은 지우지 않기: 이미 결과를 보고 있는 사용자가 있을 수 있음)

## 이미지 규칙

| 용도 | 파일명 | 권장 |
|---|---|---|
| 목록 썸네일 | `thumb` | 정사각형 |
| 문항 위 그림 | `q01`, `q02` … | |
| 그림 고르기 보기 | `q01_a`, `q01_b`, `q01_c` … | 정사각형 |
| 결과 그림 | `r01`, `r02` … | |

- 변환 스크립트가 자동으로 **긴 변 600px 이하, WebP 품질 80**으로 만듭니다. 원본은 크게 넣어도 됩니다.
- **한 번 올린 파일명은 재사용하지 않습니다.** 앱이 이미지를 기기에 캐시하기 때문에, 같은 이름으로 그림만 바꾸면 예전 그림이 계속 보일 수 있습니다. 그림을 고칠 땐 `q01_a_v2`처럼 새 이름으로 넣고 JSON도 새 이름으로 바꿉니다.
- 변환 스크립트는 `images/`에 같은 이름이 이미 있으면 덮어쓰지 않습니다. (위 규칙을 실수로 어기지 않게)
- **직접 그렸거나 상업 이용이 허락된 이미지만** 씁니다.

## JSON 형식

### index.json
```json
{
  "schemaVersion": 1,
  "tests": [
    {
      "id": "animal_type",
      "title": "MBTI보다 정확한\n동물 성향 성격 테스트",
      "thumbnail": "thumb.webp",
      "questionCount": 10,
      "file": "tests/animal_type.json",
      "minAppVersion": 772,
      "visible": true
    }
  ]
}
```
- `title`의 `\n`은 줄바꿈입니다.
- `minAppVersion`: 이 테스트를 보여줄 최소 앱 versionCode. 새 문항 형식처럼 옛날 앱이 모르는 기능을 쓸 때 올립니다. 평소엔 그대로 둡니다.

### tests/<id>.json
```json
{
  "schemaVersion": 1,
  "id": "animal_type",
  "title": "…",
  "questions": [
    {
      "type": "text",
      "text": "질문",
      "image": "q01.webp",
      "options": [ { "text": "A. 보기", "score": 4 } ]
    },
    {
      "type": "image",
      "text": "가장 마음에 드는 그림을 선택하세요",
      "options": [ { "image": "q02_a.webp", "score": 1 } ]
    }
  ],
  "results": [
    { "min": 10, "max": 13, "title": "토끼", "body": "결과 설명", "image": "r01.webp" }
  ]
}
```
- 문항 `type`: `text`(글 보기 2~4개) 또는 `image`(그림 보기 2~4개). 문항 위 `image`는 있어도 되고 없어도 됩니다.
- 총점 = 고른 보기 `score`의 합. 총점이 `min`~`max`(둘 다 포함)에 드는 결과를 보여줍니다.
- 결과 `image`는 선택입니다.
- **JSON에는 데이터만 넣습니다.** (Google Play 정책상 서버에서 실행 코드를 받으면 안 됨)

## 검사 스크립트가 잡아주는 것

- JSON 문법 오류, 빠진 필드, 잘못된 type, 보기 개수
- JSON에 적었는데 실제로 없는 이미지, 150KB 넘는 이미지
- 결과 점수 구간이 겹치는 경우
- **나올 수 있는 총점인데 해당 결과가 없는 경우** (모든 조합을 계산해서 확인)
- index.json의 문항 수가 실제와 다른 경우

## 준비물

Python 3와 Pillow: `pip3 install Pillow`
