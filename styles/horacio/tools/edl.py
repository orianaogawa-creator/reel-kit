"""Promesas: best takes, long pauses tightened. Beat = (id, line, [(in,out) source s]); pauses >0.32 s inside a range shrink to 0.2 s."""
import json
import os
P = os.environ.get('PROJ', '.')  # project folder: proj/, ov/, tools/
SIL = [tuple(map(float, p.split('-'))) for p in open(P + '/proj/sil.txt').read().split()]
B = [
 ('hook',   "Todos los días tenemos miles de pensamientos, algunos propios y otros que forman parte de lo que vimos o lo que vivimos. Y algunos de ellos pueden llegar a robarnos la paz.", [(2.06, 15.62)]),
 ('prob',   "El problema no es que aparezcan, porque muchas veces sentimos que no tenemos el control sobre cuándo aparecen. El problema aparece cuando les permitimos adueñarse de nuestra mente.",
            [(18.27, 20.40), (21.10, 23.47), (24.55, 26.98), (30.42, 35.52)]),
 ('gob',    "A veces esos pensamientos que llegan sin ser llamados terminan gobernando la forma en que pensamos, vivimos y creemos. Dejamos que se instalen al punto de que viven por años en nuestra mente y gobiernan gran parte de nuestra vida.",
            [(41.02, 51.12), (58.36, 66.95)]),
 ('pablo',  "Pablo nos dijo: llevarlos cautivos a Cristo.", [(68.95, 70.32), (75.82, 79.02)]),
 ('decide', "Somos nosotros quienes podemos decidir qué hacemos con ellos y qué lugar les damos en nuestra mente.", [(84.80, 94.40)]),
 ('verdad', "Significa entender que no todo lo que pensamos es verdad ni merece tener autoridad sobre nuestra vida. No le demos el poder a esos pensamientos que nos están dañando.", [(95.22, 104.45), (105.28, 108.80)]),
 ('donde',  "Quizá hoy no tienes que darle tanto peso a esos pensamientos, sino preguntarte de dónde vienen.", [(123.58, 132.45)]),
 ('autor',  "Párate frente a él, toma la autoridad para orar y llevar cautivo todo pensamiento que no venga de Dios.", [(133.02, 142.80)]),
 ('ora1',   "Cierra tus ojos, repite en voz baja y dile: Señor, gracias porque tú conoces cada pensamiento que aparece en mi mente y aún así no te alejas de mí.", [(143.58, 157.15)]),
 ('ora2',   "Hoy quiero pedir que me ayudes a no creerle a todo lo que pienso, sino a llevar cautivo aquello que no viene de ti.", [(157.84, 167.50)]),
 ('ora3',   "Ayúdame a reconocer, Padre, qué pensamientos tengo que soltar y a redirigir mi mirada hacia tu verdad, en el nombre poderoso de Cristo Jesús. Amén y amén.", [(167.84, 170.46), (172.56, 184.00)]),
 ('fin',    "Elimina todo pensamiento que no viene de Dios. Nos vemos la próxima.", [(185.58, 188.35), (189.15, 190.38)]),
]
def tighten(a, b, gap=.32, keep=.1):
    out, s = [], a
    for x, y in SIL:
        if x > s + .05 and y < b - .05 and y - x > gap:
            out.append((s, x + keep)); s = y - keep
    out.append((s, b)); return out
edl, beats, t = [], [], 0.0
for bid, line, pcs in B:
    t0 = t; j = 0
    for a, b in pcs:
        for x, y in tighten(a, b):
            n = round((y - x) * 30); j += 1
            edl.append({'id': f'{bid}{j}', 'beat': bid, 'in': round(x, 3), 'out': round(y, 3), 'frames': n}); t += n / 30
    beats.append({'id': bid, 'line': line, 'start': round(t0, 3), 'end': round(t, 3)})
json.dump(edl, open(P + '/proj/edl.json', 'w'), indent=1)
json.dump(beats, open(P + '/proj/beats.json', 'w'), indent=1, ensure_ascii=False)
for b in beats: print(f"{b['id']:7s} {b['start']:6.2f}-{b['end']:6.2f}")
print('pieces', len(edl), 'frames', sum(p['frames'] for p in edl), 'sec', round(t, 2))
