# Research Limitations, Methodological Boundaries & Open Questions

**Study date:** October 18, 2026 | **Project:** Moonshots Research Radar  
**Corpus window:** August 14, 2026 through October 14, 2026 | **Show:** *Moonshots with Peter Diamandis*

---

## 1. What was accomplished vs. What was NOT done

In the interest of scientific integrity and research transparency, we clearly delineate between verified completed work and intentional scope boundaries:

### Verified accomplishments
1. **Complete episode transcript acquisition:** All 24 episodes (22 numbered episodes #280–#301 and 2 unnumbered specials) published within the study window have been fully acquired, timestamped, formatted, and verified in private local storage (`.private/transcripts/`).
2. **Comprehensive second-pass evidence audits:** All 74 unique claims and analytical observations in `data/claims.json` now possess detailed second-pass evidence audit records in `data/evidence_audits.json` (clearing 100% of the previous 33-item backlog).
3. **Primary-source corroboration:** Every cited regulatory document (SEC filings, White House Accords, executive orders), scientific preprint (arXiv, Nature), organizer release (XPRIZE), and financial disclosure (NVIDIA 10-Q) has been checked against original HTTPS sources.
4. **End-to-end multi-segment reviews:** Episodes #299 and #300 have undergone multi-segment textual audits cross-referencing host disclosures, sponsor claims, and technical assertions.
5. **Commercial opportunity assessment:** Eight concrete business opportunities were evaluated across 10 structured dimensions specifically tailored to Switzer Systems' operating model.

### Explicit boundaries and limitations
1. **Textual transcripts vs. Human audio audits:** While full textual transcripts were acquired and verified for all 24 episodes, **0 out of 24 episodes have received complete human end-to-end audio audits.** Selected representative segments (e.g., 60-second samples in #300 and #299) were audited against local Whisper transcriptions to confirm timestamp accuracy and speech-to-text fidelity (~98% match). However, users must not assume every spoken inflection, background nuance, or uncaptioned remark was audited.
2. **Speaker diarization uncertainty:** Automated podcast transcriptions do not natively label speaker switches per sentence. Speaker attributions in `data/claims.json` are reconstructed from dialogue context, episode introductions, and direct vocal cues, but should be independently verified against original audio before quoting in high-stakes legal or commercial contexts.
3. **Frozen temporal cutoff (2026-10-14):** All evidentiary audits are strictly evaluated against evidence available as of October 14, 2026. Any subsequent real-world developments occurring after this date are deliberately treated as future follow-ups to preserve the validity of the 9 prospective forecasts.
4. **No automated forecast adjudication:** All nine preregistered forecasts remain open with deadlines between April 2027 and October 2027. None have been prematurely resolved.

---

## 2. Pervasive biases in the podcast source material

Any synthesis of *Moonshots with Peter Diamandis* must account for systematic structural biases:

1. **Editorial optimism bias:** The show's explicit premise is advancing exponential optimism and technological abundance. Negative externalities, regulatory frictions, implementation failures, and boring incumbent solutions are systematically underrepresented.
2. **Founder & investor self-interest:** Guests are overwhelmingly founders or venture investors promoting their own companies, token ecosystems, or fundraising rounds. For example:
   - Richard Socher (Recursive) promotes recursive AI agent models where host Peter Diamandis is a disclosed seed investor (ep-299).
   - Ben Lamm (Colossal Biosciences) promotes promptable animal de-extinction (ep-297).
   - Martine Rothblatt (United Therapeutics) promotes xenotransplantation and digital consciousness (ep-290).
   - Palmer Luckey (Anduril) promotes defense autonomy (ep-295).
3. **Sponsorship conflation:** Sponsored advertisements (e.g., Fountain Life whole-body MRI, Blitzy AI code automation) are presented by the hosts with enthusiastic personal testimonials that can easily be mistaken for objective research findings if not segregated.
4. **The "Demo-to-Deployment" fallacy:** Guests frequently describe a laboratory prototype, simulated benchmark, or competition finalist as proof that an entire global industry has been transformed.

---

## 3. Unresolved technical & scientific questions

The research cohort leaves several critical questions fundamentally unresolved:

### A. The true scaling limit of test-time compute
Frontier labs are shifting compute budgets from pretraining to inference-time search (o1, Astra, chain-of-thought exploration). However:
- Does test-time search represent genuine emergent reasoning, or does it merely perform tree search over interpolated pattern space?
- At what point does search combinatorial explosion encounter diminishing returns on problems that cannot be formally verified by a compiler or math solver?

### B. The reality of Small Modular Nuclear Reactors (SMRs)
Tech hyperscalers have announced intent to power gigawatt-scale AI datacenters with advanced nuclear reactors. However:
- Regulatory licensing schedules at the US NRC require 4–7 years per site.
- Supply chain bottlenecks in high-assay low-enriched uranium (HALEU) and specialized pressure vessels remain severe.
- Whether commercial SMRs can achieve grid-cost parity with renewables plus battery storage by 2030 remains deeply contested.

### C. The physical manipulation bottleneck in robotics
While video demos of humanoid robots folding laundry or handling boxes are visually impressive:
- What is the actual Mean Time Between Interventions (MTBI) in unstructured domestic or construction environments?
- Can bipedal humanoids achieve the energy efficiency and reliability required to justify a $30,000+ capital cost compared to specialized mobile bases and articulated arms?

### D. True enterprise willingness to pay for autonomous agents
While software developers are enthusiastic about autonomous AI agents:
- Will corporate enterprises grant autonomous agents write access to core financial ledgers, customer databases, and production servers without mandatory human sign-off?
- Does the liability risk of agent errors outweigh the operational savings of automated execution?

---

## 4. Maintenance protocol & next research gates

To maintain the Moonshots Research Radar as a live, authoritative intelligence system:

1. **Forecast monitoring schedule:** Execute `python3 forecast_review.py --as-of <DATE>` quarterly. The earliest due date is **fc-002 on April 14, 2027** (US datacenter demand-response deployment).
2. **Adjudication standard:** When a forecast reaches its deadline, adjudicate solely against the preregistered criteria using primary independent sources. If data is unavailable, classify as `unresolved`; never rewrite the original criterion.
3. **Cohort versioning:** Any analysis of episodes released after October 14, 2026 must be established in a separate cohort directory (`cohort-2026q4/`) to prevent retrospective contamination of the baseline study.
