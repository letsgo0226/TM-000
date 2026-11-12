#!/usr/bin/env python3
"""Build G26 exact formal-log tape simulator from the preserved G23 one-liner.

Development tool only. G26 execution never reads this builder, application
contracts, or any upstream files. The algorithm contains no floating logs.
"""
from pathlib import Path
import ast

HERE = Path(__file__).resolve().parent


def build(source: bytes) -> bytes:
    raw = source.decode('utf-8')
    if not (raw.startswith("python3 -c $'") and raw.endswith("'\n") and raw.count('\n') == 1):
        raise ValueError('not the archived G23 one-line Bash program')
    py = ast.literal_eval("'" + raw[len("python3 -c $'"):-2] + "'")
    substitutions = [
        ('t={};q=10;i=s=0;G=1', 't={};l={};q=10;i=s=0;G=1'),
        ('  if new:t[i]=new', '  l[i]=l.get(i,0)+new-old\n  if not l[i]:l.pop(i)\n  if new:t[i]=new'),
        ('C(N==1 and u==t)', 'C(N==1 and u==t==l)'),
        ("version='G23'", "version='G26'"),
        ('sha_used=False,orders=0)',
         'sha_used=False,orders=0,formal_log_exact=True,log_terms=len(l),'
         'g22_g23_equivalent=True,application_layer=False,g27_integrated=False)'),
    ]
    for original, replacement in substitutions:
        if py.count(original) != 1:
            raise ValueError('upstream one-liner version changed: ' + original)
        py = py.replace(original, replacement)
    encoded = py.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    result = ("python3 -c $'" + encoded + "'\n").encode('utf-8')
    if result.count(b'\n') != 1 or len(result) > 2048:
        raise ValueError('G26 exceeds one-line 2KB contract')
    return result


if __name__ == '__main__':
    parent = HERE/'Universal_G_G23_Prime_Power_2KB.sh'
    result = build(parent.read_bytes())
    path = HERE/'Universal_G_G26_Exact_Formal_Log_2KB.sh'
    path.write_bytes(result)
    print('G26 bytes:', len(result), 'physical_lines:', result.count(b'\n'))
