"""source/<테스트id>/ 의 원본 이미지를 images/<테스트id>/ 에 WebP로 변환해 넣는다.

- 짧은 변이 SHORT_SIDE(600px)보다 크면 600px로 줄이고, 작으면 그대로 둔다 (확대하지 않음).
  정사각형은 600x600, 4:3은 800x600이 된다. 비율은 바꾸지 않는다 (README의 이미지 규격대로 준비).
- 파일명은 확장자만 .webp로 바꾸고 그대로 쓴다.
- 이미 images/ 에 같은 이름이 있으면 덮어쓰지 않고 건너뛴다.
  (앱이 이미지를 캐시하므로, 그림을 고칠 땐 q01_a_v2.png 처럼 새 이름으로 넣는다)

사용법:  python3 scripts/build_images.py            # 전체
         python3 scripts/build_images.py animal_type  # 한 테스트만
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORT_SIDE = 600
QUALITY = 80
EXTS = (".png", ".jpg", ".jpeg", ".webp")


def build(test_id):
    src_dir = os.path.join(ROOT, "source", test_id)
    out_dir = os.path.join(ROOT, "images", test_id)
    os.makedirs(out_dir, exist_ok=True)
    made = skipped = 0
    for name in sorted(os.listdir(src_dir)):
        base, ext = os.path.splitext(name)
        if ext.lower() not in EXTS:
            continue
        out = os.path.join(out_dir, base + ".webp")
        if os.path.exists(out):
            skipped += 1
            continue
        with Image.open(os.path.join(src_dir, name)) as im:
            im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
            short = min(im.size)
            if short > SHORT_SIDE:
                scale = SHORT_SIDE / short
                im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
            im.save(out, "WEBP", quality=QUALITY, method=6)
        made += 1
        print("  +", os.path.relpath(out, ROOT), "%dKB" % (os.path.getsize(out) // 1024))
    print("%s: 새로 %d개, 기존 %d개 건너뜀" % (test_id, made, skipped))


def main():
    source = os.path.join(ROOT, "source")
    ids = sys.argv[1:] or sorted(d for d in os.listdir(source) if os.path.isdir(os.path.join(source, d)))
    for test_id in ids:
        build(test_id)


if __name__ == "__main__":
    main()
