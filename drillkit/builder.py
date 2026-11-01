"""問題を書いた Python モジュールから、1枚で動く問題集の HTML を組み立てる。

    import builder, questions
    builder.build(questions, out='dist/quiz.html', key='my-quiz', title='…', short='…')

問題の書き方は docs/question-format.md、画面の動きは docs/how-it-works.md。
"""
import hashlib
import json
import pathlib
import random
import sys

KIT = pathlib.Path(__file__).resolve().parent


def shuffled_order(qid, n=4):
    """問題ごとに固定の並び順。正解の位置が書いた順に偏らないようにする"""
    seed = int(hashlib.sha256(qid.encode()).hexdigest()[:8], 16)
    order = list(range(n))
    random.Random(seed).shuffle(order)
    return order


def check(sections):
    """書き漏れを列挙する。build() は警告として出し、HTMLは書き出す"""
    probs = []
    ids = set()
    for s in sections:
        for q in s['questions']:
            if q['id'] in ids:
                probs.append(f"{q['id']}: id が重複している")
            ids.add(q['id'])
            multi = isinstance(q['ans'], list)
            ans = set(q['ans']) if multi else {q['ans']}
            if len(q['opts']) != (5 if multi else 4):
                probs.append(f"{q['id']}: 選択肢の数が合わない（単一選択は4つ、複数選択は5つ）")
            if q['trap'] in ans:
                probs.append(f"{q['id']}: trap が正解に含まれている")
            want = set(range(len(q['opts']))) - ans - {q['trap']}
            if set(int(k) for k in (q.get('rest') or {})) != want:
                probs.append(f"{q['id']}: rest の添字が {sorted(want)} になっていない")
            for k in ('why', 'trapwhy'):
                if not q.get(k):
                    probs.append(f"{q['id']}: {k} が無い")
    return probs


def auto_spiral(sections, per=10):
    """10問前後ずつの周回を組む。どの周にも全分野が入るよう、分野の問題数に比例して並べてから切る。
    分野の中では書いた順に前の周へ入るので、大事な問題を各分野の先頭に書けば、前の周ほど効く並びになる"""
    seq = []
    for si, s in enumerate(sections):
        n = len(s['questions'])
        seq += [((i + 0.5) / n, si, q['id']) for i, q in enumerate(s['questions'])]
    ids = [x[2] for x in sorted(seq)]
    k = max(1, round(len(ids) / per))
    size, extra = divmod(len(ids), k)
    rounds, at = [], 0
    for r in range(k):
        m = size + (1 if r < extra else 0)
        rounds.append(ids[at:at + m])
        at += m
    return dict(rounds=rounds, dom={q['id']: s['title'] for s in sections for q in s['questions']})


def build(Q, *, out, key, title, short, desc='', note='', rate_label='', mock=None, spiral=None, sync=None, icon=None):
    """Q.SECTIONS から HTML を書き出す。

    out         書き出すファイル
    key         記録の保存キー（localStorage と同期APIで使う）。問題集ごとに変える
    title       ページのタイトル。short は上のバーとホーム画面の名前
    note        「成績・設定」の下に出す説明
    rate_label  分野ごとに出す数値の名前（分野に rate を書いたときだけ。例 '配点'）
    mock        dict(scenarios=2, per=5) で「本番形式」。分野を無作為に選んで通しで解く
    spiral      周回を自分で決めるとき dict(rounds=[[id, ...], ...], dom={id: '分野名'})。省略すると auto_spiral
    sync        端末間で同期するとき dict(url='https://…/state/my-quiz', headers={...})。省略するとブラウザにだけ保存
    icon        ホーム画面のアイコン（out からの相対パス）
    """
    sections_src = Q.SECTIONS
    probs = check(sections_src)
    if probs:
        print('\n'.join(['⚠ 未完成の項目'] + probs[:40]), file=sys.stderr)
    if spiral is None:
        spiral = auto_spiral(sections_src)

    cards = []
    for s in sections_src:
        L = s.get('lesson')
        if L:
            figs = [f for f in [L.get('fig')] + list(L.get('figs') or []) if f]
            cards.append(dict(type='lesson', id='L-' + s['id'], sec=s['id'], title=s['title'],
                              rate=s.get('rate', ''), lead=L['lead'], points=L['points'], figs=figs))
        for q in s['questions']:
            cards.append(dict(type='q', id=q['id'], sec=s['id'], stem=q['stem'], opts=q['opts'],
                              ans=q['ans'], trap=q['trap'], why=q['why'], trapwhy=q['trapwhy'],
                              deep=q.get('deep', ''), rest={str(k): v for k, v in (q.get('rest') or {}).items()},
                              fig=q.get('fig'), order=shuffled_order(q['id'], len(q['opts']))))

    sections = [dict(id=s['id'], title=s['title'], rate=(s.get('rate', '') if rate_label else ''),
                     n=len(s['questions']), scenario=s.get('scenario', '')) for s in sections_src]
    data = json.dumps(dict(key=key, rateLabel=rate_label, sections=sections, cards=cards,
                           mock=mock, spiral=spiral, sync=sync), ensure_ascii=False)
    data = data.replace('</', '<\\/')

    def esc(x):
        return str(x).replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')

    tpl = (KIT / 'template.html').read_text(encoding='utf-8')
    html = (tpl.replace('__ICON_TAG__', f'<link rel="apple-touch-icon" href="{esc(icon)}">' if icon else '')
            .replace('__TITLE__', esc(title)).replace('__SHORT__', esc(short)).replace('__DESC__', esc(desc))
            .replace('__NOTE__', esc(note)).replace('__DATA__', data))
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    nq = sum(len(s['questions']) for s in sections_src)
    print(f'書き出し: {out}（{nq}問・{len(spiral["rounds"])}周）')
    return out
