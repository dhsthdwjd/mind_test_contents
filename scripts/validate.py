"""push 전에 index.json 과 tests/*.json 을 검사한다. 오류가 하나라도 있으면 종료 코드 1.

검사 항목
- JSON 문법, 필수 필드, 문항 type(image/text)별 보기 형식
- 참조한 이미지 파일이 images/<테스트id>/ 에 실제로 있는지, 너무 크지 않은지
- 결과 점수 구간이 겹치지 않는지, 나올 수 있는 모든 총점이 어떤 결과에든 들어가는지
- index.json 의 questionCount 가 실제 문항 수와 같은지
- index.json 의 resultType 이 테스트 파일과 같은지
- resultType 이 choice 면 1문항이고, 보기 점수와 결과(min=max)가 1:1로 맞는지
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_IMAGE_KB = 150
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def check_image(test_id, name, where):
    if not isinstance(name, str) or not name:
        err("%s: 이미지 이름이 비어 있음" % where)
        return
    path = os.path.join(ROOT, "images", test_id, name)
    if not os.path.isfile(path):
        err("%s: 이미지 없음 images/%s/%s" % (where, test_id, name))
    elif os.path.getsize(path) > MAX_IMAGE_KB * 1024:
        warnings.append("%s: %s 가 %dKB (권장 %dKB 이하)"
                        % (where, name, os.path.getsize(path) // 1024, MAX_IMAGE_KB))


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

    if doc.get("id") != test_id:
        err("%s: id(%s)가 index.json 의 id(%s)와 다름" % (where, doc.get("id"), test_id))
    if not doc.get("title"):
        err("%s: title 없음" % where)

    questions = doc.get("questions") or []
    if not questions:
        err("%s: questions 비어 있음" % where)
    for i, q in enumerate(questions, start=1):
        qw = "%s 문항 %d" % (where, i)
        qtype = q.get("type")
        if qtype not in ("image", "text"):
            err("%s: type 은 image 또는 text (현재 %r)" % (qw, qtype))
        if not q.get("text"):
            err("%s: text 없음" % qw)
        if "image" in q:
            check_image(test_id, q["image"], qw)
        options = q.get("options") or []
        if not 2 <= len(options) <= 4:
            err("%s: 보기는 2~4개 (현재 %d개)" % (qw, len(options)))
        for k, o in enumerate(options, start=1):
            ow = "%s 보기 %d" % (qw, k)
            if not isinstance(o.get("score"), int):
                err("%s: score 는 정수여야 함" % ow)
            if qtype == "image":
                check_image(test_id, o.get("image"), ow)
            elif qtype == "text" and not o.get("text"):
                err("%s: text 없음" % ow)

    results = doc.get("results") or []
    if not results:
        err("%s: results 비어 있음" % where)
    ranges = []
    for i, r in enumerate(results, start=1):
        rw = "%s 결과 %d" % (where, i)
        lo, hi = r.get("min"), r.get("max")
        if not isinstance(lo, int) or not isinstance(hi, int) or lo > hi:
            err("%s: min/max 가 잘못됨 (%r~%r)" % (rw, lo, hi))
            continue
        if not r.get("title") or not r.get("body"):
            err("%s: title/body 없음" % rw)
        if "image" in r:
            check_image(test_id, r["image"], rw)
        ranges.append((lo, hi, i))
    ranges.sort()
    for (a_lo, a_hi, a), (b_lo, b_hi, b) in zip(ranges, ranges[1:]):
        if b_lo <= a_hi:
            err("%s: 결과 %d(%d~%d)과 결과 %d(%d~%d) 구간이 겹침" % (where, a, a_lo, a_hi, b, b_lo, b_hi))
    if questions and ranges:
        uncovered = sorted(t for t in reachable_totals(questions)
                           if not any(lo <= t <= hi for lo, hi, _ in ranges))
        if uncovered:
            err("%s: 이 총점들은 해당 결과가 없음 %s" % (where, uncovered))

    result_type = doc.get("resultType", "score")
    if result_type not in ("score", "choice"):
        err("%s: resultType 은 score 또는 choice (현재 %r)" % (where, result_type))
    elif result_type == "choice":
        check_choice(where, questions, results)

    if entry.get("resultType", "score") != result_type:
        err("index.json %s: resultType(%r)이 테스트 파일의 resultType(%r)과 다름 "
            "(앱 목록이 시작 화면을 건너뛸지 이 값으로 정함)"
            % (test_id, entry.get("resultType", "score"), result_type))

    if entry.get("questionCount") != len(questions):
        err("index.json %s: questionCount(%r)와 실제 문항 수(%d)가 다름"
            % (test_id, entry.get("questionCount"), len(questions)))


def check_choice(where, questions, results):
    """choice: 고른 보기 = 결과. 보기 i번의 score 와 결과 i번의 min=max 가 같아야 번호가 맞는다."""
    if len(questions) != 1:
        err("%s: resultType choice 는 문항이 1개여야 함 (현재 %d개)" % (where, len(questions)))
        return
    options = questions[0].get("options") or []
    if len(options) != len(results):
        err("%s: choice 는 보기 수(%d)와 결과 수(%d)가 같아야 함" % (where, len(options), len(results)))
        return
    for i, (o, r) in enumerate(zip(options, results), start=1):
        if r.get("min") != r.get("max"):
            err("%s: choice 결과 %d 는 min 과 max 가 같아야 함" % (where, i))
        elif o.get("score") != r.get("min"):
            err("%s: choice 보기 %d(score %r)와 결과 %d(min/max %r)가 맞지 않음"
                % (where, i, o.get("score"), i, r.get("min")))


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
        for key in ("title", "file", "minAppVersion"):
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
