# NIST CSF Gap Analysis — Consolidated Report
*(CIS MS-ISAC Policy Template Guide 2024 Alignment)*

## 1. Executive Summary
- **Overall Maturity** (in-scope only): Substantially Implemented
- **Total Subcategories**: 106 (In Scope: 32, Out of Scope: 74)
- **In-Scope Results**: Addressed: 8 | Partially Addressed: 24 | Not Addressed: 0
- **Critical Finding**: All in-scope subcategories have at least partial coverage.

## 1.5 Per-Function Executive Summaries

### Govern
**Maturity**: Partially Implemented

The Govern function has 6 subcategories in scope, of which 1 are fully addressed (16%), 5 partially addressed, and 0 not addressed. Overall maturity: Partially Implemented.

**Critical Gaps:**
- GV.OC-02: The evidence confirms that stakeholders are understood, but it does not explicitly detail the process for conducting a f
- GV.PO-01: The evidence shows enforcement mechanisms (disciplinary action) are defined, but it does not explicitly demonstrate that
- GV.PO-02: The evidence indicates an annual review and updates based on significant changes (Snippet 5). However, the guidance sugg

### Identify
**Maturity**: Partially Implemented

The Identify function has 9 subcategories in scope, of which 1 are fully addressed (11%), 8 partially addressed, and 0 not addressed. Overall maturity: Partially Implemented.

**Critical Gaps:**
- ID.AM-1: The evidence confirms that inventories are maintained, but it does not explicitly confirm the implementation guidance re
- ID.AM-2: The evidence confirms that inventories are maintained and mentions their use for patch management and identifying vulner
- ID.AM-3: The evidence shows controls (firewall rules, segmentation) but does not explicitly confirm the maintenance of network fl

### Protect
**Maturity**: Substantially Implemented

The Protect function has 6 subcategories in scope, of which 4 are fully addressed (66%), 2 partially addressed, and 0 not addressed. Overall maturity: Substantially Implemented.

**Critical Gaps:**
- PR.IR-01: The evidence confirms segmentation, MFA for remote access, and monitoring for unauthorized access attempts. However, the
- PR.PS-01: The evidence confirms that configuration management practices are established and that secure baseline configurations ar

### Detect
**Maturity**: Partially Implemented

The Detect function has 6 subcategories in scope, of which 1 are fully addressed (16%), 5 partially addressed, and 0 not addressed. Overall maturity: Partially Implemented.

**Critical Gaps:**
- DE.AE-02: The evidence confirms that security events are investigated, but it does not explicitly confirm the implementation of a 
- DE.AE-03: The evidence shows logging of authentication events and user activity, but it does not explicitly confirm that these log
- DE.AE-04: The evidence describes the review and escalation timeline for security alerts, but it does not explicitly state that ana

### Respond
**Maturity**: Substantially Implemented

The Respond function has 5 subcategories in scope, of which 1 are fully addressed (20%), 4 partially addressed, and 0 not addressed. Overall maturity: Substantially Implemented.

**Critical Gaps:**
- RS.AN-03: The evidence confirms that analysis is performed and logging supports forensics. However, the evidence does not explicit
- RS.AN-07: The evidence confirms that logs are collected and retained, which supports the foundation of forensic analysis. However,
- RS.MI-01: The evidence confirms that containment strategies depend on the incident type, but it does not explicitly confirm if 'co

### Recover
**Maturity**: N/A — No subcategories in scope for this policy type

The Recover function has 0 subcategories in scope, of which 0 are fully addressed (0%), 0 partially addressed, and 0 not addressed. Overall maturity: N/A — No subcategories in scope for this policy type.


## 2. Maturity by Function
| Function | Rating | In Scope | Addressed | Partial | Not Addressed | Out of Scope |
|----------|--------|----------|-----------|---------|---------------|--------------|
| Govern | Partially Implemented | 6 | 1 | 5 | 0 | 25 |
| Identify | Partially Implemented | 9 | 1 | 8 | 0 | 12 |
| Protect | Substantially Implemented | 6 | 4 | 2 | 0 | 16 |
| Detect | Partially Implemented | 6 | 1 | 5 | 0 | 5 |
| Respond | Substantially Implemented | 5 | 1 | 4 | 0 | 8 |
| Recover | N/A — No subcategories in scope for this policy type | 0 | 0 | 0 | 0 | 8 |

