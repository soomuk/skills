#!/usr/bin/env python3
"""skills.json을 읽어 index.html 한 파일을 만든다.

- 페이지에 쓰인 한글·한자만 골라 Noto Serif CJK KR 글꼴을 문서 안에 넣는다(woff2).
  그래서 인터넷 글꼴 없이도 iPhone·Android·PC에서 같은 글꼴로 보인다.
- 로고(assets/logo.jpg)도 문서 안에 넣는다.

쓰는 법:  python3 build.py            → index.html
필요:     pip install fonttools brotli
글꼴:     Noto Serif CJK(KR 포함) .ttc/.otf. 기본 위치에 없으면 --font-regular, --font-bold로 준다.
"""
import argparse, base64, glob, html, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

FONT_GLOBS = {
    "regular": [
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/**/NotoSerifCJK*-Regular.*",
        "~/Library/Fonts/NotoSerifKR-Regular.otf",
        "C:/Windows/Fonts/NotoSerifKR-Regular.otf",
    ],
    "bold": [
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
        "/usr/share/fonts/noto-cjk/NotoSerifCJK-Bold.ttc",
        "/usr/share/fonts/**/NotoSerifCJK*-Bold.*",
        "~/Library/Fonts/NotoSerifKR-Bold.otf",
        "C:/Windows/Fonts/NotoSerifKR-Bold.otf",
    ],
}

E = lambda s: html.escape(str(s), quote=True)
def BR(s):
    """skills.json의 줄바꿈(\\n)을 화면 줄바꿈으로 바꾸고, 라이선스 이름(CC BY-NC-SA 4.0 등)은 한 줄에 붙여 둔다."""
    import re
    t = re.sub(r"(CC BY(?:-[A-Z]{2})* \d\.\d|CC0)", r'<span style="white-space:nowrap">\1</span>', E(s))
    return "".join(f'<span class="fit">{ln}</span>' for ln in t.split("\n"))


# ---------------------------------------------------------------- 글꼴
def find_font(kind, given):
    if given:
        return given
    for pat in FONT_GLOBS[kind]:
        for p in sorted(glob.glob(os.path.expanduser(pat), recursive=True)):
            if os.path.isfile(p):
                return p
    return None


def kr_index(path):
    """TTC 안에서 한국어(KR) 글꼴 번호를 찾는다."""
    if not path.lower().endswith(".ttc"):
        return 0
    from fontTools.ttLib import TTCollection
    for i, f in enumerate(TTCollection(path).fonts):
        name = f["name"].getDebugName(1) or ""
        if "KR" in name:
            return i
    return 0


def subset_woff2(path, text):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    font = TTFont(path, fontNumber=kr_index(path), lazy=False)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.hinting = False
    opts.desubroutinize = True
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    cmap = font.getBestCmap()
    missing = sorted({c for c in text if ord(c) > 32 and ord(c) not in cmap})
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode(), missing


# ---------------------------------------------------------------- 화면 조각
def copy_box(box_id, text, button="복사", light=False):
    cls = "copy light" if light else "copy"
    return (f'<div class="copybox"><pre id="{box_id}">{E(text)}</pre>'
            f'<button type="button" class="{cls}" data-target="{box_id}">{E(button)}</button></div>')


