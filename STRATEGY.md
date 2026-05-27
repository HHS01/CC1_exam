### Monitoring Education Vulnerability in Burkina Faso: A Hybrid Data Approach
**Response to RFP: Strengthening Education Continuity in Conflict-Affected Regions**

#### 1. CONTEXT
Burkina Faso is facing an unprecedented education crisis. As of 2024, the intersection of acute insecurity and structural fragility has pushed the education system to a point where reactive aid is no longer sufficient. Field staff in regions like **Sahel** and **Est** witness the daily reality of school closures, yet their observations often lack a systematic framework for long-term prioritisation.

Our analysis reveals that in 2023 alone, the **Koulpelogo** province recorded **120 conflict events** and **527 fatalities**, while the national primary out-of-school population reached an estimated **1.6 million children**. This dual burden creates a "vulnerability trap." While historical data from UNESCO and ACLED often carries reporting lags, it remains the most reliable baseline for identifying **structural fragility**—the regions where the education system is least resilient to future shocks.

By introducing the **Education Vulnerability Index (EVI)**, we identify which of Burkina Faso's 45 provinces have the deepest historical vulnerability. This allows EBI to shift from a "first-response" model to a "structural resilience" model—prioritising support for regions like **Soum** and **Yatenga** that consistently show the highest levels of combined threat and fragility over a 12-year horizon.

#### 2. OBJECTIVES
1. **Classify all 45 BFA provinces by structural vulnerability tier**, enabling EBI to identify that regions like **Soum** and **Sahel** face compounded risk—not just acute conflict, but the weakest education infrastructure to absorb it.
2. **Deploy an Interactive Monitoring Platform** that allows EBI leadership to perform deep-dives into provincial metrics, comparing acute security exposure in **Est** or **Boucle du Mouhoun** against long-term infrastructure gaps.
3. **Institutionalise Evidence-Based Resource Allocation**, ensuring that annual budget cycles are informed by a systematic "common operating picture" of education risk, rather than relying solely on field reports that arrive unevenly.

#### 3. APPROACH
Our approach moves beyond isolated indicators to measure "Hybrid Vulnerability." We recognise that while a single attack might close a school today, the underlying system health determines if that school can ever reopen. The EVI is not a "crystal ball" for real-time events, but a diagnostic tool for **systemic risk**.

The platform provides a suite of features designed for strategic planning:
*   **Province-Level Drill-Downs:** Users can click any province, such as **Gourma**, to see a detailed breakdown of security exposure (events/fatalities) versus structural fragility (school density gaps).
*   **Time-Series Trajectories (2015–2026):** Visualising 12-year trends allows EBI to identify regions where risk is escalating versus those where it is chronic.
*   **Hybrid Scoring Methodology:** A weighted composite (50% Security, 25% Infrastructure, 25% National Education Baseline) that normalises disparate data into actionable priority tiers (Critical, High, Medium, Low).

**Technical Differentiators:**
*   **"Double Jeopardy" Risk Typology:** Beyond a single score, we classify regions into actionable risk profiles: *Double Jeopardy* (High conflict/Low infrastructure), *Flashpoints* (Acute security spikes), and *Structural Fragility* (Long-term neglect).
*   **Multi-Source "Resilience" Fetching:** Our pipeline implements a fail-safe engine that prioritises official **HDX** (UNICEF/OCHA) data, with an automated fallback to **OpenStreetMap (OSM)** via the Overpass API, ensuring data reliability across diverse geographies.
*   **Historical "Trauma" Scoring:** The system tracks multi-year conflict exposure at the site level, distinguishing between new incident clusters and chronic institutional trauma.
*   **Contextual Zoom Scaling:** The map interface dynamically transitions from provincial-level hotspots to site-level incident pins, providing both strategic overview and operational detail in a single view.

**Explore the Full Prototype:** [Central Analysis Hub](https://rsnl42.github.io/CC1_exam/)

#### 4. PROPOSED ACTIVITIES
*   **Activity 1: Multi-Sectoral Data Harmonization**
    Map all 45 provinces using the latest OCHA administrative boundaries. We will standardise nomenclature across datasets (e.g., aligning ACLED's **'Kossi'** with the official **'Kossin'**) to ensure EBI can cross-reference education data with security reports seamlessly.
*   **Activity 2: Capability-Driven Dashboard Deployment**
    Deploy the interactive platform to enable regional programme managers to enter annual resource allocation meetings with a ranked shortlist of provinces requiring immediate attention, rather than relying solely on field reports that arrive unevenly.
*   **Activity 3: Transfer & Sustainability Training**
    Deliver the complete Python-based data pipeline and a detailed methodology guide. This enables EBI to update the baseline as new UNESCO figures or ACLED archives become available, ensuring the tool remains a long-term asset.

#### 5. DELIVERABLES
| Deliverable | Description |
| :--- | :--- |
| **Provincial Risk Profiles** | Comprehensive datasets for 45 provinces, including conflict history, out-of-school estimates, and EVI scores. |
| **School Infrastructure Risk Layer** | Site-level vulnerability assessment for all mapped schools in BFA, integrating conflict proximity and provincial density gap. |
| **Interactive Strategic Dashboard** | A web-based platform featuring interactive maps, trend sparklines, and provincial data panels. |
| **Reproducible Data Pipeline** | The automated toolset for fetching, cleaning, and indexing country-wide vulnerability data. |
| **Methodology & User Guide** | Documentation covering data sources, scoring logic, and instructions for strategic interpretation. |

#### 6. CONCLUSION
By moving from a reactive to a structural resilience model, EBI gains a strategic advantage in the fight for education continuity. **The day after receiving this system, EBI will be able to transition from responding to yesterday's headlines to proactively fortifying the schools where the next decade of education is most at risk.**
