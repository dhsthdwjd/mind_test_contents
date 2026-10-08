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
2. **원본 이미지 넣기** (이미지를 쓰는 테스트만): `source/<id>/` 에 넣습니다. 이름 규칙은 아래 표를 따릅니다.
   글로만 된 테스트는 이미지 없이 JSON만 있으면 됩니다.
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

**규격 (반드시 지키기)**

| 용도 | 파일명 | 비율 | 크기 |
|---|---|---|---|
| 문항 위 그림 | `q01`, `q02` … | **4:3** (가로:세로) | 높이 600px 이상 (예: 800x600, 1024x768) |
| 그림 고르기 보기 | `q01_a`, `q01_b`, `q01_c`, `q01_d` | **정사각형** | 600x600 이상 (예: 1024x1024) |
| 결과 그림 | `r01`, `r02` … | **4:3** | 높이 600px 이상 |

- 변환 스크립트는 **크기만 줄이고 비율은 바꾸지 않습니다.** (짧은 변 600px로 축소, 확대는 안 함) 정사각형은 600x600, 4:3은 800x600이 됩니다.
- 비율이 다르거나 너무 작으면 검사 스크립트가 오류를 냅니다.
- 앱 화면: 그림 보기는 흰 정사각형 칸 안에 **잘리지 않게** 들어갑니다. 문항·결과 그림은 4:3 칸에 꽉 채워집니다.
- 그림 보기에는 `text`를 함께 적으면 그림 아래에 글자가 나옵니다 (예: "1. 딸기잼"). **글자는 그림 안에 넣지 말고 `text`로** 적는 걸 권장합니다. 오타 수정이 JSON 한 줄로 끝납니다.

**운영 규칙**
- **한 번 올린 파일명은 재사용하지 않습니다.** 앱이 이미지를 기기에 캐시하기 때문에, 같은 이름으로 그림만 바꾸면 예전 그림이 계속 보일 수 있습니다. 그림을 고칠 땐 `q01_a_v2`처럼 새 이름으로 넣고 JSON도 새 이름으로 바꿉니다.
- 변환 스크립트는 `images/`에 같은 이름이 이미 있으면 덮어쓰지 않습니다. (위 규칙을 실수로 어기지 않게)
- **직접 그렸거나 상업 이용이 허락된 이미지만** 씁니다.
- 기존 4개 테스트(shy_drawing, animal_type, charm_flower, first_impression)는 규격이 생기기 전에 만들어져 규격 검사에서 제외됩니다.

## 글자는 영어·한국어 두 가지로 (필수)

앱 기본 언어는 영어이고, 설정 > Language 에서 한국어로 바꿀 수 있습니다. 앱은 고른 언어의 글자를 보여줍니다.
그래서 **화면에 보이는 모든 글자 필드**(제목, 문항, 보기, 결과 제목·설명)는 이렇게 씁니다.

```json
"title": { "en": "What did you see first?", "ko": "가장 먼저 무엇이 보였나요?" }
```

- `en`, `ko` 둘 다 채워야 합니다. 하나라도 비면 검사 스크립트가 오류를 냅니다.
- 다른 언어(`ja` 등)는 쓰지 않습니다.
- 이미지·점수·순서는 언어와 상관없이 하나만 둡니다.
- 그림 안에 글자를 넣으면 언어를 바꿔도 그대로 보입니다. 글자는 되도록 `text`로 적습니다.

## JSON 형식

### index.json
```json
{
  "schemaVersion": 1,
  "tests": [
    {
      "id": "animal_type",
      "title": { "en": "More Accurate Than MBTI:\nAnimal Personality Test", "ko": "MBTI보다 정확한\n동물 성향 성격 테스트" },
      "questionCount": 10,
      "file": "tests/animal_type.json",
      "minAppVersion": 772,
      "visible": true
    }
  ]
}
```
- `title`의 `\n`은 줄바꿈입니다. 목록 카드에는 제목과 "N문항"만 보입니다. (썸네일 없음)
- 썸네일(`thumbnail`)은 없습니다. 적으면 검사 스크립트가 오류를 냅니다.
- `minAppVersion`: 이 테스트를 보여줄 최소 앱 versionCode. 새 문항 형식처럼 옛날 앱이 모르는 기능을 쓸 때 올립니다. 평소엔 그대로 둡니다.

