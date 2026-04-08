# NIST CSF Gap Analysis — Consolidated Report
*(CIS MS-ISAC Policy Template Guide 2024 Alignment)*

## 1. Executive Summary
- **Overall Maturity** (in-scope only): Not Started
- **Total Subcategories**: 106 (In Scope: 25, Out of Scope: 81)
- **In-Scope Results**: Addressed: 0 | Partially Addressed: 2 | Not Addressed: 23
- **Critical Finding**: 23 in-scope subcategories are not addressed. The Govern function has the most gaps (19 not addressed).

## 1.5 Per-Function Executive Summaries

### Govern
**Maturity**: Not Started

The assessment of the Govern function reveals significant gaps, as zero of the 19 in-scope subcategories were addressed by the current policy. Nineteen subcategories were found to be 'Not Addressed,' indicating a complete lack of documented controls across the governance domain. Critical gaps exist in areas such as establishing organizational context (GV.OC-01), defining risk management objectives (GV.RM-01), and managing legal/regulatory requirements (GV.OC-03). Key recommendations involve developing a comprehensive security policy that explicitly incorporates risk appetite, stakeholder expectations, and formal supply chain risk management processes to address these deficiencies.

**Critical Gaps:**
- GV.OC-01
- GV.OC-02
- GV.OC-03

### Identify
**Maturity**: Not Started

The Identify function assessment revealed significant gaps, with 3 subcategories being entirely unaddressed and 1 subcategory only partially addressed. Critical gaps exist in areas such as Asset Management procedures, Access Control policies, and formal Assessment of Policy Compliance (ID.AM-8, ID.RA-07, ID.RA-10). Key recommendations include immediately developing policies for Asset Management, Access Control, and Identification and Authentication to establish foundational security controls. Furthermore, policies covering System and Communications Protection and Incident Response must be established to address the remaining out-of-scope requirements.

**Critical Gaps:**
- ID.AM-8
- ID.RA-07
- ID.RA-10

### Protect
**Maturity**: Partially Implemented

The Protect function shows a partial implementation maturity, with only two in-scope subcategories assessed. The most critical gaps involve data protection, specifically the lack of mandates for data in transit encryption (PR.DS-02) and comprehensive data-at-rest encryption and key management (PR.DS-01). Key recommendations include immediately mandating encryption for all storage locations and establishing protocols for data-in-transit protection. To address the extensive out-of-scope requirements, separate policies must be developed for all listed access control, system lifecycle, and incident response subcategories.

**Critical Gaps:**
- PR.DS-02
- PR.DS-01

### Detect
**Maturity**: N/A — No subcategories in scope for this policy type

The Detect function is entirely out of scope for this policy document. All 11 subcategories require separate, dedicated policy documents. No gap analysis was performed for this function.

### Respond
**Maturity**: N/A — No subcategories in scope for this policy type

The Respond function is entirely out of scope for this policy document. All 13 subcategories require separate, dedicated policy documents. No gap analysis was performed for this function.

### Recover
**Maturity**: N/A — No subcategories in scope for this policy type

The Recover function is entirely out of scope for this policy document. All 8 subcategories require separate, dedicated policy documents. No gap analysis was performed for this function.


## 2. Maturity by Function
| Function | Rating | In Scope | Addressed | Partial | Not Addressed | Out of Scope |
|----------|--------|----------|-----------|---------|---------------|--------------|
| Govern | Not Started | 19 | 0 | 0 | 19 | 12 |
| Identify | Not Started | 4 | 0 | 1 | 3 | 17 |
| Protect | Partially Implemented | 2 | 0 | 1 | 1 | 20 |
| Detect | N/A — No subcategories in scope for this policy type | 0 | 0 | 0 | 0 | 11 |
| Respond | N/A — No subcategories in scope for this policy type | 0 | 0 | 0 | 0 | 13 |
| Recover | N/A — No subcategories in scope for this policy type | 0 | 0 | 0 | 0 | 8 |

## 3. In-Scope Gaps (Not Addressed)
These are gaps the current policy SHOULD cover but does not:

| Subcategory ID | Function | Gap | Recommended Action |
|----------------|----------|-----|--------------------|
| GV.OC-01 | Govern | The provided evidence snippets do not contain any information regarding the customer's security poli | Request the customer's Information Security Policy to perform the assessment. |
| GV.OC-02 | Govern | The policy does not address the requirement for understanding and considering the needs and expectat | The customer must develop or update their policy to include provisions for stakeholder analysis, doc |
| GV.OC-03 | Govern | The provided evidence explicitly states that no relevant passages were found in any policy section,  | The customer must develop or update their security policy to include provisions for understanding, m |
| GV.OC-04 | Govern | The policy does not address the requirement for formally documenting critical business services, pri | The organization should develop or update the Computer Security Threat Response Policy to formally d |
| GV.RM-01 | Govern | The provided evidence snippets do not contain any relevant passages from the customer's security pol | The customer must provide relevant policy sections to allow for an assessment against the GV.RM-01 r |
| GV.RM-02 | Govern | The provided evidence snippets do not contain any information regarding the establishment, communica | The customer must develop and incorporate formal risk appetite and tolerance statements into their s |
| GV.RM-03 | Govern | The provided evidence snippets do not contain any information regarding the customer's security poli | The customer must provide relevant policy documentation (e.g., Information Security Policy, Risk Ass |
| GV.RM-04 | Govern | The provided evidence snippets do not contain any information regarding the organization's risk resp | The customer must develop and document preferred risk response strategies (accept, avoid, transfer,  |
| GV.RM-05 | Govern | The provided evidence snippets do not contain any information regarding documented processes for rep | The customer must develop and document communication channels for risk reporting, establish escalati |
| GV.SC-01 | Govern | The policy does not address the requirements for a formal cybersecurity supply chain risk management | The customer needs to develop and implement a C-SCRM policy and program charter, define objectives a |
| GV.SC-02 | Govern | The customer policy does not contain any relevant passages to assess against the requirement for est | The customer must develop or update their policy to explicitly define cybersecurity responsibilities |
| GV.SC-03 | Govern | The customer policy does not address the requirement for integrating cybersecurity supply chain risk | The customer must update their policy to explicitly address the integration of supply chain risk man |
| GV.SC-04 | Govern | The provided evidence does not contain any policy text to assess against the GV.SC-04 requirement. | The customer policy must be reviewed to determine if it addresses the requirements of GV.SC-04, spec |
| GV.SC-05 | Govern | The customer policy does not contain any relevant passages addressing the requirements for establish | The customer must develop or update their policy to include specific requirements for managing cyber |
| GV.SC-06 | Govern | The customer policy does not address the requirement for performing planning and due diligence to re | The customer should develop or update their policy to include a formal pre-engagement security asses |
| GV.SC-07 | Govern | The customer policy does not address the requirements of GV.SC-07. | The customer must develop or update its policy to address the requirements of GV.SC-07, including es |
| GV.SC-08 | Govern | The customer policy does not address the requirement that relevant suppliers and other third parties | The customer needs to update their policy to explicitly address supply chain risk management related |
| GV.SC-09 | Govern | The provided evidence does not contain any policy text to assess against the requirements of GV.SC-0 | The customer must provide relevant policy sections to allow for an assessment against the GV.SC-09 r |
| GV.SC-10 | Govern | The customer policy does not address the requirement for cybersecurity supply chain risk management  | The customer must develop and implement a formal supplier offboarding process, including requirement |
| ID.AM-8 | Identify | The provided evidence snippets do not contain any relevant policy text to assess compliance with the | The customer must provide relevant policy sections to allow for an assessment. |
| ID.RA-07 | Identify | The provided evidence snippets do not contain any relevant policy text to assess compliance with the | The customer must provide relevant policy sections to allow for an assessment of compliance with ID. |
| ID.RA-10 | Identify | The provided evidence snippets do not contain any relevant policy text to assess compliance with the | Review the customer's 'Identification and Authentication Policy' and related policies to determine i |
| PR.DS-02 | Protect | The policy does not explicitly mandate the use of encryption for data in transit, which is the core  | The policy needs to be updated to explicitly address the protection of data in transit, including re |

