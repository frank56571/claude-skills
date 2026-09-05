---
name: codex-loop
description: Ciclo de desarrollo en tándem con Codex (OpenAI) — Claude planifica, Codex ejecuta, Claude revisa el diff y pide cambios, Codex corrige, Claude re-revisa, y cierran con revisión cruzada mutua. Usar cuando el usuario diga "codex-loop", "que lo ejecute Codex", "pásaselo a Codex", "trabaja con Codex", "revisión cruzada con Codex", o pida tándem con otro agente CLI.
---

# codex-loop

Dos modelos de proveedores distintos sobre el mismo repo. Reparto fijo:

| Rol | Quién | Por qué |
|-----|-------|---------|
| Planificar | Claude (tú) | tienes el contexto de la sesión y del proyecto |
| Ejecutar | Codex CLI | escribe el código; tú NO tocas el código en este ciclo |
| Revisar | Claude (tú) | revisas el **diff**, no lo que Codex dice que hizo |
| Corregir | Codex | mismos ojos que escribieron, con tus objeciones |
| Veredicto | ambos | cada uno intenta refutar al otro |

**Regla dura:** en fases 1–4 tú no editas archivos de código. Si arreglas tú lo que Codex hizo mal, el ciclo pierde su valor (deja de haber dos opiniones) y se vuelve teatro. Excepción: los artefactos de `.codex-loop/`.

## Sintaxis de Codex CLI — verificado en 0.150.1 (2026-08-27)

Tres cosas que rompen si las haces de memoria:

- **No existe `--full-auto`** en `codex exec`. Es `-s workspace-write` (o `read-only` / `danger-full-access`).
- **Las opciones van ANTES del subcomando**: `codex exec -m X -s workspace-write resume <SID>`. Después de `resume` da `error: unexpected argument '-s'`.
- **Siempre pasa `-m`.** El `~/.codex/config.toml` del usuario dice `model = "gpt-5-codex"`, que ya no se sirve a cuentas ChatGPT (`400: model is not supported when using Codex with a ChatGPT account`). No lo edites — la app de Codex lee ese mismo archivo.

Modelo: **`gpt-5.6-sol` con `-c model_reasoning_effort=xhigh`** (preferencia del owner; sol apareció en el catálogo el 2026-08-27 con prioridad 1). Cadena de fallback si `at capacity`: sol → terra → luna, y **anota en el log** qué modelo corrió cada ronda — un cambio de modelo a mitad de trabajo cambia cómo se lee el resultado. La lista viva:

```bash
python3 -c "import json;print(' '.join(m['slug'] for m in json.load(open('$HOME/.codex/models_cache.json'))['models'] if m['visibility']=='list'))"
```

Cada `codex exec` tarda minutos: `run_in_background: true` o `timeout: 600000`, y avisa al usuario que está corriendo.
- **En background SIEMPRE `< /dev/null`**: con stdin abierto sin EOF, `codex exec` se cuelga para siempre en "Reading additional input from stdin..." (0% CPU, sin header). No es un kill — espera un EOF que nunca llega. Verificado 2026-08-27.

## Fase 0 — preparar

```bash
git rev-parse --git-dir >/dev/null || { echo "no es repo git"; exit 1; }
git status --porcelain            # debe estar limpio; si no, para y pregunta
BASE=$(git branch --show-current) # la rama de la que sales, para el diff final
git switch -c codex-loop/<slug>
mkdir -p .codex-loop && echo "$BASE" > .codex-loop/base
grep -qxF '.codex-loop/' .git/info/exclude || echo '.codex-loop/' >> .git/info/exclude
which codex || echo "MODO HANDOFF"   # sin binario → ver final del documento
```

## Fase 1 — plan (Claude)

Escribe `.codex-loop/PLAN.md`. No es un ensayo: es un contrato ejecutable.

- **Objetivo** en una frase.
- **Archivos** que se esperan tocar (rutas concretas).
- **Pasos** numerados, cada uno verificable.
- **Aserciones**: qué comando prueba que funciona (`pytest -q`, `npm test`, un curl). Sin esto no hay revisión posible, solo opinión.
- **Fuera de alcance**: lo que Codex NO debe tocar.

Si el usuario no dio suficiente para escribir aserciones, pregúntale antes de arrancar. Un plan sin criterio de éxito hace que las fases 3–5 no sirvan.

## Fase 2 — ejecutar (Codex)

```bash
M="-m gpt-5.6-sol -c model_reasoning_effort=xhigh"   # fallback: terra, luego luna
codex exec $M -s workspace-write -o .codex-loop/last-1.txt < /dev/null "$(cat .codex-loop/PLAN.md)

Trabaja solo en este repo. No cambies de rama, no hagas commit, no toques nada fuera del alcance.
Al terminar imprime solo la lista de archivos que modificaste." 2>&1 | tee .codex-loop/run-1.log
grep -m1 'session id:' .codex-loop/run-1.log | awk '{print $3}' > .codex-loop/session-id
```

