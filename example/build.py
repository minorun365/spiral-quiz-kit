#!/usr/bin/env python3
"""見本の問題集を組む。  python3 example/build.py  →  example/python-basics.html"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'drillkit'))
sys.path.insert(0, str(HERE))
import builder  # noqa: E402
import questions  # noqa: E402

builder.build(
    questions,
    out=HERE / 'python-basics.html',
    key='python-basics',
    title='Python の基礎｜周回で解く21問',
    short='Python の基礎',
    desc='Python の基礎を10問前後ずつの周回で解く問題集の見本。',
    note='見本の問題集。10問前後ずつの周に分けてあり、どの周も3分野を一通り回る。PCは 1〜5 で選択、← → でめくる。',
)