## 4. In-Scope Gaps (Partially Addressed)
| Subcategory ID | Function | Gap | Recommended Action |
|----------------|----------|-----|--------------------|
| ID.AM-7 | Identify | The policy defines data classification (Public and Confidential), which addresses the need to classi | The policy needs to be expanded to include procedures for conducting data discovery exercises, docum |
| PR.DS-01 | Protect | The policy establishes the need for data at rest protection and identifies encryption as the primary | The policy needs to be expanded to explicitly mandate encryption for all specified data-at-rest loca |

## 5. Missing Policy Documents
Out-of-scope subcategories grouped by the policy template needed:

| Missing Policy Template | Count | NIST Subcategories Covered |
|-------------------------|-------|---------------------------|
| Computer Security Threat Response Policy | 30 | DE.AE-06, DE.AE-08, ID.IM-01, ID.IM-02, ID.IM-03, ID.IM-04, ID.RA-05, ID.RA-06, ID.RA-08, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-03, RS.AN-06, RS.AN-07, RS.AN-08, RS.CO-02, RS.CO-03, RS.MA-01, RS.MA-02, RS.MA-03, RS.MA-04, RS.MA-05, RS.MI-01, RS.MI-02 |
| Cyber Incident Response Standard | 30 | DE.AE-06, DE.AE-08, ID.IM-01, ID.IM-02, ID.IM-03, ID.IM-04, ID.RA-05, ID.RA-06, ID.RA-08, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-03, RS.AN-06, RS.AN-07, RS.AN-08, RS.CO-02, RS.CO-03, RS.MA-01, RS.MA-02, RS.MA-03, RS.MA-04, RS.MA-05, RS.MI-01, RS.MI-02 |
| Incident Response Policy | 30 | DE.AE-06, DE.AE-08, ID.IM-01, ID.IM-02, ID.IM-03, ID.IM-04, ID.RA-05, ID.RA-06, ID.RA-08, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-03, RS.AN-06, RS.AN-07, RS.AN-08, RS.CO-02, RS.CO-03, RS.MA-01, RS.MA-02, RS.MA-03, RS.MA-04, RS.MA-05, RS.MI-01, RS.MI-02 |
| Information Security Policy | 22 | DE.AE-06, DE.AE-08, GV.OC-05, GV.OV-01, GV.OV-02, GV.OV-03, GV.RM-06, GV.RM-07, GV.RR-01, GV.RR-02, GV.RR-03, GV.RR-04, ID.AM-1, ID.AM-2, ID.AM-5, ID.RA-03, ID.RA-05, ID.RA-06, ID.RA-08, PR.AA-06, PR.AT-01, PR.AT-02 |
| Contingency Planning Policy | 19 | ID.IM-02, ID.IM-03, ID.IM-04, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-03, RS.AN-06, RS.AN-07, RS.AN-08, RS.CO-02, RS.CO-03, RS.MI-01, RS.MI-02 |
| System and Information Integrity Policy | 16 | DE.AE-02, DE.AE-03, DE.AE-04, DE.AE-07, DE.AE-08, DE.CM-01, DE.CM-02, DE.CM-03, DE.CM-06, DE.CM-09, ID.RA-01, ID.RA-02, ID.RA-04, ID.RA-09, PR.IR-03, PR.IR-04 |
| Auditing and Accountability Standard | 12 | DE.AE-02, DE.AE-03, DE.AE-04, DE.AE-07, DE.CM-01, DE.CM-02, DE.CM-03, DE.CM-06, DE.CM-09, ID.RA-01, ID.RA-02, ID.RA-04 |
| Vulnerability Scanning Standard | 12 | DE.AE-02, DE.AE-03, DE.AE-07, DE.AE-08, DE.CM-01, DE.CM-02, DE.CM-03, DE.CM-06, ID.RA-01, ID.RA-02, ID.RA-03, ID.RA-04 |
| Security Logging Standard | 11 | DE.AE-02, DE.AE-03, DE.AE-07, DE.CM-01, DE.CM-02, DE.CM-03, DE.CM-06, DE.CM-09, ID.RA-01, ID.RA-02, ID.RA-04 |
| Access Control Policy | 8 | ID.AM-1, ID.AM-2, PR.AA-01, PR.AA-02, PR.AA-04, PR.AA-05, PR.AT-02, PR.PS-03 |
| Identification and Authentication Policy | 8 | ID.AM-1, ID.AM-2, PR.AA-01, PR.AA-02, PR.AA-04, PR.AA-05, PR.AT-02, PR.PS-04 |
| Security Awareness and Training Policy | 7 | GV.PO-01, GV.PO-02, GV.RR-01, GV.RR-02, GV.RR-04, PR.AT-01, PR.AT-02 |
| Account Management/Access Control Standard | 7 | ID.AM-1, ID.AM-2, PR.AA-01, PR.AA-02, PR.AA-04, PR.AA-05, PR.AT-02 |
| Maintenance Policy | 7 | DE.CM-01, ID.RA-03, PR.AA-06, PR.DS-10, PR.DS-11, PR.IR-02, PR.PS-02 |
| Configuration Management Policy | 7 | PR.AA-01, PR.AA-02, PR.AA-04, PR.AA-05, PR.AT-02, PR.PS-01, PR.PS-05 |
| Information Security Risk Management Standard | 6 | GV.OV-01, GV.OV-02, GV.OV-03, GV.RM-06, GV.RM-07, GV.RR-03 |
| Risk Assessment Policy | 6 | GV.OV-01, GV.OV-02, GV.OV-03, GV.RM-06, GV.RM-07, GV.RR-03 |
| Acceptable Use of Information Technology Resource Policy | 6 | GV.RR-01, GV.RR-02, ID.AM-1, ID.AM-2, PR.AT-01, PR.AT-02 |
| Sanitization Secure Disposal Standard | 6 | PR.AA-01, PR.AA-05, PR.DS-10, PR.IR-02, PR.PS-03, PR.PS-06 |
| System and Communications Protection Policy | 5 | GV.OC-05, ID.AM-3, ID.AM-4, PR.AA-06, PR.IR-01 |
| Personnel Security Policy | 5 | GV.PO-01, GV.PO-02, GV.RR-04, PR.AT-01, PR.AT-02 |
| Physical and Environmental Protection Policy | 5 | GV.PO-01, GV.PO-02, GV.RR-04, PR.AT-01, PR.AT-02 |
| Media Protection Policy | 5 | ID.RA-03, PR.AA-06, PR.DS-10, PR.DS-11, PR.IR-01 |
| Secure Configuration Standard | 5 | PR.AA-01, PR.AA-05, PR.DS-10, PR.IR-02, PR.PS-05 |
| Secure System Development Life Cycle Standard | 5 | PR.AA-01, PR.AA-05, PR.DS-10, PR.IR-02, PR.IR-03 |
| Mobile Device Security | 4 | ID.RA-03, PR.AA-06, PR.DS-10, PR.IR-01 |
| Security Assessment and Authorization Policy | 3 | ID.AM-1, ID.AM-2, ID.RA-03 |
| Encryption Standard | 3 | ID.RA-03, PR.AA-06, PR.IR-01 |
| Authentication Tokens Standard | 3 | PR.AA-02, PR.AA-04, PR.AT-02 |
| Remote Access Standard | 3 | PR.AA-03, PR.AA-05, PR.IR-01 |
| Information Classification Standard | 2 | GV.OC-05, ID.AM-5 |
| Systems and Services Acquisition Policy | 1 | ID.IM-04 |
| Patch Management Standard | 1 | ID.RA-03 |
| 802.11 Wireless Network Security Standard | 1 | PR.IR-03 |
| Secure Coding Standard | 1 | DE.AE-02 |

## 6. Prioritized Remediation Roadmap

| Priority | Action | Details |
|----------|--------|---------|
| **1 — Immediate (0–30 days)** | Address critical in-scope gaps | GV.OC-01, GV.OC-02, GV.OC-03, GV.OC-04, GV.RM-01, GV.RM-02, GV.RM-03, GV.RM-04, GV.RM-05, GV.SC-01 |
| **2 — Short-term (30–90 days)** | Strengthen partially addressed areas | ID.AM-7, PR.DS-01 |
| **3 — Medium-term (90–180 days)** | Create missing policy documents | 802.11 Wireless Network Security Standard, Acceptable Use of Information Technology Resource Policy, Access Control Policy, Account Management/Access Control Standard, Auditing and Accountability Standard |