def skill_section(s, n):
    sid = s["id"]
    out = [f'<section class="skill" id="{E(sid)}" aria-labelledby="h-{E(sid)}">']
    out.append(f'<header class="skill-head"><h2 id="h-{E(sid)}">{E(s["name"])}</h2>'
               f'<p class="tagline">{E(s["tagline"])}</p>')
    if s.get("flow"):
        out.append(f'<p class="flow">{E(s["flow"])}</p>')
    out.append('</header>')

    out.append('<h3>설치</h3>')
    out.append(copy_box(f"install-{sid}", s["install_prompt"], "복사"))

    if s.get("invoke"):
        out.append('<h3>불러오기</h3>')
        out.append('<p class="hint">채팅창에 <b>/</b>를 치면 스킬 목록이 뜹니다.<br>아래 이름을 고르거나 그대로 입력한 뒤, 한 칸 띄고 요청을 이어 쓰세요.</p>')
        out.append(copy_box(f"invoke-{sid}", s["invoke"], "복사", light=True))

    out.append('<h3>사용 예시</h3>')
    if s.get("invoke"):
        out.append(f'<p class="hint">스킬을 부른 뒤 이어 쓰거나, 슬래시 없이 그냥 요청해도 Claude가 알아서 이 스킬을 씁니다.</p>')
    for i, ex in enumerate(s.get("examples", []), 1):
        text = ex["text"] if isinstance(ex, dict) else ex
        out.append(copy_box(f"ex-{sid}-{i}", text, "복사", light=True))

    if s.get("note"):
        out.append(f'<p class="note">{BR(s["note"])}</p>')

    more = [f'<li><a href="{E(s["zip"])}">zip 파일 내려받기</a> — 카드가 안 뜨면 Claude 맞춤 설정 → 스킬 → + → Upload a skill로 올리기</li>']
    if s.get("claude_code"):
        more.append('<li>Claude Code' + copy_box(f"cc-{sid}", "\n".join(s["claude_code"]), "복사", light=True) + '</li>')
    out.append('<details><summary>다른 설치 방법</summary><ul class="more">' + "".join(more) + '</ul></details>')
    if s.get("extra"):
        x = s["extra"]
        chips = "".join(f'<span class="chip">{E(t)}</span>' for t in x["items"])
        out.append(f'<details><summary>{E(x["title"])}</summary><div class="chips">{chips}</div></details>')
    out.append(f'<p class="repo"><a href="{E(s["repo"])}">GitHub에서 자세히 →</a></p>')
    out.append('</section>')
    return "".join(out)


def build_body(data):
    site = data["site"]
    skills = data["skills"]
    logo = base64.b64encode(open(os.path.join(HERE, "assets", "logo.jpg"), "rb").read()).decode()
    steps = "".join(
        f'<li><b>{E(st["title"])}</b> {E(st["text"])}</li>' for st in data.get("common_steps", []))
    note = f'<p class="start-note">{E(data["common_note"])}</p>' if data.get("common_note") else ""
    menu = "".join(
        f'<a class="menu-item" href="#{E(s["id"])}" data-id="{E(s["id"])}">'
        f'<span class="mi-name">{E(s["name"])}</span></a>'
        for s in skills)
    sections = "".join(skill_section(s, i) for i, s in enumerate(skills, 1))
    body = f"""
<header class="site-head">
  <img class="logo" src="data:image/jpeg;base64,{logo}" alt="樹默" width="80" height="80">
  <div class="head-txt"><h1><span class="fit">{E(site["title"])}</span></h1><p class="sub"><span class="fit">{E(site["subtitle"])}</span></p></div>
</header>
<main>
<p class="intro">{E(site["intro"])}</p>
<ol class="steps">{steps}</ol>
{note}
<nav class="menu" aria-label="스킬 목록"><div class="menu-list">{menu}</div></nav>
{sections}
</main>
<footer class="site-foot">
  <p><span class="fit">{E(site["org"])} · <a href="{E(site["github"])}">GitHub</a></span>{BR(site.get("license_note") or site["license"] + " License")}</p>
</footer>"""
    return body, logo


