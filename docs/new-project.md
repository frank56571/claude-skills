# `/new-project` — guía de uso

`/new-project` arranca un proyecto nuevo con un framework probado y después lo acompaña durante todo el build. No es un generador one-shot: el scaffold es la hora cero, y los comandos que deja instalados (`/next`, `/verify`, `/direction`) son los que llevan el proyecto de ahí en adelante.

Piezas: `commands/new-project.md` (el comando) + `skills/project-architect/` (referencias y plantillas que el comando lee).

---

## Instalación

```sh
git clone https://github.com/frank56571/claude-skills.git
cd claude-skills
cp commands/new-project.md ~/.claude/commands/
cp -R skills/project-architect ~/.claude/skills/
```

Reinicia Claude Code. Requisitos:

| Requisito | Para qué | ¿Obligatorio? |
|---|---|---|
| `git` | branches + PRs, siempre | sí |
| Vault Obsidian en `~/SecondBrain/` | memoria del proyecto (el *por qué*) | convención: ajusta la ruta si usas otra |
| [Graphify](https://pypi.org/project/graphifyy/) (`uv tool install graphifyy && graphify install`) | mapa del código | sí |
| `uv` | modo `orchestrated` (servidor MCP del board) | solo en ese modo |
| MCP `notebooklm-mcp` | notebook con la documentación externa | no, se puede saltar |
| Herramientas MCP de navegador | agente `first-user` | solo en proyectos con UI |
| Key de Anthropic/OpenAI + presupuesto | DeepSec | no, opt-in |

---

## Uso rápido

```text
mkdir mi-proyecto && cd mi-proyecto
claude
> /new-project mi-proyecto
```

Responde la entrevista. Al terminar tienes un repo con código real, un smoke test que pasa, git configurado y memoria en el vault. Desde ahí:

```text
> /next
```

…y sigues con `/next` cada sesión.

---

## Qué pasa al correrlo

### 0. Detecta si el proyecto ya existe

Es lo primero que hace, antes de cualquier pregunta:

| Estado del directorio | Resultado |
|---|---|
| Tiene `CLAUDE.md` + memoria en el vault + `.claude/commands/next.md` | **RESUME**: no te entrevista; lee el estado y te pasa a `/next`. |
| Scaffoldeado pero sin `next.md` | **RETROFIT**: pregunta y añade solo los comandos del companion; no toca nada más. |
| Ninguno de los dos | **NEW**: entrevista completa. |

Correr `/new-project` en un proyecto existente es seguro: nunca vuelve a planear desde cero. Si al proyecto le falta `/direction` (fue creado antes del 2026-10-20), te ofrece una vez añadirlo.

### 1. Entrevista

Las preguntas 1–4 son obligatorias; el resto depende de la categoría.

| # | Pregunta | Para qué sirve |
|---|---|---|
| 1 | Nombre + descripción en una línea | misión del CLAUDE.md, PRD |
| 2 | Categoría | decide qué se genera (ver tabla abajo) |
| 3 | Lenguaje / runtime / framework | skeleton base (`uv init`, `create-next-app`…) |
| 4 | Owner / cliente / usuario | tono, gates, alcance |
| 5 | Integraciones | `.env.example`, contratos |
| 6 | Agentes y sus reglas CAN/CANNOT | solo en proyectos de agentes |
| 7 | Gates de aprobación | toda acción con efectos (pagar, publicar, borrar) |
| 8 | Target de deploy | compose / notas de deploy |
| 9 | ¿Delivery con gates (SAW)? | equipos / agentes en producción |
| 10 | Modo de paralelización | ver sección *Paralelizar* |
| 11 | Material de referencia para el notebook | docs, specs, videos externos |
| 12 | **Must-not-trade-offs + zonas críticas** | lo que nunca se sacrifica, cada regla con su test |
| 13 | **Profundidad de seguridad** (`none` / `deepsec`) | ver sección *Seguridad* |

Categorías: `agent-system`, `single-agent-app`, `api-service`, `web-app`, `cli-tool`, `library-sdk`, `data-pipeline`, `research-prototype`, `other`.

### 2. Qué genera

**Siempre, en toda categoría:**

```text
mi-proyecto/
├── CLAUDE.md                  # sistema operativo del agente + reglas del proyecto (<200 líneas)
├── README.md
├── specs/PRD.md               # problema, usuario, features numeradas con criterios de aceptación
├── tasks/todo.md              # el plan activo; el primer ítem es el MVP
├── .env.example               # todas las variables, sin valores
├── tests/                     # runner del lenguaje + smoke test que pasa
├── .claude/commands/
│   ├── next.md                # companion
│   ├── verify.md              # barrera de revisión
│   └── direction.md           # chequeo de desvío contra specs/
└── graphify-out/              # mapa del código (gitignored, se regenera)

~/SecondBrain/projects/mi-proyecto/
├── MEMORY.md                  # índice + ## Estado (lo que está en curso)
├── decisions/  domain/  context/  reference/
```

**Según la categoría:**

| Categoría | Además |
|---|---|
| `agent-system`, `single-agent-app` | orquestador, schemas entre agentes, `prompts/<agente>/v1/`, gates de aprobación, `breaker` |
| `api-service`, `web-app` | rutas/handlers, schemas request/response, middleware, `breaker` |
| `web-app` o cualquier proyecto con UI | `first-user` + suite de recorridos `tests/e2e/` |
| `data-pipeline` | runner, schedule, idempotency keys, observabilidad, `breaker` |
| `cli-tool`, `library-sdk`, `research-prototype` | sin agentes adversarios |
| Modo `orchestrated` | `coordination/` (board MCP), `.mcp.json`, `/orchestrate`, `/worker`, agentes `sentinel` y `task-planner` |

---

## Después del scaffold: el día a día

### `/next`: el companion

Lo corres al empezar cada sesión. Hace esto:

1. **Orienta**: lee el `## Estado` del vault, `tasks/todo.md` y `git status`. Si hay trabajo sin commitear, eso es lo primero que reporta.
2. **Rankea**: P0 (bloquea el deploy) → lo que desbloquea más ítems → P1 → P2. Si todavía no hay MVP, el MVP es la jugada.
3. **Propone y se detiene**: qué, por qué ahora y cuál quedó segundo. **No construye hasta que confirmes.**
4. **Diseña**, si el cambio es grande (3 o más archivos, o un endpoint/tabla/pantalla nueva): firmas sin cuerpo, call stack, tests y las decisiones de las que menos seguro está. Vuelve a esperar.
5. **Ejecuta** en vertical: primero un corte que corre de punta a punta, luego se rellena.
6. **Verifica** con `/verify`.
7. **Registra**: marca `todo.md`, guarda las lecciones durables en el vault y actualiza `## Estado`.

### `/verify`: la barrera de revisión

Tres revisores corren a la vez sobre el diff, **a ciegas**: ven solo el diff y los criterios de aceptación, nunca la conversación del build.

| Lente | Busca |
|---|---|
| `/code-review` | bugs, edge cases, manejo de errores |
| `/simplify` (solo reporta) | duplicación, abstracción mal ubicada |
| `ponytail-review` | sobre-ingeniería, dependencias innecesarias |
| `web-design-guidelines` | solo en proyectos con UI |

Los veredictos se reportan por separado, con `file:line`. Los revisores siempre corren en modelo fuerte: un juez barato reporta de más, y los agentes terminan "arreglando" lo que no estaba roto.

### `/direction`: ¿vamos hacia donde dijimos?

Con agentes, construir es barato; los tokens y los PRs miden volumen, no dirección. `/direction` lanza un agente por documento de `specs/` para comprobar si el código cumple cada requisito, mientras el agente principal lista lo que se construyó **sin que ningún spec lo pidiera**. Entrega:

- una puntuación por spec (`delivered / partial / missing / contradicted`)
- el estado de cada regla Must-Not-Trade-Off
- la lista de trabajo no planeado: por cada ítem decides **adopt** (actualizar el spec) o **revert**

Solo reporta, no edita nada. Córrelo antes de cada release y cada pocas features; `/next` te lo recuerda.

### Agentes adversarios

- **`breaker`**: intenta romper la app con concurrencia, pasos saltados, input malo, carga y dependencias caídas. **Solo ataca una copia aislada**; si el destino apunta a staging, producción o datos reales, se niega. Cada rotura confirmada se convierte en un test de regresión, y lo vuelves a correr hasta que no encuentre nada nuevo.
  ```text
  > corre el agente breaker contra el stack local
  ```
- **`first-user`**: usa la app como alguien que la ve por primera vez, **solo con el navegador** (no tiene permiso para leer el código). Tú arrancas la app y le pasas la URL. Reporta dónde se traba un usuario nuevo.
  ```text
  > levanta la app y pásale la URL al agente first-user
  ```
- **Suite de recorridos** (`tests/e2e/`): un test e2e por cada camino que todo cliente debe completar, con resultados en `tests/e2e/journeys.json`. Funciona como proxy de "sesiones sin errores". Córrela antes de cada release.

---

## Seguridad

Hay dos capas:

1. **`/security-review` después de cada feature.** Siempre activo, gratis y local. Es un gate aparte de `/verify`.
2. **DeepSec** ([vercel-labs/deepsec](https://github.com/vercel-labs/deepsec)): opt-in en la pregunta 13. Es un escáner de vulnerabilidades basado en agentes y llega más profundo, pero:
   - **cuesta dinero**: usa modelos tope al máximo de thinking, y un scan completo de un repo grande puede costar miles de USD
   - **el código sale de tu máquina** hacia el proveedor del modelo
   - **es un agente con shell completo** sobre la máquina donde corre

Cómo lo deja configurado el skill:

- **No lo ejecuta en el scaffold**, porque todavía no hay nada que escanear. Queda como P1 en `todo.md` para después de la primera feature real.
- Setup con key propia y tope de gasto (ajusta los números):
  ```sh
  npx deepsec init --model-auth direct --ai-provider anthropic \
    --ai-api-key-env DEEPSEC_ANTHROPIC_API_KEY \
    --max-cost-usd 20 --max-duration 30m
  ```
- En cada cambio a una zona crítica, después de `/security-review`:
  ```sh
  cd .deepsec && pnpm deepsec process --diff main   # exit 1 = finding nuevo → revisar antes del merge
  ```
- Antes de un release: `scan` → `process` → `revalidate` → `export --format md-dir --out ./findings`.
- `.deepsec/data/` y los findings van en `.gitignore`: son una lista de vulnerabilidades explotables. **Nunca los commitees**, menos en un repo público.
- Nunca lo corras sobre código de terceros sin revisar ni en una máquina con secretos de producción o datos reales de clientes.
- Si el código no puede llegar a un tercero, responde `none` en la pregunta 13.

Las **zonas críticas** (auth, pagos, datos de usuario, todo lo monetario o fiscal) se definen en la pregunta 12. Ahí el código desordenado no se acepta: toda la barrera `/verify` y tests en cada cambio. Fuera de ellas se permite ir rápido.

---

## Must-Not-Trade-Off

En la pregunta 12 declaras lo que el proyecto nunca sacrifica, por ejemplo:

```markdown
## 🚫 Must-Not-Trade-Off
- Los totales de nómina cuadran al centavo — checked by `tests/test_payroll_totals.py`
- p95 de la API < 300 ms — checked by `make bench`
```

Cada regla **tiene que** nombrar su check, y el scaffold genera ese test. Una regla sin check es un deseo: va como P0 en `todo.md` hasta que exista su test. Esto importa porque las reglas en prosa se olvidan cuando el contexto crece, y un test en git no se puede saltar.

---

## Memoria y contexto

Tres capas, cada una con una sola responsabilidad:

| Capa | Dónde | Contiene | Cuándo consultarla |
|---|---|---|---|
| Vault Obsidian | `~/SecondBrain/projects/<slug>/` | el **por qué**: decisiones, glosario, gotchas, `## Estado` | "¿por qué?", "¿cuál es el plan?" |
| Graphify | `graphify-out/` (en el repo, gitignored) | **qué conecta con qué** en el código | "¿dónde se usa X?" → `/graphify query "…"` |
| Notebook NotebookLM | UUID en `reference/notebook.md` | lo que dice la **fuente externa** | antes de diseñar contra una API o spec ajena |

Lo que decidimos nosotros va al vault, lo que hace el código está en graphify, y lo que dice un tercero va al notebook. Después de cambios estructurales, actualiza el mapa con `/graphify . --update`.

---

## Paralelizar

Todo proyecto trae git con `main` como trunk: una unidad de trabajo, un branch, un PR, y merge humano. La pregunta 10 elige el modo:

| Modo | Cómo funciona | Cuándo usarlo |
|---|---|---|
| `single-instance` | una sesión con subagentes / Workflow | por defecto, lo más barato |
| `multiple-instances` | una sesión por tarea, cada una en su git worktree; los prompts listos para pegar quedan en `tasks/parallel-prompts.md` | tareas independientes con archivos disjuntos |
| `orchestrated` | terminal 1 `/orchestrate` y terminales 2..N `/worker` sobre un board MCP que **rechaza** tareas cuyos archivos se solapan | equipos de agentes en paralelo |
| `decide-later` | solo git + PRs | aún no sabes |

Para builds largos de varias features existe `/mission-control` (skill aparte de este repo).

---

## Gotchas

- `/next` **propone y espera**. Si quieres que construya algo concreto, dilo directamente; el companion no avanza sin tu confirmación.
- `/simplify` aplica fixes por defecto; dentro de `/verify` está forzado a solo reportar. Si lo corres suelto, sí edita.
- `first-user` necesita que `{BROWSER_TOOLS}` quede lleno con herramientas MCP de navegador reales. Sin ellas no hace nada.
- El notebook y DeepSec escriben a servicios externos: los dos piden confirmación y los dos se pueden saltar sin romper el scaffold.
- Re-correr `/new-project` en un proyecto existente hace RESUME, no lo reinicia.