Guarda el session id: `resume --last` agarra la sesión más reciente **de toda la máquina**, no la de este repo. Si el usuario abrió Codex en otra ventana mientras tanto, `--last` reanuda la equivocada.

Congela el resultado — es la unidad que vas a revisar:

```bash
git add <archivos del alcance>   # nunca -A: docs propios a medio escribir en el árbol entrarían al commit
git commit -qm "codex: <slug> ronda 1" --no-verify
git diff HEAD~1 HEAD > .codex-loop/diff-1.patch   # dos revisiones: `git diff HEAD~1` a secas arrastra el working tree
```

## Fase 3 — revisar (Claude)

Lee **el diff y los archivos**, no el resumen de Codex (`last-1.txt` es referencia, no evidencia). Corre las aserciones del plan tú mismo:

```bash
git diff HEAD~1 HEAD --stat
<comando de aserción del PLAN.md>
```

Escribe `.codex-loop/REVIEW-1.md`. Una línea por hallazgo:

```
[BLOQUEA] src/auth.py:42 — el token no se valida antes de decodificar → arreglo: verificar firma antes de jwt.decode
[MENOR]   src/api.py:88 — nombre confuso; no bloquea
```

Solo `[BLOQUEA]` vuelve a Codex. Nada de elogios, nada de resumen. Si el diff no cumple una aserción, eso es `[BLOQUEA]` aunque el código se vea bien; si el diff cumple todo, dilo y salta a la fase 5.

## Fase 4 — corregir (Codex) y re-revisar

```bash
codex exec $M -s workspace-write resume "$(cat .codex-loop/session-id)" \
  "Revisión de tu trabajo. Arregla SOLO los [BLOQUEA]:

$(cat .codex-loop/REVIEW-1.md)

Si crees que alguno está mal, no lo cambies: explica por qué. Discrepar es válido."
```

Commit + `diff-2.patch` + `REVIEW-2.md` igual que antes.

**Máximo 2 rondas de corrección.** Si en la ronda 3 sigue habiendo `[BLOQUEA]`, para y lleva el desacuerdo al usuario con las dos posturas. Un ping-pong entre dos modelos puede correr indefinidamente sin converger, y quema tokens de ambas suscripciones.

Si Codex rechaza un hallazgo con argumento, verifícalo antes de insistir — puede tener razón.

## Fase 5 — veredicto cruzado

Cada uno intenta tumbar al otro sobre el diff completo.

```bash
git diff "$(cat .codex-loop/base)" HEAD > .codex-loop/diff-final.patch
```

**Gotcha verificado 2026-08-27 (0.150.1):** `codex exec review --base <rama> "<prompt>"` NO funciona — `error: the argument '--base <BRANCH>' cannot be used with '[PROMPT]'`, aunque la línea de uso del `--help` muestre los dos juntos. O usas `review --base <rama>` con las instrucciones por defecto de Codex, o le pasas tus propias instrucciones por el carril normal en read-only. Para un pase adversarial dirigido, lo segundo:

```bash
codex exec $M -s read-only "Revisión adversarial. Busca razones por las que este diff FALLE:
bugs, casos borde, regresiones, y cosas que el plan pedía y no están. Presta atención
a los CALLERS del código tocado, no solo al diff. No resumas, no elogies.
Defectos con archivo:línea, o 'sin objeciones'.
No corras tests que escriban en disco: en read-only el sandbox no puede crear temporales
y fallan con FileNotFoundError — eso es limitación del sandbox, no defecto.

--- PLAN ---
$(cat .codex-loop/PLAN.md)
--- DIFF ---
$(cat .codex-loop/diff-final.patch)" 2>&1 | tee .codex-loop/review-codex.md
```

`-s read-only` importa: el revisor no debe poder arreglar lo que encuentra. Un FAILED que venga de ese pase no es evidencia hasta reproducirlo fuera del sandbox (verificado 2026-09-04: 168 fallos falsos por temporales).

Tú haces tu propio pase adversarial sobre el mismo diff **antes de leer** el de Codex — si lo lees primero, te anclas a lo que él vio. Luego juntas ambas listas en `.codex-loop/VERDICTO.md`:

- **Ambos limpio** → listo para merge.
- **Uno objeta** → esa objeción vuelve a fase 4 (cuenta como ronda).
- **Se contradicen** → escribe las dos posturas y decide el usuario. No arbitres solo.

Reporta al usuario: qué se hizo, qué aserciones pasaron con su salida real, qué quedó abierto.

## Modo handoff (sin `codex` en PATH)

El usuario es el bus de mensajes. Idéntico ciclo, sin automatizar las fases 2 y 4:

1. Escribes `.codex-loop/PLAN.md`.
2. Le dices al usuario: *"pega esto en Codex: `lee .codex-loop/PLAN.md y ejecútalo, no hagas commit`"*.
3. Cuando avise, tú haces commit + revisas el diff → `REVIEW-N.md`.
4. *"pega esto en Codex: `lee .codex-loop/REVIEW-1.md y arregla solo los [BLOQUEA]`"*.

Todo pasa por archivos del repo, así ambos agentes ven lo mismo sin copiar y pegar código.
