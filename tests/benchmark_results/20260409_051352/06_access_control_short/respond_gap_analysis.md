# Respond Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 13
**In Scope**: 5 | **Out of Scope**: 8
**Addressed**: 1 | **Partially Addressed**: 4 | **Not Addressed**: 0
**Overall Maturity** (in-scope only): Substantially Implemented

---

## In-Scope Subcategory Assessments

### RS.AN-03 — Analysis is performed to establish what has taken place during an incident and the root cause of the incident. Understanding root cause is essential for preventing recurrence.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Audit logging: All authentication events, access grants and revocations, and privileged actions are logged with sufficient detail to support forensic investigation.
Snippet 2: Analysis is performed to establish what has taken place during an incident and the root cause of the incident. Understanding root cause is essential for preventing recurrence.
**Gap**: The evidence confirms that analysis is performed and logging supports forensics. However, the evidence does not explicitly confirm that structured Root Cause Analysis (RCA) techniques are used or that RCA findings are explicitly documented to drive remediation actions, which are key implementation guidance points.
**Recommendation**: Implement a formal Root Cause Analysis (RCA) process for all significant incidents. Ensure that the analysis utilizes structured techniques (e.g., 5 Whys, fishbone diagram). Document the findings in a post-incident report and ensure these findings directly drive remediation actions to prevent recurrence.

### RS.AN-06 — Actions performed during an investigation are recorded, and the records' integrity and provenance are preserved.
**Status**: Addressed
**Evidence from Policy**: Snippet 1: Actions performed during an investigation are recorded, and the records' integrity and provenance are preserved.
Snippet 4: Actions performed during an investigation are recorded, and the records' integrity and provenance are preserved.
**Gap**: None - fully addressed
**Recommendation**: While the policy addresses recording actions and preserving integrity/provenance, consider explicitly documenting required elements like timesstamps, tools used, and maintaining a formal chain of custody for digital evidence to fully align with implementation guidance.

### RS.AN-07 — Incident data and metadata are collected, and their integrity and provenance are preserved.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Authentication events are logged centrally for audit purposes.
Snippet 2: Audit logging: All authentication events, access grants and revocations, and privileged actions are logged with sufficient detail to support forensic investigation. Logs are retained for 12 months minimum and protected from modification.
**Gap**: The evidence confirms that logs are collected and retained, which supports the foundation of forensic analysis. However, the evidence does not explicitly confirm adherence to all implementation guidance, such as: 
- Whether forensic data collection procedures (e.g., write blockers, cryptographic hashing) are documented and followed.
- Whether cryptographic hashing is used to verify the integrity of collected evidence.
- Whether evidence is stored in a secure, access-controlled location with audit logs.
**Recommendation**: Update the Cyber Incident Response Standard or Computer Security Threat Response Policy to explicitly detail the forensic data collection procedures. This should include mandatory steps for using write blockers, applying cryptographic hashing to verify evidence integrity upon collection, and documenting the complete chain of custody for all collected incident data.

### RS.MI-01 — Incident containment strategy and execution
**Status**: Partially Addressed
**Evidence from Policy**: Incidents are contained. Containment stops the spread of the incident and prevents additional damage while analysis and eradication are underway. The appropriate containment strategy depends on the incident type — from network isolation to account suspension to disabling specific services.
**Gap**: The evidence confirms that containment strategies depend on the incident type, but it does not explicitly confirm if 'containment playbooks are defined for common incident types,' or if 'responders have the authority and technical capability to implement containment quickly,' or if 'evidence preservation is considered alongside containment actions.'
**Recommendation**: Develop and document specific containment playbooks for common incident types. Establish clear roles and responsibilities defining the authority of responders to execute containment actions rapidly, and integrate evidence preservation steps into the containment procedures.

### RS.MI-02 — Incident eradication procedures and verification
**Status**: Partially Addressed
**Evidence from Policy**: Incidents are eradicated. After containment, the threat must be completely removed from the environment.
**Gap**: The evidence confirms that threats must be eradicated after containment, but it does not explicitly demonstrate that eradication procedures are defined for common threat types, that eradication is verified through scanning before recovery begins, or that all affected accounts, credentials, and access paths are reviewed during eradication.
**Recommendation**: Define specific, documented eradication procedures for common threat types (e.g., malware removal, account remediation, vulnerability patching, configuration correction). Implement a mandatory verification step, such as post-eradication scanning and monitoring, before proceeding with system recovery. Ensure the process includes a review of all affected accounts, credentials, and access paths during the eradication phase, referencing guidance from the CIS MS-ISAC template for comprehensive incident response planning.

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| RS.AN-08 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RS.CO-02 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RS.CO-03 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RS.MA-01 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy |
| RS.MA-02 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy |
| RS.MA-03 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy |
| RS.MA-04 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy |
| RS.MA-05 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy |

---

## Respond Function — Overall Maturity Assessment
**Rating**: Substantially Implemented
**Justification**: Of 5 in-scope subcategories, 1 fully addressed, 4 partially addressed, 0 not addressed. 8 subcategories are out of scope for this policy.
**Top Priority Gaps**:
1. **RS.AN-03** — The evidence confirms that analysis is performed and logging supports forensics. However, the evidence does not explicit
2. **RS.AN-07** — The evidence confirms that logs are collected and retained, which supports the foundation of forensic analysis. However,
3. **RS.MI-01** — The evidence confirms that containment strategies depend on the incident type, but it does not explicitly confirm if 'co
