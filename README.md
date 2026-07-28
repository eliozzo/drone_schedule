# Drone Path Scheduling

Implementazione semplice del problema DPSP descritto nel paper allegato.

Il progetto contiene:

- `algoritmi/rec.py`: algoritmo REC;
- `algoritmi/heap_based.py`: algoritmo Heap-Based;
- `algoritmi/ilp.py`: formulazione ILP esatta usata come riferimento;
- `experimental_setting/generator.py`: generatore riproducibile di istanze;
- `experimental_setting/run_experiments.py`: esecuzione dei benchmark;
- `experimental_setting/plots.py`: grafici del rapporto `makespan algoritmo / makespan ILP`;
- `tests/`: test di correttezza essenziali.

REC è definito solo per cammini unidirezionali. Heap-Based funziona anche sui
cammini bidirezionali, ma in quel caso non è necessariamente ottimo.

## Installazione

```bash
cd drone_scheduling
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Esecuzione

Esperimento completo richiesto (33 istanze per ogni coppia `n-m`):

```bash
python -m experimental_setting.run_experiments --mode both
```

I valori predefiniti sono:

- `n = 5, 10, 15`;
- `m = 10, 20, 30, 40`;
- slot iniziale uniforme in `{1, ..., 5}`;
- lunghezza del cammino uniforme in `{1, ..., m}`;
- direzione uniforme tra sinistra-destra e destra-sinistra nelle istanze
  bidirezionali;
- 33 istanze per combinazione.

I risultati vengono scritti in `results/results.csv`. I grafici sono:

- `results/ratio_vs_n.png`;
- `results/ratio_vs_m.png`.

Per una prova veloce:

```bash
python -m experimental_setting.run_experiments \
  --mode both --n-values 5 --m-values 10 --instances 2
```

Per rigenerare i grafici da un CSV esistente:

```bash
python -m experimental_setting.plots results/results.csv
```

## Test

```bash
python -m unittest discover -s tests -v
```

L'ILP usa `scipy.optimize.milp` e non richiede solver commerciali. Il benchmark
completo può richiedere tempo, soprattutto per le istanze bidirezionali più
grandi; `--time-limit` imposta il limite in secondi per ciascuna ILP.