CSS = r"""
:root{--paper:#f7f3ea;--card:#fffdf8;--ink:#1f1d1a;--sub:#5b564e;--line:#ddd5c6;--plum:#a8323f;--plum-soft:#f6e3e3;--moss:#3d5a45}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:%%FAMILY%%;font-size:16px;line-height:1.7;word-break:keep-all;overflow-wrap:anywhere}
a{color:var(--plum)}
.site-head{display:flex;align-items:center;gap:16px;max-width:760px;margin:0 auto;padding:32px 20px 4px}
.logo{width:80px;height:80px;border-radius:50%;flex:none}
h1{font-size:1.9rem;line-height:1.3;margin:0}
.sub{margin:0;color:var(--sub)}
main{max-width:760px;margin:0 auto;padding:0 20px}
.intro{font-size:1.1rem;margin:18px 0 10px}
.steps{margin:0;padding-left:1.4em}
.steps li{margin:2px 0}
.steps b{color:var(--plum);margin-right:4px}
.start-note{margin:8px 0 0;color:var(--sub);font-size:.9rem}
.menu{margin:24px 0 16px}
.menu-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
.menu-item{display:block;text-decoration:none;color:inherit;background:var(--card);border:1.5px solid var(--line);border-radius:12px;padding:12px 14px}
.menu-item:hover{border-color:var(--plum)}
.menu-item.on{border-color:var(--plum);box-shadow:0 0 0 3px var(--plum-soft)}
.mi-name{display:block;font-weight:700;font-size:1.05rem}
.mi-tag{display:block;color:var(--sub);font-size:.88rem;line-height:1.55}
.skill{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:24px;margin-bottom:24px;scroll-margin-top:12px}
.js .skill{display:none}
.js .skill.on{display:block}
.skill-head h2{font-size:1.5rem;margin:0;line-height:1.35}
.tagline{margin:4px 0 0;font-size:1.05rem}
.flow{display:inline-block;margin:10px 0 0;background:#efe9dc;border-radius:8px;padding:3px 12px;font-size:.9rem}
h3{font-size:1rem;margin:22px 0 6px;color:var(--plum)}
.copybox{display:flex;align-items:center;gap:10px;background:#f3eee3;border:1px solid var(--line);border-radius:10px;padding:10px 10px 10px 14px;margin:6px 0}
.copybox pre{flex:1;min-width:0;margin:0;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere;font-family:inherit;font-size:.98rem;line-height:1.6}
.copy{flex:none;font:inherit;font-size:.9rem;font-weight:700;color:#fff;background:var(--ink);border:1.5px solid var(--ink);border-radius:8px;padding:8px 16px;cursor:pointer;min-height:44px;white-space:nowrap}
.copy:hover{background:var(--plum);border-color:var(--plum)}
.copy.light{background:transparent;color:var(--ink);font-weight:400}
.copy.light:hover{background:var(--ink);color:#fff}
.copy.done,.copy.light.done{background:var(--moss);border-color:var(--moss);color:#fff}
.hint{margin:0 0 4px;color:var(--sub);font-size:.92rem}
.hint.small{margin-top:4px;font-size:.85rem}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.85rem;background:#efe9dc;padding:1px 6px;border-radius:5px;overflow-wrap:anywhere}
.note{margin:16px 0 0;color:var(--sub);font-size:.92rem;border-left:3px solid var(--plum);padding-left:10px}
details{margin:14px 0 0;font-size:.92rem}
summary{cursor:pointer;color:var(--sub)}
.more{margin:8px 0 0;padding-left:1.2em}
.more li{margin:6px 0}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.chip{font-size:.85rem;background:#efe9dc;border-radius:99px;padding:2px 10px}
.repo{margin:16px 0 0;font-size:.92rem}
.fit{display:block}
.head-txt{min-width:0;flex:1}
.site-foot{max-width:760px;margin:0 auto;padding:12px 20px 36px;color:var(--sub);font-size:.85rem}
@media (max-width:640px){
  .site-head{padding:22px 16px 2px;gap:12px}
  .logo{width:60px;height:60px}
  h1{font-size:clamp(1rem,5vw,1.5rem)}
  .sub{font-size:clamp(.8rem,3.6vw,1rem)}
  main{padding:0 14px}
  .skill{padding:18px 14px}
  .copybox{padding:10px 10px 10px 12px}
  .copy{padding:8px 12px}
  .site-foot{padding:10px 14px 30px}
}
"""

