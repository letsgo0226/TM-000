#!/usr/bin/env python3
"""Offline development-only generator; the produced G20 Quine NEVER imports this file."""
from pathlib import Path

TEMPLATE = r'''import sys
t=%r
p=t%%t
c="python3 -c $'"+p.replace("\\","\\\\").replace("'","\\'").replace("\n","\\n")+"'\n"
b=c.encode()
m=int(sum(b)%%3==0)
pr=[];k=2
while len(pr)<256:
 if all(k%%x for x in pr if x*x<=k):pr.append(k)
 k+=1
B=257 if m else 2048
f=lambda x:x+1 if m else pr[x]
G=1
for x in b:G=G*B+f(x)
rev={v:i for i,v in enumerate(pr)}
a=[]
while G>1:
 G,x=divmod(G,B)
 a.append(x-1 if m else rev[x])
if bytes(a[::-1])!=b:raise SystemExit("BLOCKED")
sys.stdout.buffer.write(b)'''


def build(marker: str = "") -> bytes:
    """Construct a literal single-physical-line shell Quine, optionally with a no-op source variant."""
    if not isinstance(marker, str) or len(marker) > 32:
        raise ValueError("bad variant marker")
    template = TEMPLATE
    if marker:
        template = template.replace('b=c.encode()\n', 'b=c.encode()\nmarker=' + repr(marker) + '\n')
    python_source = template % template
    escaped = (python_source.replace('\\', '\\\\')
               .replace("'", "\\'")
               .replace('\n', '\\n'))
    return ("python3 -c $'" + escaped + "'\n").encode('utf-8')


if __name__ == '__main__':
    p = Path(__file__).with_name('Universal_G_G20_Self_Quine_2KB.sh')
    p.write_bytes(build())
    print('Generated:', p, 'bytes=', p.stat().st_size)
