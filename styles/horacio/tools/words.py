"""Promesas: word fixes, 1-3 word caption chunks, hook and top titles with per-word keyframe times -> ov/data.js"""
import json, re
import os
P = os.environ.get('PROJ', '.')  # project folder: proj/, ov/, tools/
W = json.load(open(P + '/proj/cut_words.json'))
T = {48: 'cuándo', 102: 'dijo:', 169: 'Párate', 257: 'verdad,'}
for i, w in enumerate(W):
    if i in T: w['text'] = T[i]
at = lambda k: round(W[k]['start'], 3)
end = lambda k: round(W[k]['end'], 3)
ch, cur = [], []
for k, w in enumerate(W):
    cur.append(k)
    nxt = W[k + 1] if k + 1 < len(W) else None
    if re.search(r'[.,?!:]$', w['text']) or len(cur) == 3 or nxt is None or nxt['start'] - w['end'] > 0.35:
        ch.append(cur); cur = []
EMPH = {6, 31, 37, 56, 59, 70, 89, 104, 106, 111, 133, 145, 168, 175, 180, 190, 197, 225, 249, 257, 265, 267, 268, 275}
caps = [[{'t': W[k]['text'], 's': at(k), 'e': int(k in EMPH)} for k in c] for c in ch]
END = sum(p['frames'] for p in json.load(open(P + '/proj/edl.json'))) / 30
def L(text, t, gap=.09):
    """one title line; *word* = gold. every word punches in, staggered from t"""
    return [{'w': x.strip('*'), 'g': int(x.startswith('*')), 't': round(t + i * gap, 3)} for i, x in enumerate(text.split())]
def LW(pairs):
    """a line whose words land on the spoken word: [(word, word_index)]"""
    return [{'w': x.strip('*'), 'g': int(x.startswith('*')), 't': at(k)} for x, k in pairs]
def ttl(i, a, b, k, lines, size=0): return {'id': i, 'from': round(a, 3), 'to': round(b, 3), 'k': k, 'lines': lines, 'size': size}
HOOK = ttl('hook', 0, 5.2, 'Promesas de Dios para ti', [L('¿QUÉ PENSAMIENTO', .05), L('TE ESTÁ ROBANDO', .45), L('*LA* *PAZ?*', .9, .14)], 1)
H = [HOOK,
 ttl('prob',  at(32), end(59) + .5, 'El problema no es que aparezcan', [L('ES DEJAR QUE', at(50)), LW([('SE', 54), ('*ADUEÑEN*', 56)]), L('DE TU MENTE', at(57))]),
 ttl('gob1',  at(60), at(79) - .05, 'Pensamientos sin invitación', [L('GOBIERNAN CÓMO', at(69)), LW([('*PIENSAS*', 75), ('·', 75), ('*VIVES*', 76), ('·', 76), ('*CREES*', 78)])]),
 ttl('gob2',  at(79), end(99) + .3, 'Les damos espacio', [L('Y SE QUEDAN', at(79)), LW([('*AÑOS*', 89)]), L('EN TU MENTE', at(90))]),
 ttl('pablo', at(100), end(106) + .25, '2 Corintios 10:5', [L('LLÉVALOS CAUTIVOS', at(103)), LW([('A', 105), ('*CRISTO*', 106)])]),
 ttl('decide', at(107), end(123) + .3, 'Tú decides', [L('QUÉ LUGAR', at(117)), L('LES DAS EN', at(119)), L('*TU* *MENTE*', at(122))]),
 ttl('verdad', at(124), end(140) + .2, 'Entiende esto', [L('NO TODO LO', at(127)), L('QUE PIENSAS', at(130)), LW([('ES', 132), ('*VERDAD*', 133)])]),
 ttl('poder', at(141), end(152) + .3, 'Pensamientos que dañan', [L('NO LES DES', at(141)), LW([('EL', 144), ('*PODER*', 145)])]),
 ttl('donde', at(153), end(168) + .35, 'Pregúntate', [L('¿DE DÓNDE', at(165)), LW([('*VIENEN?*', 168)])]),
 ttl('autor', at(169), end(187) + .3, 'Toma la autoridad', [L('LLEVA *CAUTIVO*', at(179)), L('TODO PENSAMIENTO', at(181))]),
 ttl('ora1',  at(188), end(216) + .2, 'Cierra tus ojos', [L('ORA', at(188) + .2), L('*CONMIGO*', at(188) + .45)], 2),
 ttl('ora2',  at(217), end(240) + .2, 'Señor, ayúdame', [L('A NO CREERLE A', at(223)), L('TODO LO QUE', at(227)), LW([('*PIENSO*', 230)])]),
 ttl('ora3',  at(241), end(264) + .1, 'Padre', [L('¿QUÉ TENGO', at(245)), LW([('QUE', 248), ('*SOLTAR?*', 249)])]),
 ttl('amen',  at(265), end(267) + .15, 'En el nombre de Cristo Jesús', [LW([('*AMÉN*', 265)])], 2),
 ttl('fin',   at(268), END, 'Promesas de Dios para ti', [L('ELIMINA TODO', at(268)), L('PENSAMIENTO QUE', at(270)), L('NO VIENE DE *DIOS*', at(272))]),
]
for a, b in zip(H, H[1:]): a['to'] = min(a['to'], b['from'])
json.dump(W, open(P + '/proj/words.json', 'w'), indent=1, ensure_ascii=False)
open(P + '/ov/data.js', 'w', encoding='utf-8').write(
    'const CAPS=' + json.dumps(caps, ensure_ascii=False) + ';\nconst HL=' + json.dumps(H, ensure_ascii=False) + f';\nconst END={END:.4f};\n')
print(len(W), 'words', len(caps), 'chunks')
for h in H: print(f"{h['id']:7s} {h['from']:6.2f}-{h['to']:6.2f}  {h['k']} | " + ' / '.join(' '.join(w['w'] for w in l) for l in h['lines']))
