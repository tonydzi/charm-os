# CharmOS · {C(H+A)RM}

**The first open-source framework that manages both your human contacts AND your AI agents as first-class relationships, on top of a personal "second brain", driven by one decision loop: RDR.**

> C(H+A)RM = **C**RM for **H**umans **+ A**gents **R**elationship **M**anagement.
> RDR = **R**ecall to **D**eep **R**esearch to synthesis. The loop that turns memory into decisions.

---

## What this is

Three things most people keep in separate silos, unified into one open framework:

1. **Second Brain** to a private, local-first knowledge base (markdown vault) with semantic recall (embeddings + reranker), an always-on per-turn memory ledger, and a graph/associative recall layer.
2. **C(H+A)RM** to a relationship layer that treats **people and AI agents alike** as contacts you maintain: notes, history, warm intros, follow-ups.
3. **RDR** to the method that ties them together: **Recall** what you already know, run **Deep Research** to fill the gaps, then **synthesize** into a Decision Memo before you act.

## Why it is different

The ecosystem is rich but siloed:

| Space | Examples | What they miss |
|---|---|---|
| Personal knowledge (PKM) | AFFiNE, Logseq, Khoj, Quivr | no agent memory, no contacts |
| Agent / LLM memory | Mem0, Letta, Cognee, Graphiti | no personal vault, no human CRM |
| Personal CRM | Monica, Twenty | ignore AI agents entirely |

**No tool spans personal notes to agent memory to human CRM, and none prescribe a structured decision loop.** That intersection, plus RDR, is the whole point.

## Who it is for

Founders, researchers, and operators who want a durable "digital twin" of how they think and who they know, that they fully own, can repair themselves, and can grow over years.

## Architecture (high level)

```
        ┌──────────────────────────────────────────────┐
        │                   RDR LOOP                     │
        │  Recall  ->  Deep Research  ->  Synthesis      │
        └───────▲───────────────────────────────┬───────┘
                │                                 │
        ┌───────┴────────┐               ┌────────▼────────┐
        │  SECOND BRAIN  │               │    C(H+A)RM     │
        │ vault + RAG +  │◄─────────────►│ humans + agents │
        │ memory ledger  │   shared      │ as contacts     │
        │ + graph recall │   knowledge   │ intros, history │
        └───────▲────────┘               └────────▲────────┘
                │                                 │
        ┌───────┴─────────────────────────────────┴───────┐
        │   Import pipelines (chat / mail / calls / docs)   │
        │   Skills (composable agent commands)             │
        └──────────────────────────────────────────────────┘
```

## Status

**Manifest-first, now with runnable modules.** This repository shipped the **vision, architecture, and docs** first (see [MANIFESTO.md](MANIFESTO.md) and [`/docs`](docs/)); real code is now landing under [`modules/`](modules/):

- [`modules/turnstate/`](modules/turnstate/) (v0.2.0) — the **always-on memory ledger**: per-turn deterministic working state, hook + self-healing backfill.
- [`modules/rdr/`](modules/rdr/) (v0.3.0) — the **RDR loop** as a CLI: `recall` → `research` → `memo`, built on the TurnState ledger.
- [`modules/eval-harness/`](modules/eval-harness/) (v0.1.0) — **grade your agent fleet against rules it must never break.** Turns a multi-agent event log into reproducible traces and scores them against explicit safety invariants. Includes our own production results: human-gate before a risky commit **100%**, independent verify before commit **7.7%** — we publish both.

All deterministic, zero-LLM-token, pure stdlib. More modules follow.

### Roadmap

