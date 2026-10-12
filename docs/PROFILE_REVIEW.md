# Professional profile refresh — copy-ready content and fact checklist

This document contains the copy-ready text for updating LinkedIn, the
alignment notes for the CV (which is generated from `data/cv.yaml` and
`data/publications.yaml`), and a checklist of details that still need
confirmation before anything is published.

Nothing in this repository modifies external accounts automatically. Apply the
LinkedIn changes by hand and verify every item in the checklist first.

---

## 1. LinkedIn headline

```
Machine Learning Researcher | Continual Learning & Machine Unlearning | Representation Geometry
```

## 2. LinkedIn About

```
I am a Machine Learning Researcher and PhD Researcher at GMUM, Jagiellonian University, currently working at IDEAS Research Institute.

My research focuses on continual learning and machine unlearning, with a particular interest in the geometry and modularity of neural representations. I investigate how structure in hidden activation spaces can be leveraged to control interference between tasks, preserve learned capabilities, and selectively modify neural network behaviour.

With a background in computational mathematics, I combine mathematical perspectives with hands-on deep learning research and systems engineering. Alongside developing new methods, I build tools for efficient activation analysis and conduct experiments on modern neural networks, including large-scale diffusion models.
```

## 3. LinkedIn experience descriptions

### IDEAS Research Institute — Senior Machine Learning Research Engineer | May 2026 – Present

```
Researching continual learning and machine unlearning, with an emphasis on activation-space methods for controlling interference and preserving model behaviour.

• Developing methods that use the geometry and structure of neural activations to support continual adaptation and targeted information removal.
• Investigating activation-level constraints and representation-space interventions in diffusion models and other deep neural networks.
• Designing and conducting experiments to evaluate forgetting, retention, and changes in model behaviour.
• Building tools for efficient activation tracking and analysis to support research on large neural networks.
```

### Jagiellonian University — GMUM — PhD Researcher in Technical Computer Science | July 2025 – Present

```
Research on continual learning and machine unlearning, focusing on the structure of neural representations and activation-level mechanisms for controlling model updates.

• Investigating representation-space methods for mitigating catastrophic forgetting and enabling targeted changes to learned behaviour.
• Developing and evaluating methods based on interval-bounded activations and geometric constraints.
• Conducting empirical research on deep neural networks, including diffusion models.
```

### Jagiellonian University — GMUM — Graduate Research Assistant | October 2023 – July 2025

```
• Conducted research in meta-learning, continual learning, and diffusion models.
• Designed neural architectures, custom layers, and end-to-end training pipelines.
• Explored hypergradient methods, neural optimizers, and consistency models.
```

### Jagiellonian University — GMUM — Undergraduate Research Assistant | July 2022 – October 2023

```
• Developed Bayesian extensions of meta-learning models.
• Designed experiments to investigate uncertainty estimation in learning systems.
```

### Aptiv — Computer Vision / Machine Learning Engineer | April 2025 – April 2026

```
• Researched and designed neural network architectures for real-time multi-camera perception.
• Implemented custom TensorRT operators and optimized inference performance.
• Developed high-performance image-processing pipelines using CUDA and x86 SIMD.
• Integrated perception models into real-time systems using low-latency, zero-copy interfaces.
```

### OANDA — Junior Data Scientist | September 2024 – December 2024

```
• Developed a Bayesian Marketing Mix Model in PyMC, covering model specification, inference, and validation.
• Built an interactive Streamlit interface and prepared deployment on Google Cloud Vertex AI.
```

### OANDA — Data Engineer / Associate Data Engineer | March 2023 – September 2024

```
• Designed and maintained transaction-reporting and data-processing pipelines.
• Developed a declarative framework for Apache Beam pipelines and optimized cloud resource utilization.
```

Keep earlier software development experience (EUROLOOP / Willbert) to one
concise entry, as it is on the CV.

## 4. LinkedIn skills

Top 3 highlighted skills: **Machine Learning · Deep Learning · Research**
(use PyTorch as the third highlighted skill if LinkedIn does not offer
"Research").

Full skills section, roughly in this order:

- Core research: Machine Learning · Deep Learning · Continual Learning · Representation Learning · Computer Vision · Research
- Methods and topics: Machine Unlearning · Transfer Learning · Meta-Learning · Generative Models · Diffusion Models · Neural Networks
- Research implementation: PyTorch · Python · CUDA · Model Optimization · Experimental Design · Scientific Computing
- Systems engineering: C++ · TensorRT · High-Performance Computing · GPU Computing · Computer Architecture · Linux · Docker
- Additional: Rust · SQL · Google Cloud Platform (GCP) · Apache Beam · Data Engineering · Bayesian Statistics

## 5. LinkedIn profile details

- Current position: Senior Machine Learning Research Engineer, IDEAS Research Institute.
- Education: PhD in Technical Computer Science, Jagiellonian University; MSc and BSc in Computational Mathematics.
- Featured section: BARRIER, InTAct, ActivationScope, and the personal research website.
- Banner: minimal and typographic (name + three research keywords); avoid generic AI imagery.

## 6. GitHub profile

Bio (already reflected in the website copy):

```
Machine Learning Researcher working on continual learning, machine unlearning, and representation geometry. Building methods and tools for understanding and controlling neural representations.
```

Pinned repositories and order:

| Priority | Repository    | Purpose                          | State |
| -------- | ------------- | -------------------------------- | ----- |
| 1        | BARRIER       | First-author research            | public |
| 2        | InTAct-Flex / link to pkrukowski1/InTAct | Continual learning research | public (fork) |
| 3        | ActivationScope | Research tooling              | public |
| 4        | local-cl      | Earlier work on local neural layers | public |
| 5        | CLASP         | Continual adaptation research    | not public yet |
| 6        | TRTTL         | Systems engineering depth        | public |

Improve each README before cosmetic changes: one-sentence problem statement,
short description of the idea, paper link and citation, implementation and
reproduction section, and current status/limitations where relevant.

## 7. CV

The CV is generated from `data/cv.yaml` and `data/publications.yaml`
(`scripts/generate_cv.py` → `cv/cv.tex` → `static/cv.pdf`). It follows the
website order: profile (same text as the homepage) → selected publications →
research experience (including the NCN grant) → industry experience → teaching →
education → skills. It links GitHub, LinkedIn, Google Scholar, and the website,
and is kept at two A4 pages. Edit the YAML files, then run `make cv`.

## 8. Checklist — confirm before publishing

Publication metadata:

- [ ] BARRIER: confirm the complete author list and the arXiv link (`arXiv:2605.15737` as provided); confirm the repository URL `github.com/OneAndZero24/BARRIER` is the canonical code link.
- [ ] InTAct: confirm the NeurIPS 2026 acceptance wording and the final venue string; add the NeurIPS proceedings link once it exists; confirm the code repository (`github.com/pkrukowski1/InTAct`) should be linked.
- [ ] CLASP: confirm `arXiv:2610.01331` is the correct identifier and the correct author order (`W. Gromski, P. Krukowski, Jan Miksa, M. Zieba, P. Spurek`); add the code URL if one becomes public.
- [ ] Kernel HyperNetworks: confirm the full author list (currently ends with "et al.") and the DOI (`10.1007/s00138-023-01403-4`). Full names vs. initials are a style decision.
- [ ] "Local learning in deep neural networks" is currently hidden (Scholar lists no venue). Decide whether to show it as a thesis/unpublished manuscript, or leave it out.
- [ ] Scholar "cited by" counts are refreshed automatically; they may lag by a few days.

Positions and dates:

- [ ] IDEAS Research Institute: confirm the official title "Senior Machine Learning Research Engineer" and the start date (May 2026).
- [ ] PhD Researcher at GMUM (July 2025 – present) and the PhD programme start year (2025) on the CV education list.
- [ ] Aptiv role dates (April 2025 – April 2026) — note it overlaps with the PhD period.
- [ ] Decide whether the phone number should remain on the public CV (it is currently there, as in the previous CV).

Website:

- [x] `baseURL` set to `https://oneandzero24.github.io/` (root user-site repo); the CV website link matches. Verify once the repository is live.
- [ ] Optionally add `SERPAPI_API_KEY` as a repository secret for a more reliable Scholar sync.
- [ ] Favicons are still the template defaults; replace them if desired.
- [ ] Verify the GitHub Pages source is set to "GitHub Actions" in the repository settings.
- [ ] LinkedIn returns HTTP 999 to automated checks; that is normal and does not indicate a broken link.
