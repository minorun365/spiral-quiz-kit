# 解説カード・問題の解説に入れる図の部品。questions.py から import して使う。
# 図はHTMLとCSSで描く（SVGの文字は折り返さないため、スマホ幅で読めなくなる）。
# 描画は template.html の figHTML()。ここでは JSON にできる dict を組むだけ。
#
# 文字はどれも短く。見出しは全角12字前後、補足は全角30字前後を目安にする。
#
#   flow(cap, steps, end=None, h=False)   手順・データの流れ。end で最後に2〜3方向へ分岐
#   cycle(cap, steps, back)              ループ（最後から最初へ戻る矢印つき）
#   vs(cap, ng, ok)                      よくある誤り（左）と正しい形（右）の対比
#   layers(cap, rows, hl=None)           上から下へ重なる層・選択肢の棚。hl は強調する行
#   hub(cap, top, kids, bottom=None)     親と子、子の結果の集約
#   matrix(cap, cols, rows)              条件×選択肢の早見表（列は3つまで）
#   bars(cap, items, unit='')            数値の比較。items は (ラベル, 数値, 補足)
#
# steps / rows / kids の各要素は (見出し, 補足) か (見出し, 補足, 'ok'|'ng'|'key')。
# 3つ目は色。ok=正しい側（緑）、ng=誤り・落とし穴（赤）、key=注目点（金）。


def _items(xs):
    out = []
    for x in xs:
        x = list(x) + [''] * (3 - len(x))
        out.append(dict(t=x[0], s=x[1], tone=x[2]))
    return out


def flow(cap, steps, end=None, h=False):
    return dict(k='flow', cap=cap, steps=_items(steps), end=_items(end or []), h=h)


def cycle(cap, steps, back):
    return dict(k='cycle', cap=cap, steps=_items(steps), back=back)


def vs(cap, ng, ok):
    """ng / ok は (見出し, [項目, ...])"""
    return dict(k='vs', cap=cap, ng=dict(t=ng[0], items=list(ng[1])), ok=dict(t=ok[0], items=list(ok[1])))


def layers(cap, rows, hl=None):
    r = _items(rows)
    if hl is not None:
        for i in ([hl] if isinstance(hl, int) else hl):
            r[i]['tone'] = r[i]['tone'] or 'key'
    return dict(k='layers', cap=cap, rows=r)


def hub(cap, top, kids, bottom=None):
    return dict(k='hub', cap=cap, top=_items([top])[0], kids=_items(kids),
                bottom=_items([bottom])[0] if bottom else None)


def matrix(cap, cols, rows):
    """cols は見出し行（先頭は行ラベルの列名）。rows は [行ラベル, セル, ...]。
    セル文字の先頭に ○ / × / △ を置くと色が付く"""
    return dict(k='matrix', cap=cap, cols=list(cols), rows=[list(r) for r in rows])


def bars(cap, items, unit=''):
    return dict(k='bars', cap=cap, unit=unit,
                items=[dict(t=i[0], v=i[1], s=(i[2] if len(i) > 2 else ''), tone=(i[3] if len(i) > 3 else '')) for i in items])
