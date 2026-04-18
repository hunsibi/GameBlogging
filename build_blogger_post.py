import base64
import re
import os

input_html = r"d:\WorkSpace\GameBlogging\2_작가요원\post_20260404_TRUE_FINAL.html"
output_html = r"d:\WorkSpace\GameBlogging\2_작가요원\post_20260404_Blogger.html"
shared_dir = r"d:\WorkSpace\GameBlogging\shared\4.4"

with open(input_html, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 엉뚱했던 하이라이트 박스 및 태그 HTML 걷어내기
content = re.sub(r'<div class="focus-rect"></div>\s*', '', content)
content = re.sub(r'<div class="focus-tag">.*?</div>\s*', '', content)

# 2. 관련 CSS 덩어리 걷어내기
content = re.sub(r'/\* HIGHLIGHT OVERLAY \*/.*?(?=\.footer)', '', content, flags=re.DOTALL)

# 3. Base64 이미지로 교체 (복붙 호환성 극대화)
def repl_img(match):
    src = match.group(1)
    filename = src.split('/')[-1]
    filepath = os.path.join(shared_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as imgf:
            b64 = base64.b64encode(imgf.read()).decode('utf-8')
            ext = filename.split('.')[-1].lower()
            mime_type = f"image/{ext}" if ext != 'jpg' else 'image/jpeg'
            new_src = f"data:{mime_type};base64,{b64}"
            return f'src="{new_src}"'
    return match.group(0)

# src="경로" 부분을 찾아서 변환
content = re.sub(r'src="(\.\./shared/4\.4/[^"]+)"', repl_img, content)

with open(output_html, 'w', encoding='utf-8') as f:
    f.write(content)
print("Blogger optimized HTML generated successfully with embedded images!")