## 3. In-Scope Gaps (Not Addressed)
These are gaps the current policy SHOULD cover but does not:

*No in-scope subcategories are fully unaddressed.*

## 4. In-Scope Gaps (Partially Addressed)
| Subcategory ID | Function | Gap | Recommended Action |
|----------------|----------|-----|--------------------|
| GV.OC-02 | Govern | The evidence confirms that stakeholders are understood, but it does not explicitly detail the proces | Conduct a formal stakeholder analysis to identify all internal and external stakeholders (e.g., IT,  |
| GV.PO-01 | Govern | The evidence shows enforcement mechanisms (disciplinary action) are defined, but it does not explici | Update the policy documentation to explicitly reference the organization's risk assessment findings  |
| GV.PO-02 | Govern | The evidence indicates an annual review and updates based on significant changes (Snippet 5). Howeve | Implement a formal policy review cycle that includes scheduled annual reviews (as mentioned in Snipp |
| GV.RR-01 | Govern | The evidence confirms leadership responsibility but lacks specific implementation guidance mentioned | Document executive-level cybersecurity responsibilities formally and include cybersecurity culture e |
| GV.RR-02 | Govern | The evidence shows *what* controls are in place (provisioning, RBAC, access reviews) but does not ex | Develop and formally document a cybersecurity RACI matrix. Integrate specific cybersecurity responsi |
| ID.AM-1 | Identify | The evidence confirms that inventories are maintained, but it does not explicitly confirm the implem | Update the policy to include specific requirements for automated hardware discovery, integration wit |
| ID.AM-2 | Identify | The evidence confirms that inventories are maintained and mentions their use for patch management an | Update the relevant policy section to explicitly include requirements for tagging software inventory |
| ID.AM-3 | Identify | The evidence shows controls (firewall rules, segmentation) but does not explicitly confirm the maint | Update the System and Communications Protection Policy to include a requirement for creating and mai |
| ID.AM-5 | Identify | The evidence confirms prioritization based on classification, criticality, resources, and impact. Ho | Develop and document an Information Classification Standard (as referenced in the Required Policy Te |
| ID.AM-8 | Identify | The evidence confirms lifecycle management is addressed, but it does not explicitly detail the integ | Update the policy to explicitly include requirements for integrating security controls into the asse |
| ID.IM-01 | Identify | The evidence shows that findings are generated, but it does not explicitly confirm the existence of  | Develop a formal process that mandates the creation of a findings report and a corresponding improve |
| ID.IM-03 | Identify | The evidence confirms the existence of a channel for reporting improvements (Snippet 1 & 4). However | Develop and document a formal process that captures, tracks, prioritizes, and incorporates operation |
| ID.IM-04 | Identify | The evidence confirms that plans are 'established, communicated, maintained, and improved,' but it d | Update the policy to explicitly state the frequency for reviewing and updating operational cybersecu |
| PR.IR-01 | Protect | The evidence confirms segmentation, MFA for remote access, and monitoring for unauthorized access at | Update the policy or related standards to explicitly include a requirement for implementing Network  |
| PR.PS-01 | Protect | The evidence confirms that configuration management practices are established and that secure baseli | Update the Configuration Management Policy to explicitly state that secure baseline configurations a |
| DE.AE-02 | Detect | The evidence confirms that security events are investigated, but it does not explicitly confirm the  | Implement a Security Information and Event Management (SIEM) or equivalent log analysis platform to  |
| DE.AE-03 | Detect | The evidence shows logging of authentication events and user activity, but it does not explicitly co | Define specific correlation rules within the SIEM that combine authentication logs with other releva |
| DE.AE-04 | Detect | The evidence describes the review and escalation timeline for security alerts, but it does not expli | Update the System and Information Integrity Policy to include specific criteria for assessing the sc |
| DE.AE-06 | Detect | The evidence shows logging and review/escalation processes, but lacks explicit mention of defining r | Integrate the policy to explicitly define roles and notification criteria for adverse event informat |
| DE.CM-03 | Detect | The evidence indicates monitoring for insider threats and general user activity. However, the guidan | Implement User and Entity Behavior Analytics (UEBA) tools to detect anomalous activity and define ba |
| RS.AN-03 | Respond | The evidence confirms that analysis is performed and logging supports forensics. However, the eviden | Implement a formal Root Cause Analysis (RCA) process for all significant incidents. Ensure that the  |
| RS.AN-07 | Respond | The evidence confirms that logs are collected and retained, which supports the foundation of forensi | Update the Cyber Incident Response Standard or Computer Security Threat Response Policy to explicitl |
| RS.MI-01 | Respond | The evidence confirms that containment strategies depend on the incident type, but it does not expli | Develop and document specific containment playbooks for common incident types. Establish clear roles |
| RS.MI-02 | Respond | The evidence confirms that threats must be eradicated after containment, but it does not explicitly  | Define specific, documented eradication procedures for common threat types (e.g., malware removal, a |

## 5. Missing Policy Documents
Out-of-scope subcategories grouped by the policy template needed:

| Missing Policy Template | Count | NIST Subcategories Covered |
|-------------------------|-------|---------------------------|
| Computer Security Threat Response Policy | 25 | DE.AE-08, GV.OC-04, GV.SC-08, ID.IM-02, ID.RA-05, ID.RA-06, ID.RA-08, PR.DS-01, PR.DS-02, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-08, RS.CO-02, RS.CO-03, RS.MA-01, RS.MA-02, RS.MA-03, RS.MA-04, RS.MA-05 |
| Cyber Incident Response Standard | 25 | DE.AE-08, GV.OC-04, GV.SC-08, ID.IM-02, ID.RA-05, ID.RA-06, ID.RA-08, PR.DS-01, PR.DS-02, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-08, RS.CO-02, RS.CO-03, RS.MA-01, RS.MA-02, RS.MA-03, RS.MA-04, RS.MA-05 |
| Incident Response Policy | 25 | DE.AE-08, GV.OC-04, GV.SC-08, ID.IM-02, ID.RA-05, ID.RA-06, ID.RA-08, PR.DS-01, PR.DS-02, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-08, RS.CO-02, RS.CO-03, RS.MA-01, RS.MA-02, RS.MA-03, RS.MA-04, RS.MA-05 |
| Information Security Policy | 24 | DE.AE-08, GV.OC-01, GV.OC-05, GV.OV-01, GV.OV-02, GV.OV-03, GV.RM-01, GV.RM-02, GV.RM-03, GV.RM-04, GV.RM-06, GV.RM-07, GV.RR-03, GV.SC-02, ID.AM-7, ID.RA-03, ID.RA-05, ID.RA-06, ID.RA-08, PR.AA-06, PR.AT-01, PR.AT-02, PR.DS-01, PR.DS-02 |
| Identification and Authentication Policy | 14 | GV.OC-03, GV.RM-05, GV.SC-01, GV.SC-03, GV.SC-04, GV.SC-05, GV.SC-06, GV.SC-07, GV.SC-09, GV.SC-10, ID.RA-10, PR.AA-02, PR.AA-04, PR.AT-02 |
| Security Assessment and Authorization Policy | 12 | GV.OC-03, GV.RM-05, GV.SC-01, GV.SC-03, GV.SC-04, GV.SC-05, GV.SC-06, GV.SC-07, GV.SC-09, GV.SC-10, ID.RA-03, ID.RA-10 |
| Systems and Services Acquisition Policy | 12 | GV.OC-03, GV.RM-05, GV.SC-01, GV.SC-03, GV.SC-04, GV.SC-05, GV.SC-06, GV.SC-07, GV.SC-08, GV.SC-09, GV.SC-10, ID.RA-10 |
| Contingency Planning Policy | 12 | ID.IM-02, RC.CO-03, RC.CO-04, RC.RP-01, RC.RP-02, RC.RP-03, RC.RP-04, RC.RP-05, RC.RP-06, RS.AN-08, RS.CO-02, RS.CO-03 |
| System and Information Integrity Policy | 11 | DE.AE-07, DE.AE-08, DE.CM-02, DE.CM-06, DE.CM-09, ID.RA-01, ID.RA-02, ID.RA-04, ID.RA-09, PR.IR-03, PR.IR-04 |
| Information Security Risk Management Standard | 10 | GV.OV-01, GV.OV-02, GV.OV-03, GV.RM-01, GV.RM-02, GV.RM-03, GV.RM-04, GV.RM-06, GV.RM-07, GV.RR-03 |
| Risk Assessment Policy | 10 | GV.OV-01, GV.OV-02, GV.OV-03, GV.RM-01, GV.RM-02, GV.RM-03, GV.RM-04, GV.RM-06, GV.RM-07, GV.RR-03 |
| Vulnerability Scanning Standard | 8 | DE.AE-07, DE.AE-08, DE.CM-02, DE.CM-06, ID.RA-01, ID.RA-02, ID.RA-03, ID.RA-04 |
| Maintenance Policy | 8 | ID.RA-03, PR.AA-06, PR.DS-01, PR.DS-02, PR.DS-10, PR.DS-11, PR.IR-02, PR.PS-02 |
| Auditing and Accountability Standard | 7 | DE.AE-07, DE.CM-02, DE.CM-06, DE.CM-09, ID.RA-01, ID.RA-02, ID.RA-04 |
| Security Logging Standard | 7 | DE.AE-07, DE.CM-02, DE.CM-06, DE.CM-09, ID.RA-01, ID.RA-02, ID.RA-04 |
| Media Protection Policy | 6 | ID.RA-03, PR.AA-06, PR.DS-01, PR.DS-02, PR.DS-10, PR.DS-11 |
| Mobile Device Security | 5 | ID.RA-03, PR.AA-06, PR.DS-01, PR.DS-02, PR.DS-10 |
| Encryption Standard | 4 | ID.RA-03, PR.AA-06, PR.DS-01, PR.DS-02 |
| Access Control Policy | 4 | PR.AA-02, PR.AA-04, PR.AT-02, PR.PS-03 |
| Configuration Management Policy | 4 | PR.AA-02, PR.AA-04, PR.AT-02, PR.PS-05 |
| Sanitization Secure Disposal Standard | 4 | PR.DS-10, PR.IR-02, PR.PS-03, PR.PS-06 |
| System and Communications Protection Policy | 3 | GV.OC-05, ID.AM-4, PR.AA-06 |
| Acceptable Use of Information Technology Resource Policy | 3 | GV.SC-02, PR.AT-01, PR.AT-02 |
| Security Awareness and Training Policy | 3 | GV.SC-02, PR.AT-01, PR.AT-02 |
| Patch Management Standard | 3 | ID.RA-03, PR.DS-01, PR.DS-02 |
| Account Management/Access Control Standard | 3 | PR.AA-02, PR.AA-04, PR.AT-02 |
| Authentication Tokens Standard | 3 | PR.AA-02, PR.AA-04, PR.AT-02 |
| Secure Configuration Standard | 3 | PR.DS-10, PR.IR-02, PR.PS-05 |
| Secure System Development Life Cycle Standard | 3 | PR.DS-10, PR.IR-02, PR.IR-03 |
| Information Classification Standard | 2 | GV.OC-05, ID.AM-7 |
| Personnel Security Policy | 2 | PR.AT-01, PR.AT-02 |
| Physical and Environmental Protection Policy | 2 | PR.AT-01, PR.AT-02 |
| 802.11 Wireless Network Security Standard | 1 | PR.IR-03 |

## 6. Prioritized Remediation Roadmap

| Priority | Action | Details |
|----------|--------|---------|
| **2 — Short-term (30–90 days)** | Strengthen partially addressed areas | GV.OC-02, GV.PO-01, GV.PO-02, GV.RR-01, GV.RR-02, ID.AM-1, ID.AM-2, ID.AM-3, ID.AM-5, ID.AM-8 |
| **3 — Medium-term (90–180 days)** | Create missing policy documents | 802.11 Wireless Network Security Standard, Acceptable Use of Information Technology Resource Policy, Access Control Policy, Account Management/Access Control Standard, Auditing and Accountability Standard |