**Now — [v0.4.0](https://github.com/tonydzi/charm-os/releases).** The three
modules above, each versioned on its own, plus the manifesto and docs that came first.

**Next**, from [CHANGELOG.md](CHANGELOG.md): a Second Brain reference implementation (vault + RAG +
reranker), the graph/associative recall layer with entity-vs-theme gating, the C(H+A)RM relationship
layer (humans and agents as contacts), and the import pipelines.

We version with [SemVer](https://semver.org), and **every noticeable change ships as a new release**
— a shipped module is a release, cut when the work lands rather than when someone remembers. The
[release feed](https://github.com/tonydzi/charm-os/releases) is how you tell what
is real here from what is still a manifesto.

## Privacy (read this first)

This framework operates on deeply personal data. **No real personal data is included in this repository.** Everything under [`/examples`](examples/) is synthetic. If you self-host, your data stays yours and local. See [docs/privacy.md](docs/privacy.md).

## Cite this work

If this repo shows up in your research, cite it via [CITATION.cff](CITATION.cff) (GitHub's "Cite this repository" button). Author: **Anton Dziatkovskii** ([ORCID 0000-0001-7408-3054](https://orcid.org/0000-0001-7408-3054), GitHub [@tonydzi](https://github.com/tonydzi)) — one spelling everywhere, in publications, commits and `CITATION.cff`.

## AI contributors

This project is built by a human + AI team, and the git log says so: Claude
writes most of the code, Codex and Grok review it, Gemini feeds the research.
Each is credited on a commit **only if its output changed that commit's
content** — no decorative credits. Lab-wide policy, one source for every repo:
[AI-CONTRIBUTORS.md](https://github.com/tonydzi/.github/blob/main/AI-CONTRIBUTORS.md).

## License

[Apache License 2.0](LICENSE). Permissive, with an explicit patent grant. An open-core path (optional paid layer/hosting) may follow, but the core stays open.

---

Built by [Palo Alto AI Research Lab](https://github.com/tonydzi). Contributions and discussion welcome once V1 docs settle.

<!-- CONTACT-FOOTER -->
## About & contact

Questions, war stories, or you want to run this on your own fleet:

- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 📣 Channels: [@ClawRus](https://t.me/ClawRus) (RU) · [@ClawEng](https://t.me/ClawEng) (EN)
- 🌐 [palo-alto.ai](https://palo-alto.ai) · [Palo Alto AI Research Lab](https://github.com/tonydzi)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.

---

<!--we-ask:start-->

## Contributors welcome — and here is what we are missing

We spend a lot of time answering other people's issues. It was fair to say out loud
what we have not built ourselves:

- [eval-harness: contribute a safety invariant that is not on our list](https://github.com/tonydzi/charm-os/issues/1)
- [turnstate: write a ledger adapter for a harness that is not Claude Code](https://github.com/tonydzi/charm-os/issues/2)

Issues labelled [`accepted`](https://github.com/tonydzi/charm-os/issues?q=is%3Aissue+is%3Aopen+label%3Aaccepted) are scoped, free to take, and nobody is on them.
Comment **"claiming this"** — no permission needed — and it is yours for 7 days.
New here? Start with [`good first issue`](https://github.com/tonydzi/charm-os/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

**You keep the copyright to your code.** No CLA, no assignment, ever — your contribution goes
in under this repo's existing license, the same terms as ours. We answer every issue and PR
within 48 hours, including "no, and here is why"; our silence is our bug, so ping the thread.

Full deal: [CONTRIBUTING.md](https://github.com/tonydzi/.github/blob/main/CONTRIBUTING.md)

<!--we-ask:end-->

---

<!--ecosystem-map:start-->

## 🧩 One piece of a working system

This repository is one piece lifted out of a live operation: one non-technical founder, an AI
cofounder, and a fleet of machines that reach consensus with each other and wake the human only
for money or the irreversible. It was extracted after it survived production, not written as a
demo — and it runs on its own: nothing here phones home to the rest.

**See how the whole thing fits together → [SYSTEM.md](https://github.com/tonydzi/tonydzi/blob/main/SYSTEM.md)**

Its closest neighbours in the **governance** layer: [`agent-approval-gate`](https://github.com/tonydzi/agent-approval-gate) · [`claude-bible`](https://github.com/tonydzi/claude-bible) · [`agent-leash`](https://github.com/tonydzi/agent-leash)

<!--ecosystem-map:end-->

<!-- READ-WITH-AI:START (generated by read_with_ai.py - do not hand-edit) -->

### READ THIS WITH AI

One click and an agent reads the repo, pulls out the patterns and helps you apply them to your own work.

<a href="https://chatgpt.com/codex?prompt=Read%20this%20repo%3A%20https%3A%2F%2Fgithub.com%2Ftonydzi%2Fcharm-os%20%28%E2%80%9Ccharm-os%E2%80%9D%20-%20CharmOS%20%2F%20C%28H%2BA%29RM%20%E2%80%94%20open-source%20framework%20to%20manage%20humans%20AND%20AI%20agents%20as%20first-class%20relationships%2C%20on%20a%20personal%20second%20brain%2C%20driven%20by%20the%20RDR%20loop%20%28Recall%20to%20Deep%20Research%29%29.%20Work%20out%20what%20problem%20it%20actually%20solves%2C%20pull%20out%20the%20reusable%20patterns%20and%20help%20me%20apply%20them%20to%20my%20own%20setup.%20Start%20by%20asking%20what%20I%20am%20working%20on."><img alt="Codex - open" src="https://img.shields.io/badge/Codex-open-000000?style=for-the-badge&logo=openai&logoColor=white"></a> <a href="https://chatgpt.com/?q=Read%20this%20repo%3A%20https%3A%2F%2Fgithub.com%2Ftonydzi%2Fcharm-os%20%28%E2%80%9Ccharm-os%E2%80%9D%20-%20CharmOS%20%2F%20C%28H%2BA%29RM%20%E2%80%94%20open-source%20framework%20to%20manage%20humans%20AND%20AI%20agents%20as%20first-class%20relationships%2C%20on%20a%20personal%20second%20brain%2C%20driven%20by%20the%20RDR%20loop%20%28Recall%20to%20Deep%20Research%29%29.%20Work%20out%20what%20problem%20it%20actually%20solves%2C%20pull%20out%20the%20reusable%20patterns%20and%20help%20me%20apply%20them%20to%20my%20own%20setup.%20Start%20by%20asking%20what%20I%20am%20working%20on."><img alt="ChatGPT - open" src="https://img.shields.io/badge/ChatGPT-open-10a37f?style=for-the-badge&logo=openai&logoColor=white"></a> <a href="https://claude.ai/new?q=Read%20this%20repo%3A%20https%3A%2F%2Fgithub.com%2Ftonydzi%2Fcharm-os%20%28%E2%80%9Ccharm-os%E2%80%9D%20-%20CharmOS%20%2F%20C%28H%2BA%29RM%20%E2%80%94%20open-source%20framework%20to%20manage%20humans%20AND%20AI%20agents%20as%20first-class%20relationships%2C%20on%20a%20personal%20second%20brain%2C%20driven%20by%20the%20RDR%20loop%20%28Recall%20to%20Deep%20Research%29%29.%20Work%20out%20what%20problem%20it%20actually%20solves%2C%20pull%20out%20the%20reusable%20patterns%20and%20help%20me%20apply%20them%20to%20my%20own%20setup.%20Start%20by%20asking%20what%20I%20am%20working%20on."><img alt="Claude - open" src="https://img.shields.io/badge/Claude-open-d97757?style=for-the-badge&logo=anthropic&logoColor=white"></a>

<details>
<summary>Copy the prompt (works in any agent: Gemini, Grok, a local model, your own CLI)</summary>

```text
Read this repo: https://github.com/tonydzi/charm-os (“charm-os” - CharmOS / C(H+A)RM — open-source framework to manage humans AND AI agents as first-class relationships, on a personal second brain, driven by the RDR loop (Recall to Deep Research)). Work out what problem it actually solves, pull out the reusable patterns and help me apply them to my own setup. Start by asking what I am working on.
```

</details>

<sub>— TonyDzi, Palo Alto AI Research Lab · second brain, agent coordination, persistent memory: github.com/tonydzi</sub>

<!-- READ-WITH-AI:END -->