### tests/<id>.json
```json
{
  "schemaVersion": 1,
  "id": "animal_type",
  "title": { "en": "…", "ko": "…" },
  "questions": [
    {
      "type": "text",
      "text": { "en": "Question", "ko": "질문" },
      "image": "q01.webp",
      "options": [ { "text": { "en": "A. Option", "ko": "A. 보기" }, "score": 4 } ]
    },
    {
      "type": "image",
      "text": { "en": "Choose the picture you like the most", "ko": "가장 마음에 드는 그림을 선택하세요" },
      "options": [ { "image": "q02_a.webp", "text": { "en": "1. Strawberry jam", "ko": "1. 딸기잼" }, "score": 1 } ]
    }
  ],
  "results": [
    { "min": 10, "max": 13, "title": { "en": "Rabbit", "ko": "토끼" }, "body": { "en": "…", "ko": "결과 설명" }, "image": "r01.webp" }
  ]
}
```
- 문항 `type`: `text`(글 보기 2~4개) 또는 `image`(그림 보기 2~4개). 문항 위 `image`는 있어도 되고 없어도 됩니다.
- 그림 보기의 `text`는 선택입니다. 있으면 그림 아래에 보입니다.
- (score 방식) 총점 = 고른 보기 `score`의 합. 총점이 `min`~`max`(둘 다 포함)에 드는 결과를 보여줍니다.
- 결과 `image`는 선택입니다.
- `resultType`(선택): 결과를 보여주는 방식.
  - `score` (기본값, 생략 가능): "당신의 점수: 14점"과 "13점 ~ 14점: 재스민"(영어: "Your score: 14", "13–14 pts: Jasmine")처럼 점수와 구간을 보여줍니다. 여러 문항을 합산하는 테스트용.
  - `choice`: **고른 보기가 곧 결과인 1문항 테스트용.** N번째 보기 → N번째 결과. `score`/`min`/`max` 없이 씁니다.
    결과에 "1번. 머리 먼저"처럼 번호가 붙고, 시작 화면(점수 합산 안내)을 건너뜁니다.
  - **choice 테스트는 `index.json`의 해당 항목에도 `"resultType": "choice"`를 똑같이 적습니다.** 앱 목록은 테스트 파일을 열기 전에 이 값으로 시작 화면을 건너뛸지 정합니다. (검사 스크립트가 두 값이 다르면 알려줌)

### choice 테스트 작성법 (예: 아이스크림 토핑)

**1문항에서 N번째 보기를 고르면 N번째 결과**가 나옵니다. `score`, `min`, `max`는 쓰지 않습니다.
보기와 결과의 **개수와 순서만 맞추면** 됩니다.

```json
{
  "schemaVersion": 1,
  "id": "icecream_topping",
  "title": { "en": "What Your Ice Cream Says\nAbout Your Love Style", "ko": "아이스크림으로 알아보는\n내 연애력 확인 테스트" },
  "resultType": "choice",
  "questions": [
    {
      "type": "image",
      "text": { "en": "If you had to choose a topping\nfor vanilla ice cream, which would it be?", "ko": "당신이 바닐라 아이스크림의 토핑을\n골라야 한다면 어떤 것을 고르시겠습니까?" },
      "options": [
        { "image": "q01_a.webp", "text": { "en": "1. Strawberry jam", "ko": "1. 딸기잼" } },
        { "image": "q01_b.webp", "text": { "en": "2. Matcha syrup", "ko": "2. 녹차시럽" } }
      ]
    }
  ],
  "results": [
    { "title": { "en": "Strawberry jam", "ko": "딸기잼" }, "body": { "en": "…", "ko": "…" } },
    { "title": { "en": "Matcha syrup", "ko": "녹차 시럽" }, "body": { "en": "…", "ko": "…" } }
  ]
}
```
- 결과 화면에는 "1번. 불타는 열정을 가진 사람"처럼 번호가 붙고, 점수는 나오지 않습니다.
- 시작 화면(점수 합산 안내)을 건너뛰고 바로 문항으로 갑니다.
- `index.json`의 해당 항목에도 `"resultType": "choice"`를 똑같이 적습니다.
- 검사 스크립트가 "1문항인지, 보기 수와 결과 수가 같은지"를 확인합니다.
- **JSON에는 데이터만 넣습니다.** (Google Play 정책상 서버에서 실행 코드를 받으면 안 됨)

## 형식을 바꿀 때 (옛 버전 앱 보호)

이미 설치된 앱은 지금 형식만 압니다. 그래서 **"추가는 OK, 변경은 금지"** 원칙을 지킵니다.

**저장소만 고치면 되는 것** (앱 업데이트 불필요)
- 지금 형식(text/image 문항, 보기 2~4개, score/choice 결과)으로 새 테스트 추가
- 기존 테스트의 문구·오타·이미지 수정 (이미지는 새 파일명으로)
- 순서 변경, `visible: false`로 숨기기

**앱 업데이트가 필요한 것**: 새 문항 형식, 새 채점 방식, 결과 화면의 새 요소
1. 앱에 새 형식을 **추가**하고 새 versionCode로 출시
2. 새 형식을 쓰는 테스트의 `minAppVersion`을 그 versionCode로 올림 → 옛 앱 목록에서는 자동으로 숨겨짐

**금지**
- 기존 필드의 뜻 바꾸기 (예: `score`를 다른 의미로 쓰기). 새 의미가 필요하면 새 필드를 추가합니다. 앱은 모르는 필드를 무시합니다.
- 기존 테스트를 새 형식으로 바꾸기. 새 id로 새 테스트를 만듭니다.
- `index.json`의 구조 바꾸기.

앱은 모르는 문항 `type`이 있는 테스트는 열지 않고 "불러오지 못했어요"로 안내합니다. (깨진 화면으로 보이지 않음)

## 검사 스크립트가 잡아주는 것

- 글자 필드에 영어(`en`)나 한국어(`ko`)가 빠진 경우
- JSON 문법 오류, 빠진 필드, 잘못된 type, 보기 개수
- JSON에 적었는데 실제로 없는 이미지, 150KB 넘는 이미지
- 결과 점수 구간이 겹치는 경우
- **나올 수 있는 총점인데 해당 결과가 없는 경우** (모든 조합을 계산해서 확인)
- index.json의 문항 수가 실제와 다른 경우
- index.json과 테스트 파일의 `resultType`이 다른 경우
- `resultType: choice`인데 1문항이 아니거나, 보기 수와 결과 수가 다른 경우

## 준비물

Python 3와 Pillow: `pip3 install Pillow`
