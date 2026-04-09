# Govern Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 31
**In Scope**: 6 | **Out of Scope**: 25
**Addressed**: 1 | **Partially Addressed**: 5 | **Not Addressed**: 0
**Overall Maturity** (in-scope only): Partially Implemented

---

## In-Scope Subcategory Assessments

### GV.OC-02 — Internal and external stakeholders are understood, and their needs and expectations regarding cybersecurity risk management are understood and considered. Stakeholders include employees, executives, regulators, customers, vendors, and auditors.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 4: Internal and external stakeholders are understood, and their needs and expectations regarding cybersecurity risk management are understood and considered. Stakeholders include employees, executives, regulators, customers, vendors, and auditors.
**Gap**: The evidence confirms that stakeholders are understood, but it does not explicitly detail the process for conducting a formal stakeholder analysis, mapping specific cybersecurity expectations to policies, or tracking changes in those expectations as suggested by the Implementation Guidance.
**Recommendation**: Conduct a formal stakeholder analysis to identify all internal and external stakeholders (e.g., IT, legal, HR, board) and map their specific cybersecurity requirements to existing policies. Ensure that the 'Identification and Authentication Policy' and 'Security Assessment and Authorization Policy' explicitly address these documented stakeholder requirements.

### GV.PO-01 — Policy for managing cybersecurity risks is established based on organizational context, cybersecurity strategy, and priorities, and is communicated and enforced
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 6: Compliance with this policy is mandatory. Violations including sharing credentials, accessing unauthorized systems, or circumventing access controls will result in disciplinary action up to and including termination.
**Gap**: The evidence shows enforcement mechanisms (disciplinary action) are defined, but it does not explicitly demonstrate that the policy is 'established based on organizational context, cybersecurity strategy, and priorities,' nor does it confirm that policies are 'communicated' or 'assigned policy owners who are accountable for enforcement.'
**Recommendation**: Update the policy documentation to explicitly reference the organization's risk assessment findings and strategic objectives. Clearly define which roles or individuals are accountable for enforcing the policy, as suggested by the Implementation Guidance.

### GV.PO-02 — Policy for managing cybersecurity risks is reviewed, updated, communicated, and enforced to reflect changes in requirements, threats, technology, and organizational mission.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 3: Policy for managing cybersecurity risks is reviewed, updated, communicated, and enforced to reflect changes in requirements, threats, technology, and organizational mission. Outdated policies create false confidence and compliance gaps. Snippet 5: Annual policy review is conducted by the IT Security Manager. The policy is updated when significant changes occur in technology, organizational structure, or threat landscape.
**Gap**: The evidence indicates an annual review and updates based on significant changes (Snippet 5). However, the guidance suggests triggering ad-hoc reviews after significant incidents or regulatory changes, and requires a version control system. There is no explicit mention of reviewing policies after significant incidents or regulatory changes, nor is there any mention of a version control system.
**Recommendation**: Implement a formal policy review cycle that includes scheduled annual reviews (as mentioned in Snippet 5) and trigger ad-hoc reviews following significant incidents or regulatory changes. Establish and maintain a version control system for all policy documents to ensure traceability and manage updates effectively.

### GV.RR-01 — Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving. Leadership must model good cybersecurity behavior and set expectations from the top.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 2: Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving. Leadership must model good cybersecurity behavior and set expectations from the top.
**Gap**: The evidence confirms leadership responsibility but lacks specific implementation guidance mentioned in the Implementation Guidance section of the NIST CSF (e.g., documentation of executive responsibilities or inclusion in performance reviews).
**Recommendation**: Document executive-level cybersecurity responsibilities formally and include cybersecurity culture expectations in leadership performance reviews to fully meet the implementation guidance for GV.RR-01.

### GV.RR-02 — Roles, responsibilities, and authorities related to cybersecurity risk management are established, communicated, understood, and enforced.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: This policy establishes requirements for managing user identities, controlling access to information systems, and protecting organizational resources from unauthorized access.
Snippet 2: User accounts are created through a formal provisioning process requiring manager approval and documented business justification.
Snippet 4: Access rights are assigned based on role-based access control (RBAC). Access roles are defined for each system and mapped to job functions.
Snippet 5: All user access rights are reviewed quarterly by system owners. Accounts with no activity in the past 60 days are flagged for validation or removal.
Snippet 6: Compliance with this policy is mandatory. Violations including sharing credentials, accessing unauthorized systems, or circumventing access controls will result in disciplinary action up to and including termination.
**Gap**: The evidence shows *what* controls are in place (provisioning, RBAC, access reviews) but does not explicitly demonstrate the establishment of a formal RACI matrix, explicit inclusion of cybersecurity roles in job descriptions/onboarding, or communication/reinforcement through annual training as suggested by the Implementation Guidance.
**Recommendation**: Develop and formally document a cybersecurity RACI matrix. Integrate specific cybersecurity responsibilities into all relevant job descriptions and onboarding documentation. Establish an annual training program to communicate roles, responsibilities, and accountability mechanisms.

### GV.RR-04 — Cybersecurity in Human Resources Practices
**Status**: Addressed
**Evidence from Policy**: Snippet 1: Cybersecurity is included in human resources practices. This includes background checks, security training at onboarding, role-based access provisioning, and offboarding procedures that revoke access.
**Gap**: None - fully addressed
**Recommendation**: Ensure documented handoff procedures are established between HR and IT/security teams for managing the employee lifecycle, as suggested by the Implementation Guidance. Also, confirm that employment contracts explicitly include cybersecurity obligations to fully satisfy the Key Questions regarding contractual obligations and process integration across all lifecycle stages (hiring, onboarding, role change, termination).

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| GV.OC-01 | Information Security Policy |
| GV.OC-03 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.OC-04 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy |
| GV.OC-05 | System and Communications Protection Policy, Information Classification Standard, Information Security Policy |
| GV.OV-01 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.OV-02 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.OV-03 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RM-01 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RM-02 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RM-03 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RM-04 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RM-05 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.RM-06 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RM-07 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RR-03 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.SC-01 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-02 | Acceptable Use of Information Technology Resource Policy, Information Security Policy, Security Awareness and Training Policy |
| GV.SC-03 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-04 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-05 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-06 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-07 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-08 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Systems and Services Acquisition Policy |
| GV.SC-09 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-10 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |

---

## Govern Function — Overall Maturity Assessment
**Rating**: Partially Implemented
**Justification**: Of 6 in-scope subcategories, 1 fully addressed, 5 partially addressed, 0 not addressed. 25 subcategories are out of scope for this policy.
**Top Priority Gaps**:
1. **GV.OC-02** — The evidence confirms that stakeholders are understood, but it does not explicitly detail the process for conducting a f
2. **GV.PO-01** — The evidence shows enforcement mechanisms (disciplinary action) are defined, but it does not explicitly demonstrate that
3. **GV.PO-02** — The evidence indicates an annual review and updates based on significant changes (Snippet 5). However, the guidance sugg
