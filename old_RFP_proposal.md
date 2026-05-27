# Proposal: Data-Driven Strengthening of Education Continuity in Conflict-Affected Regions

**To:** Education Bridge Initiative (EBI)  
**From:** Sunil Raman  
**Date:** May 7, 2026

---

## 1. Executive Summary
In response to EBI’s Request for Proposals (RFP), this document outlines a framework designed to bridge the gap between field-level expertise and widely available digital data. By integrating granular conflict metrics with longitudinal education data, we propose a system that empowers field staff to visualize hidden vulnerabilities, trends and patterns, and prioritize resources where conflict-driven school dropouts are most imminent or prevalent.

## 2. Context: The Conflict-Education Gap
Our preliminary analysis across 24 conflict-affected Humanitarian Response Plan (HRP) countries (ACLED data) reveals that traditional metrics often mask the localized reality of school dropouts (OPRI data). While 'Gross Enrollment' numbers may appear stable, children are often quietly dropping out of schools due to localized violence and conflict events, as seen in the case of [Burkina Faso](https://github.com/rsnl42/CC1_exam/blob/main/Burkina_Faso_conflict_edu.png).

### Key Insights from Preliminary Research:
*   **Conflict vs Persistence:** Sharp spikes in localized conflict (granular, historical ACLED data) correlate with immediate drops in 'Survival Rate', revealing hidden dropout crises that aggregate enrollment figures fail to capture. This results in higher 'OOS' (out-of-school) numbers despite a growing school-age population, as clearly evidenced in [Burkina Faso](https://github.com/rsnl42/CC1_exam/blob/main/Burkina_Faso_oos.png) between 2019-2023.
*   **The Vulnerability Timeline:** Using proximity analysis, we can identify schools within 10km of recurring conflict hotspots at a very granular level and classify them *Vulnerable*. Whilst currently a descriptive solution, it could be used for real-time monitoring as well with access to the most recent ACLED data.
*   **Gender Neutral Interventions:** Preliminary data shows comparable decline in 'Survival Rate's across genders, suggesting universal interventions such as *School Meal programmes* may be more effective than targeted gender-specific responses at this stage, as evidenced by the improvements in [Ethiopia and Mali](https://github.com/rsnl42/CC1_exam/blob/main/May_02/meal_prog_impact_chart.png)
*   **Data Limitation Challenges:** Significant reporting lags and low granularity of data, particularly for educational metrics, results in significant data gaps in constructing an effective knowledge base. Our solution addresses this by suggesting the field team to gather more context specific data in those instances, to avoid having to resort to heuristics and developing ineffective solutions based on faulty/inaccurate premises.

---

## 3. Strategic Phasing: Build and Transfer

We propose a streamlined two-phase approach that embeds our unique *Data/AI differential* directly into EBI operations. This differential leverages automated ingestion pipelines, geospatial risk modeling, and conflict-education correlation to provide insights far beyond static reporting.

### Phase 1: Build (The Monitoring Infrastructure)
We will deploy our data pipeline to automate the ingestion, cleaning and harmonization of fragmented education and conflict data. By integrating granular conflict metrics (ACLED) with localized school registry data (HDX/OSM), we build a persistent and robust data model that functions as an effective monitoring tool, as well as an early warning system.

*   **Key Capabilities:**
    *   **Automated Pipeline:** Transforms disparate, siloed data into a unified, clean, and actionable format.
    *   **Geospatial Modeling:** Maps *Dynamic Vulnerability* by identifying school proximity to high-risk conflict zones at a very granular level, allowing for proactive, rather than reactive, resource allocation.  
    *   **Interactive Insights:** As a key component of our centralized dashboard, the [Interactive Vulnerability Timeline](https://rsnl42.github.io/CC1_exam/timeline_map/index.html) provides longitudinal analysis to track risk migration patterns and vulnerable educational institutions from 1997-2024 with a high level of granularity.
    *   **LLM-Generated Narrative Synthesis:** Passes structured dashboard outputs to an LLM to auto-generate plain language [*Situation Reports*](https://github.com/rsnl42/CC1_exam/blob/main/llm_narrative/pending_sitrep.md) that would assist in identifying at-risk clusters and priority regions without requiring data literacy from the EBI field staff. Summaries are flagged as AI-generated and reviewed by a focal point before distribution, keeping the field team's judgement central to the decision making.

### Phase 2: Transfer (Capacity & Sustainability)
The final phase focuses on organizational independence. We will deliver a **Methodology Guide** and conduct intensive training for EBI staff, ensuring they can operate, maintain and adapt the pipeline without requiring our assistance. Our system is designed to be *indicator-agnostic*, enabling EBI to incorporate new metrics or geographic regions autonomously. The [Humanitarian Pipeline](https://rsnl42.github.io/CC1_exam/humanitarian_pipeline/README.md) demonstrates this modularity, ensuring that the Analysis Hub remains an enduring asset, not a project-based deliverable.

---

## 4. Deliverables
The following tangible outputs will be delivered as part of this engagement:

| Category | Deliverable | Description |
| :--- | :--- | :--- |
| **Technical** | **Central Analysis Hub** | An interactive, real-time dashboard for EBI-wide school vulnerability monitoring. |
| **Strategy** | **Methodology Guide** | A comprehensive manual for automating & maintaining the data pipeline. |
| **Capacity** | **Staff Training Workshop** | Hands-on training session for field staff on data interpretation and tool use. |
| **Data** | **Harmonized Dataset** | A cleaned, multi-year dataset of school sites and conflict events for 24 countries, ready for internal analysis. |

---

## 5. Conclusion
By reducing the time to assemble a cross-regional picture from weeks to hours, EBI can redirect resources to the identified at-risk schools *before* the dropout spikes rather than after. Across EBI's 12 operating countries and 800 supported schools, this means earlier interventions, better-targeted programming, and decisions grounded in evidence rather than incomplete field reports. By grounding technical innovation in field-level reality, EBI can ensure that education continuity is maintained even in the most volatile environments. This partnership will provide the tools needed to protect the future of children where it is most at risk.

**Explore the Full Prototype:** [Central Analysis Hub](https://rsnl42.github.io/CC1_exam/)

[**My GitHub Repo**](https://github.com/rsnl42/CC1_exam) 