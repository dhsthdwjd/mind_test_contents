"""push 전에 index.json 과 tests/*.json 을 검사한다. 오류가 하나라도 있으면 종료 코드 1.

검사 항목
- JSON 문법, 필수 필드, 문항 type(image/text)별 보기 형식
- 모든 글자 필드가 {"en": "...", "ko": "..."} 이고 두 언어 모두 채워져 있는지
- 참조한 이미지 파일이 images/<테스트id>/ 에 실제로 있는지, 너무 크지 않은지
- 이미지 규격: 그림 보기는 정사각형, 문항·결과 그림은 4:3, 모두 높이 600px 이상 (LEGACY_TESTS 제외)
- 결과 점수 구간이 겹치지 않는지, 나올 수 있는 모든 총점이 어떤 결과에든 들어가는지
- index.json 의 questionCount 가 실제 문항 수와 같은지
- index.json 의 resultType 이 테스트 파일과 같은지
- resultType 이 choice 면 1문항이고, 보기 수와 결과 수가 같은지 (N번 보기 → N번 결과)
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_IMAGE_KB = 150
MIN_SIDE = 600          # 그림 보기: 한 변, 문항·결과 그림: 높이
RATIO_TOLERANCE = 0.02  # 2%
SQUARE = (1, 1)         # 그림 보기
WIDE = (4, 3)           # 문항 위 그림, 결과 그림
# 이미지 규격(README)이 생기기 전에 만든 테스트. 규격 검사만 건너뛴다.
LEGACY_TESTS = {"shy_drawing", "animal_type", "charm_flower", "first_impression"}
errors, warnings = [], []


def err(msg):
    errors.append(msg)


LANGUAGES = ("en", "ko")


def check_text(value, where, required=True):
    """글자 필드는 {"en": "...", "ko": "..."} 이고 두 언어 모두 비어 있으면 안 된다."""
    if value is None:
        if required:
            err("%s: 없음" % where)
        return
    if not isinstance(value, dict):
        err('%s: {"en": "...", "ko": "..."} 형식이어야 함 (현재 %r)' % (where, value))
        return
    for lang in LANGUAGES:
        if not isinstance(value.get(lang), str) or not value[lang].strip():
            err("%s: %s 글자가 비어 있음" % (where, lang))
    extra = set(value) - set(LANGUAGES)
    if extra:
        err("%s: 알 수 없는 언어 %s (en, ko 만 사용)" % (where, sorted(extra)))


def check_image(test_id, name, where, shape=None):
    """shape: SQUARE 또는 WIDE 면 비율과 최소 크기도 검사한다."""
    if not isinstance(name, str) or not name:
        err("%s: 이미지 이름이 비어 있음" % where)
        return
    path = os.path.join(ROOT, "images", test_id, name)
    if not os.path.isfile(path):
        err("%s: 이미지 없음 images/%s/%s" % (where, test_id, name))
        return
    if os.path.getsize(path) > MAX_IMAGE_KB * 1024:
        warnings.append("%s: %s 가 %dKB (권장 %dKB 이하)"
                        % (where, name, os.path.getsize(path) // 1024, MAX_IMAGE_KB))
    if shape is None or test_id in LEGACY_TESTS:
        return
    with Image.open(path) as im:
        w, h = im.size
    rw, rh = shape
    label = "정사각형" if shape == SQUARE else "4:3"
    if abs(w * rh - h * rw) > RATIO_TOLERANCE * h * rw:
        err("%s: %s 는 %s 이어야 함 (현재 %dx%d)" % (where, name, label, w, h))
    if h < MIN_SIDE:
        err("%s: %s 는 높이 %dpx 이상이어야 함 (현재 %dx%d). 원본을 더 크게 준비하세요"
            % (where, name, MIN_SIDE, w, h))


def reachable_totals(questions):
    totals = {0}
    for q in questions:
        scores = {o.get("score") for o in q.get("options", []) if isinstance(o.get("score"), int)}
        totals = {t + s for t in totals for s in scores}
    return totals


def check_test(entry):
    test_id = entry.get("id")
    where = "tests/%s.json" % test_id
    path = os.path.join(ROOT, entry.get("file", ""))
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except FileNotFoundError:
        err("%s: 파일 없음" % entry.get("file"))
        return
    except json.JSONDecodeError as e:
        err("%s: JSON 문법 오류 %s" % (where, e))
        return

    result_type = doc.get("resultType", "score")
    if result_type not in ("score", "choice"):
        err("%s: resultType 은 score 또는 choice (현재 %r)" % (where, result_type))
        return
    choice = result_type == "choice"

    if doc.get("id") != test_id:
        err("%s: id(%s)가 index.json 의 id(%s)와 다름" % (where, doc.get("id"), test_id))
    check_text(doc.get("title"), "%s title" % where)

    questions = doc.get("questions") or []
    if not questions:
        err("%s: questions 비어 있음" % where)
    for i, q in enumerate(questions, start=1):
        qw = "%s 문항 %d" % (where, i)
        qtype = q.get("type")
        if qtype not in ("image", "text"):
            err("%s: type 은 image 또는 text (현재 %r)" % (qw, qtype))
        check_text(q.get("text"), "%s text" % qw)
        if "image" in q:
            check_image(test_id, q["image"], qw, WIDE)
        options = q.get("options") or []
        if not 2 <= len(options) <= 4:
            err("%s: 보기는 2~4개 (현재 %d개)" % (qw, len(options)))
        for k, o in enumerate(options, start=1):
            ow = "%s 보기 %d" % (qw, k)
            if not choice and not isinstance(o.get("score"), int):
                err("%s: score 는 정수여야 함" % ow)
            if qtype == "image":
                check_image(test_id, o.get("image"), ow, SQUARE)
                check_text(o.get("text"), "%s text" % ow, required=False)
            else:
                check_text(o.get("text"), "%s text" % ow)

    results = doc.get("results") or []
    if not results:
        err("%s: results 비어 있음" % where)
    ranges = []
    for i, r in enumerate(results, start=1):
        rw = "%s 결과 %d" % (where, i)
        check_text(r.get("title"), "%s title" % rw)
        check_text(r.get("body"), "%s body" % rw)
        if "image" in r:
            check_image(test_id, r["image"], rw, WIDE)
        if choice:
            continue
        lo, hi = r.get("min"), r.get("max")
        if not isinstance(lo, int) or not isinstance(hi, int) or lo > hi:
            err("%s: min/max 가 잘못됨 (%r~%r)" % (rw, lo, hi))
            continue
        ranges.append((lo, hi, i))
    if not choice:
        ranges.sort()
        for (a_lo, a_hi, a), (b_lo, b_hi, b) in zip(ranges, ranges[1:]):
            if b_lo <= a_hi:
                err("%s: 결과 %d(%d~%d)과 결과 %d(%d~%d) 구간이 겹침" % (where, a, a_lo, a_hi, b, b_lo, b_hi))
        if questions and ranges:
            uncovered = sorted(t for t in reachable_totals(questions)
                               if not any(lo <= t <= hi for lo, hi, _ in ranges))
            if uncovered:
                err("%s: 이 총점들은 해당 결과가 없음 %s" % (where, uncovered))
    else:
        check_choice(where, questions, results)

    if entry.get("resultType", "score") != result_type:
        err("index.json %s: resultType(%r)이 테스트 파일의 resultType(%r)과 다름 "
            "(앱 목록이 시작 화면을 건너뛸지 이 값으로 정함)"
            % (test_id, entry.get("resultType", "score"), result_type))

    if entry.get("questionCount") != len(questions):
        err("index.json %s: questionCount(%r)와 실제 문항 수(%d)가 다름"
            % (test_id, entry.get("questionCount"), len(questions)))


def check_choice(where, questions, results):
    """choice: 1문항에서 N번째 보기를 고르면 N번째 결과. score/min/max 는 쓰지 않는다."""
    if len(questions) != 1:
        err("%s: resultType choice 는 문항이 1개여야 함 (현재 %d개)" % (where, len(questions)))
        return
    options = questions[0].get("options") or []
    if len(options) != len(results):
        err("%s: choice 는 보기 수(%d)와 결과 수(%d)가 같아야 함 (N번 보기 → N번 결과)"
            % (where, len(options), len(results)))
    if any("score" in o for o in options) or any("min" in r or "max" in r for r in results):
        warnings.append("%s: choice 테스트는 score/min/max 를 쓰지 않음 (무시됨). 지워도 됩니다" % where)


def main():
    try:
        with open(os.path.join(ROOT, "index.json"), encoding="utf-8") as f:
            index = json.load(f)
    except json.JSONDecodeError as e:
        print("index.json: JSON 문법 오류", e)
        sys.exit(1)

    seen = set()
    for entry in index.get("tests", []):
        test_id = entry.get("id")
        if not test_id:
            err("index.json: id 없는 항목")
            continue
        if test_id in seen:
            err("index.json: id 중복 %s" % test_id)
        seen.add(test_id)
        check_text(entry.get("title"), "index.json %s title" % test_id)
        for key in ("file", "minAppVersion"):
            if key not in entry:
                err("index.json %s: %s 없음" % (test_id, key))
        if "thumbnail" in entry:
            err("index.json %s: thumbnail 은 더 이상 쓰지 않음. 항목을 지우세요" % test_id)
        check_test(entry)

    for w in warnings:
        print("주의:", w)
    for e in errors:
        print("오류:", e)
    if errors:
        print("\n검사 실패: 오류 %d개. 고친 뒤 다시 실행하세요." % len(errors))
        sys.exit(1)
    print("검사 통과: 테스트 %d개, 주의 %d개" % (len(seen), len(warnings)))


if __name__ == "__main__":
    main()