JS = r"""
(function(){
  document.documentElement.classList.add('js');
  var items=[].slice.call(document.querySelectorAll('.menu-item'));
  var secs=[].slice.call(document.querySelectorAll('.skill'));
  function show(id,scroll){
    var hit=secs.filter(function(s){return s.id===id})[0]||secs[0];
    if(!hit)return;
    secs.forEach(function(s){s.classList.toggle('on',s===hit)});
    items.forEach(function(a){a.classList.toggle('on',a.getAttribute('data-id')===hit.id)});
    if(scroll)hit.scrollIntoView({behavior:'smooth',block:'start'});
  }
  items.forEach(function(a){a.addEventListener('click',function(e){
    e.preventDefault();var id=a.getAttribute('data-id');
    if(history.replaceState)history.replaceState(null,'','#'+id);
    show(id,true);
  })});
  window.addEventListener('hashchange',function(){show(location.hash.slice(1),true)});
  show(location.hash.slice(1),false);

  function fallback(t){var ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');
    ta.style.position='fixed';ta.style.top='-1000px';document.body.appendChild(ta);ta.select();
    try{document.execCommand('copy')}catch(e){}document.body.removeChild(ta)}
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('.copy');if(!b)return;
    var t=document.getElementById(b.getAttribute('data-target')).textContent;
    var label=b.getAttribute('data-label')||b.textContent;b.setAttribute('data-label',label);
    function ok(){b.textContent='복사됨 ✓';b.classList.add('done');
      setTimeout(function(){b.textContent=label;b.classList.remove('done')},1800)}
    if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok,function(){fallback(t);ok()})}
    else{fallback(t);ok()}
  });
})();
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "skills.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"))
    ap.add_argument("--font-regular")
    ap.add_argument("--font-bold")
    a = ap.parse_args()

    data = json.load(open(a.data, encoding="utf-8"))
    ids = [s["id"] for s in data["skills"]]
    if len(ids) != len(set(ids)):
        sys.exit("오류: skills.json에 같은 id가 두 번 있습니다.")

    body, logo = build_body(data)
    site = data["site"]
    # 글꼴에 넣을 글자: 페이지 전체 글자 + 기본 문장부호·영숫자 + 복사 버튼 문구
    import re
    visible = re.sub(r"<[^>]+>", " ", body + JS + CSS)
    visible = html.unescape(visible)
    text = visible + "".join(chr(c) for c in range(0x20, 0x7F)) + "복사됨✓·→…「」『』“”‘’"

    family = "'Noto Serif KR','Noto Serif CJK KR','Apple SD Gothic Neo','Malgun Gothic',serif"
    faces = ""
    for kind, weight, given in (("regular", 400, a.font_regular), ("bold", 700, a.font_bold)):
        path = find_font(kind, given)
        if not path:
            print(f"경고: {kind} 글꼴을 찾지 못해 기기 글꼴로 대신합니다.", file=sys.stderr)
            continue
        b64, missing = subset_woff2(path, text)
        faces += (f"@font-face{{font-family:'SoomukSerif';font-weight:{weight};font-style:normal;"
                  f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}\n")
        if missing:
            print(f"경고: 글꼴에 없는 글자 {''.join(missing)}", file=sys.stderr)
        print(f"글꼴({kind}): {os.path.basename(path)} → {len(b64)*3//4//1024} KB")
    if faces:
        family = "'SoomukSerif'," + family

    desc = site["intro"]
    doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(site["title"])} — {E(site["subtitle"])}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(site["title"])}">
<meta property="og:description" content="{E(desc)}">
<meta name="theme-color" content="#f7f3ea">
<link rel="icon" href="data:image/jpeg;base64,{logo}">
<link rel="apple-touch-icon" href="data:image/jpeg;base64,{logo}">
<style>
{faces}{CSS.replace("%%FAMILY%%", family)}
</style>
</head>
<body>
{body}
<script>{JS}</script>
</body>
</html>
"""
    # UTF-8 BOM을 붙여 어떤 환경에서도 한글이 깨지지 않게 한다.
    with open(a.out, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(doc)
    print(f"완성: {a.out} ({os.path.getsize(a.out)//1024} KB, 스킬 {len(ids)}개)")


if __name__ == "__main__":
    main()
