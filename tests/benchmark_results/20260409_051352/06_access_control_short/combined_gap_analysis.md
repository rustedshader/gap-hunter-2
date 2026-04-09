# NIST Cybersecurity Framework Gap Analysis Report

This report provides a comprehensive gap analysis of the organization's policies
against the NIST Cybersecurity Framework 2.0.

================================================================================

## Govern Function Analysis

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


================================================================================

## Identify Function Analysis

# Identify Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 21
**In Scope**: 9 | **Out of Scope**: 12
**Addressed**: 1 | **Partially Addressed**: 8 | **Not Addressed**: 0
**Overall Maturity** (in-scope only): Partially Implemented

---

## In-Scope Subcategory Assessments

### ID.AM-1 — Inventories of hardware managed by the organization are maintained.
**Status**: Partially Addressed
**Evidence from Policy**: Inventories of hardware managed by the organization are maintained. This includes all physical devices: servers, workstations, laptops, network devices, printers, IoT devices, and mobile devices.
**Gap**: The evidence confirms that inventories are maintained, but it does not explicitly confirm the implementation guidance requirements such as using automated discovery tools, integrating with CMDB or ITSM platforms, including asset owner, location, classification, and lifecycle status, nor does it specify the frequency of review and reconciliation.
**Recommendation**: Update the policy to include specific requirements for automated hardware discovery, integration with asset management systems (CMDB/ITSM), and a defined schedule for quarterly inventory review and reconciliation, as suggested by the implementation guidance.

### ID.AM-2 — Inventories of software, services, and systems managed by the organization are maintained.
**Status**: Partially Addressed
**Evidence from Policy**: Inventories of software, services, and systems managed by the organization are maintained. This includes operating systems, applications, SaaS tools, APIs, and cloud services. Software inventory is essential for patch management, license compliance, and identifying unauthorized or vulnerable software.
**Gap**: The evidence confirms that inventories are maintained and mentions their use for patch management and identifying vulnerable software. However, the provided policy snippet does not explicitly detail *how* these inventories are managed (e.g., the required tagging of business owners, versions, and patch status, nor does it explicitly confirm integration with vulnerability management workflows as suggested in the Implementation Guidance.
**Recommendation**: Update the relevant policy section to explicitly include requirements for tagging software inventory entries with business owner, version, and patch status. Furthermore, document the process by which the software inventory is integrated with vulnerability management workflows to fully meet the implementation guidance for this subcategory.

### ID.AM-3 — Representations of authorized network communication and data flows are maintained
**Status**: Partially Addressed
**Evidence from Policy**: Firewall rules restricting traffic to authorized services and ports
Network segmentation separating sensitive systems from general corporate networks
**Gap**: The evidence shows controls (firewall rules, segmentation) but does not explicitly confirm the maintenance of network flow documentation or diagrams as suggested by the implementation guidance.
**Recommendation**: Update the System and Communications Protection Policy to include a requirement for creating and maintaining network diagrams showing all authorized communication paths, and a process for reviewing and updating these documents after significant network changes, referencing CIS MS-ISAC template guidance.

### ID.AM-5 — Assets are prioritized based on classification, criticality, resources, and impact on the mission. Not all assets require the same level of protection. Prioritization ensures that the most critical and sensitive assets receive the strongest controls and the most attention during incidents.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 2: Assets are prioritized based on classification, criticality, resources, and impact on the mission. Not all assets require the same level of protection. Prioritization ensures that the most critical and sensitive assets receive the strongest controls and the most attention during incidents.
**Gap**: The evidence confirms prioritization based on classification, criticality, resources, and impact. However, the provided snippets do not explicitly confirm the existence or consistent application of a documented asset classification scheme or how this classification directly drives control selection as suggested by the Implementation Guidance.
**Recommendation**: Develop and document an Information Classification Standard (as referenced in the Required Policy Templates) that defines the classification levels (e.g., Critical, High, Medium, Low) based on data sensitivity, operational dependency, and regulatory requirements. Ensure this standard is used to drive the selection of appropriate security controls for each asset class.

### ID.AM-8 — Systems, hardware, software, services, and data are managed throughout their life cycles.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 6: Systems, hardware, software, services, and data are managed throughout their life cycles. Assets introduce risk at every stage — acquisition, deployment, operation, change, and disposal. Lifecycle management ensures security controls are maintained at every stage and that outdated or decommissioned assets don't become liabilities.
**Gap**: The evidence confirms lifecycle management is addressed, but it does not explicitly detail the integration of security requirements into asset procurement criteria, a secure disposal process for retired hardware and data, or the removal of decommissioned assets from inventories and access control lists.
**Recommendation**: Update the policy to explicitly include requirements for integrating security controls into the asset acquisition (procurement) process. Furthermore, establish a formal, documented process for the sanitization and secure disposal of all retired hardware and data, referencing the Sanitization/Secure Disposal Standard. Finally, document the procedure for removing decommissioned assets from all relevant inventories and access control lists.

### ID.IM-01 — Improvements are identified from evaluations.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 3: Evaluations — including audits, assessments, penetration tests, and compliance reviews — generate findings that should directly feed into improvement plans.
**Gap**: The evidence shows that findings are generated, but it does not explicitly confirm the existence of a formal process to convert these findings into tracked improvement actions with owners and deadlines, nor does it mention tracking these actions to closure or reporting progress in governance meetings as suggested by the Implementation Guidance.
**Recommendation**: Develop a formal process that mandates the creation of a findings report and a corresponding improvement plan with assigned owners and deadlines for every evaluation. Implement a system to track these improvement actions to closure and establish a mechanism to report on improvement progress in governance meetings.

### ID.IM-03 — Improvements are identified from execution of operational processes, procedures, and activities. Day-to-day operations surface inefficiencies, gaps, and risks that formal assessments may miss. Operational staff should have a channel to report process improvement opportunities.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Operational staff should have a channel to report process improvement opportunities.
Snippet 4: Day-to-day operations surface inefficiencies, gaps, and risks that formal assessments may miss. Operational staff should have a channel to report process improvement opportunities.
**Gap**: The evidence confirms the existence of a channel for reporting improvements (Snippet 1 & 4). However, the evidence does not explicitly confirm if these reported issues are tracked systematically or incorporated into the annual security program review, which is part of the implementation guidance.
**Recommendation**: Develop and document a formal process that captures, tracks, prioritizes, and incorporates operational feedback into the annual security program review, as suggested by the Implementation Guidance for ID.IM-03.

### ID.IM-04 — Incident response plans and other cybersecurity plans are established, communicated, maintained, and improved.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 4: Incident response plans and other cybersecurity plans that affect operations are established, communicated, maintained, and improved.
**Gap**: The evidence confirms that plans are 'established, communicated, maintained, and improved,' but it does not explicitly confirm the required frequency of review (e.g., annually) or the existence of a version control system, which are key aspects of the implementation guidance.
**Recommendation**: Update the policy to explicitly state the frequency for reviewing and updating operational cybersecurity plans (e.g., 'All operational cybersecurity plans shall be reviewed and updated at least annually or after any significant incident or organizational change'). Additionally, document a formal version control system for all relevant plans.

### ID.RA-07 — Changes and exceptions are managed, assessed for risk impact, recorded, and tracked.
**Status**: Addressed
**Evidence from Policy**: Changes and exceptions are managed, assessed for risk impact, recorded, and tracked. Every change to the environment — new systems, configuration changes, software updates, exceptions to policy — carries potential risk. Change management processes ensure risks are assessed before changes are implemented. Exceptions require written approval from the IT Security Manager and must be reviewed every 90 days. All exceptions are logged in the exception register.
**Gap**: None - fully addressed
**Recommendation**: None - fully addressed

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| ID.AM-4 | System and Communications Protection Policy |
| ID.AM-7 | Information Classification Standard, Information Security Policy |
| ID.IM-02 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| ID.RA-01 | Auditing and Accountability Standard, Security Logging Standard, System and Information Integrity Policy, Vulnerability Scanning Standard |
| ID.RA-02 | Auditing and Accountability Standard, Security Logging Standard, System and Information Integrity Policy, Vulnerability Scanning Standard |
| ID.RA-03 | Encryption Standard, Information Security Policy, Maintenance Policy, Media Protection Policy, Mobile Device Security, Security Assessment and Authorization Policy, Vulnerability Scanning Standard, Patch Management Standard |
| ID.RA-04 | Auditing and Accountability Standard, Security Logging Standard, System and Information Integrity Policy, Vulnerability Scanning Standard |
| ID.RA-05 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Information Security Policy |
| ID.RA-06 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Information Security Policy |
| ID.RA-08 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Information Security Policy |
| ID.RA-09 | System and Information Integrity Policy |
| ID.RA-10 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |

---

## Identify Function — Overall Maturity Assessment
**Rating**: Partially Implemented
**Justification**: Of 9 in-scope subcategories, 1 fully addressed, 8 partially addressed, 0 not addressed. 12 subcategories are out of scope for this policy.
**Top Priority Gaps**:
1. **ID.AM-1** — The evidence confirms that inventories are maintained, but it does not explicitly confirm the implementation guidance re
2. **ID.AM-2** — The evidence confirms that inventories are maintained and mentions their use for patch management and identifying vulner
3. **ID.AM-3** — The evidence shows controls (firewall rules, segmentation) but does not explicitly confirm the maintenance of network fl


================================================================================

## Protect Function Analysis

# Protect Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 22
**In Scope**: 6 | **Out of Scope**: 16
**Addressed**: 4 | **Partially Addressed**: 2 | **Not Addressed**: 0
**Overall Maturity** (in-scope only): Substantially Implemented

---

## In-Scope Subcategory Assessments

### PR.AA-01 — Identities and credentials for authorized users, services, and hardware are managed by the organization. This includes the full lifecycle of identities: creation, modification, review, and deletion. Unmanaged credentials — stale accounts, shared passwords, default credentials — are among the most exploited vulnerabilities.
**Status**: Addressed
**Evidence from Policy**: Snippet 2: All users must have a unique individual account. Shared accounts are prohibited. User accounts are created through a formal provisioning process requiring manager approval and documented business justification.
Snippet 5: All user access rights are reviewed quarterly by system owners. Accounts with no activity in the past 60 days are flagged for validation or removal.
**Gap**: None - fully addressed
**Recommendation**: Implement an Identity Governance and Administration (IGA) tool or process to automate account deprovisioning upon employee departure, as suggested by the implementation guidance.

### PR.AA-03 — Users, services, and hardware are authenticated. Authentication verifies that the entity requesting access is who or what it claims to be. Strong authentication — particularly multi-factor authentication (MFA) — dramatically reduces the risk of unauthorized access through compromised credentials.
**Status**: Addressed
**Evidence from Policy**: Snippet 2: Multi-factor authentication (MFA) is mandatory for: All remote access to organizational systems Access to systems containing sensitive or confidential data All administrative and privileged accounts Cloud platform consoles and management interfaces
Snippet 5: Users, services, and hardware are authenticated. Authentication verifies that the entity requesting access is who or what it claims to be. Strong authentication — particularly multi-factor authentication (MFA) — dramatically reduces the risk of unauthorized access through compromised credentials
**Gap**: None - fully addressed
**Recommendation**: The policy explicitly mandates MFA for remote access, administrative/privileged accounts, and access to sensitive data systems. This aligns with the implementation guidance to require MFA for these high-risk paths.

### PR.AA-05 — Access permissions, entitlements, and authorizations are defined in a policy, managed, enforced, and reviewed, and incorporate the principles of least privilege and separation of duties
**Status**: Addressed
**Evidence from Policy**: Snippet 1: Access to systems is granted based on the principle of least privilege. Users receive only the minimum access required to perform their job duties.
Snippet 4: Access rights are assigned based on role-based access control (RBAC). Users are assigned to roles, not granted individual permissions where avoidable.
Snippet 5: Quarterly access reviews: All user access rights are reviewed quarterly by system owners. Accounts with no activity in the past 60 days are flagged for validation or removal.
**Gap**: None - fully addressed
**Recommendation**: The policy effectively addresses least privilege (Snippet 1) and role-based access control (RBAC) (Snippet 4). Quarterly reviews are also in place (Snippet 5). To fully address the 'separation of duties' aspect mentioned in the requirement, the policy should explicitly define and enforce separation of duties controls for critical functions, as suggested by the Implementation Guidance.

### PR.IR-01 — Networks and environments are protected from unauthorized logical access and usage. Network segmentation, remote access controls, and wireless security prevent attackers from moving laterally through the environment or accessing sensitive systems from unauthorized locations.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 3: Network segmentation separating sensitive systems from general corporate networks
Snippet 2: Multi-factor authentication (MFA) is mandatory for: All remote access to organizational systems
Snippet 4: User activity on systems containing sensitive data is logged and monitored for: Unauthorized access attempts and repeated authentication failures
**Gap**: The evidence confirms segmentation, MFA for remote access, and monitoring for unauthorized access attempts. However, the evidence does not explicitly confirm the implementation of Network Access Control (NAC) to prevent unauthorized device connections, which is mentioned in the Implementation Guidance.
**Recommendation**: Update the policy or related standards to explicitly include a requirement for implementing Network Access Control (NAC) to prevent unauthorized device connections, as suggested by the Implementation Guidance.

### PR.PS-01 — Configuration management practices are established and applied. Secure baseline configurations reduce the attack surface of every system. Unmanaged configurations drift over time, introducing vulnerabilities. A robust configuration management program ensures systems are deployed securely and remain secure over time.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 3: Configuration management practices are established and applied. Secure baseline configurations reduce the attack surface of every system. Unmanaged configurations drift over time, introducing vulnerabilities. A robust configuration management program ensures systems are deployed securely and remain secure over time. Snippet 5: Configuration management practices are established and applied. Secure baseline configurations reduce the attack surface of every system. Unmanaged configurations drift over time, introducing vulnerabilities. A robust configuration management program ensures systems are deployed securely and remain secure over time.
**Gap**: The evidence confirms that configuration management practices are established and that secure baseline configurations are used, which addresses parts of the requirement. However, the evidence does not explicitly confirm the use of industry benchmarks (like CIS Benchmarks) or the enforcement/monitoring mechanisms mentioned in the Implementation Guidance (e.g., Group Policy, MDM, or infrastructure-as-code).
**Recommendation**: Update the Configuration Management Policy to explicitly state that secure baseline configurations are developed using industry benchmarks (e.g., CIS Benchmarks) and detail the specific tools and processes used for enforcement and monitoring of configuration drift.

### PR.PS-04 — Log records are generated and made available for continuous monitoring.
**Status**: Addressed
**Evidence from Policy**: Snippet 1: Authentication events are logged centrally for audit purposes.
Snippet 2: Audit logging: All authentication events, access grants and revocations, and privileged actions are logged with sufficient detail to support forensic investigation. Logs are retained for 12 months minimum and protected from modification.
**Gap**: None - fully addressed
**Recommendation**: The policy adequately addresses the requirements by stating that authentication events are logged centrally and that logs include sufficient detail for forensic investigation, along with a defined retention period (12 months). No further action is immediately required based on this evidence. (Referencing CIS MS-ISAC template guidance: Ensure log sources are comprehensive and centralized.)

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| PR.AA-02 | Access Control Policy, Account Management/Access Control Standard, Authentication Tokens Standard, Configuration Management Policy, Identification and Authentication Policy |
| PR.AA-04 | Access Control Policy, Account Management/Access Control Standard, Authentication Tokens Standard, Configuration Management Policy, Identification and Authentication Policy |
| PR.AA-06 | Encryption Standard, Information Security Policy, Maintenance Policy, Media Protection Policy, Mobile Device Security, System and Communications Protection Policy |
| PR.AT-01 | Information Security Policy, Personnel Security Policy, Physical and Environmental Protection Policy, Security Awareness and Training Policy, Acceptable Use of Information Technology Resource Policy |
| PR.AT-02 | Information Security Policy, Personnel Security Policy, Physical and Environmental Protection Policy, Security Awareness and Training Policy, Access Control Policy, Account Management/Access Control Standard, Authentication Tokens Standard, Configuration Management Policy, Identification and Authentication Policy, Acceptable Use of Information Technology Resource Policy |
| PR.DS-01 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Encryption Standard, Incident Response Policy, Information Security Policy, Maintenance Policy, Media Protection Policy, Mobile Device Security, Patch Management Standard |
| PR.DS-02 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Encryption Standard, Incident Response Policy, Information Security Policy, Maintenance Policy, Media Protection Policy, Mobile Device Security, Patch Management Standard |
| PR.DS-10 | Sanitization Secure Disposal Standard, Secure Configuration Standard, Secure System Development Life Cycle Standard, Maintenance Policy, Media Protection Policy, Mobile Device Security |
| PR.DS-11 | Maintenance Policy, Media Protection Policy |
| PR.IR-02 | Secure Configuration Standard, Secure System Development Life Cycle Standard, Sanitization Secure Disposal Standard, Maintenance Policy |
| PR.IR-03 | Secure System Development Life Cycle Standard, System and Information Integrity Policy, 802.11 Wireless Network Security Standard |
| PR.IR-04 | System and Information Integrity Policy |
| PR.PS-02 | Maintenance Policy |
| PR.PS-03 | Sanitization Secure Disposal Standard, Access Control Policy |
| PR.PS-05 | Configuration Management Policy, Secure Configuration Standard |
| PR.PS-06 | Sanitization Secure Disposal Standard |

---

## Protect Function — Overall Maturity Assessment
**Rating**: Substantially Implemented
**Justification**: Of 6 in-scope subcategories, 4 fully addressed, 2 partially addressed, 0 not addressed. 16 subcategories are out of scope for this policy.
**Top Priority Gaps**:
1. **PR.IR-01** — The evidence confirms segmentation, MFA for remote access, and monitoring for unauthorized access attempts. However, the
2. **PR.PS-01** — The evidence confirms that configuration management practices are established and that secure baseline configurations ar


================================================================================

## Detect Function Analysis

# Detect Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 11
**In Scope**: 6 | **Out of Scope**: 5
**Addressed**: 1 | **Partially Addressed**: 5 | **Not Addressed**: 0
**Overall Maturity** (in-scope only): Partially Implemented

---

## In-Scope Subcategory Assessments

### DE.AE-02 — Potentially adverse events are analyzed to better understand associated activities.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 3: Security events — alerts, log entries, anomalies — must be investigated to determine what happened, what systems were affected, and whether the event is benign or malicious. Without analysis, organizations cannot distinguish noise from signal.
**Gap**: The evidence confirms that security events are investigated, but it does not explicitly confirm the implementation of a SIEM/log analysis platform, the definition of analysis playbooks, or the tracking of Mean Time To Analyze (MTTA).
**Recommendation**: Implement a Security Information and Event Management (SIEM) or equivalent log analysis platform to aggregate and correlate events. Define analysis playbooks for common event types. Track mean time to analyze (MTTA) as a performance metric, as suggested by the Implementation Guidance for this subcategory.

### DE.AE-03 — Information is correlated from multiple sources.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Authentication events are logged centrally for audit purposes.
Snippet 2: User activity on systems containing sensitive data is logged and monitored for: Unauthorized access attempts and repeated authentication failures Access to data outside normal job scope Bulk data downloads or exports Access outside normal business hours
**Gap**: The evidence shows logging of authentication events and user activity, but it does not explicitly confirm that these logs are being correlated from *multiple* sources (e.g., network logs, endpoint telemetry, threat intelligence) as required by the guidance.
**Recommendation**: Define specific correlation rules within the SIEM that combine authentication logs with other relevant data sources (such as network flow data or endpoint telemetry) to detect complex attack patterns. Regularly tune these correlation rules to minimize false positives and ensure they effectively identify sophisticated threats.

### DE.AE-04 — Estimated impact and scope of adverse events are understood.
**Status**: Partially Addressed
**Evidence from Policy**: Security alerts from access monitoring are reviewed within 4 hours during business hours and escalated on-call after hours.
**Gap**: The evidence describes the review and escalation timeline for security alerts, but it does not explicitly state that analysts 'quickly assess how widespread it is and what the potential business impact could be' or that 'impact assessment is a required step in all investigation playbooks'.
**Recommendation**: Update the System and Information Integrity Policy to include specific criteria for assessing the scope and impact of adverse events. Develop and document a mandatory impact assessment step within all incident investigation playbooks, linking these assessments to defined escalation thresholds.

### DE.AE-06 — Information on adverse events is provided to authorized staff and tools. Timely distribution of event information to the right people and systems enables faster response. Analysts, incident responders, system owners, and automated response tools must all receive relevant event data when it is needed.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Authentication events are logged centrally for audit purposes.
Snippet 2: Security alerts from access monitoring are reviewed within 4 hours during business hours and escalated on-call after hours.
Snippet 3: Information on adverse events is provided to authorized staff and tools. Timely distribution of event information to the right people and systems enables faster response. Analysts, incident responders, system owners, and automated response tools must all receive relevant event data when it is needed.
**Gap**: The evidence shows logging and review/escalation processes, but lacks explicit mention of defining roles and notification criteria for adverse event information, integrating SIEM alerts with ticketing/incident management, or implementing automated notifications for high-severity events.
**Recommendation**: Integrate the policy to explicitly define roles and notification criteria for adverse event information. Integrate Security Information and Event Management (SIEM) alerts with existing ticketing and incident management tools. Implement automated notifications specifically for high-severity events to ensure timely distribution to all required parties.

### DE.CM-01 — Network monitoring detects unusual traffic patterns, unauthorized connections, data exfiltration, and lateral movement.
**Status**: Addressed
**Evidence from Policy**: Snippet 4: Network monitoring detects unusual traffic patterns, unauthorized connections, data exfiltration, and lateral movement.
**Gap**: None - fully addressed
**Recommendation**: Review the implementation guidance for DE.CM-01 to ensure that specific tools like IDS/IPS or NDR are deployed across key network segments, and that monitoring covers DNS, NetFlow, and proxy logs, as these are mentioned in the guidance but not explicitly detailed in the provided evidence snippets.

### DE.CM-03 — Personnel activity and technology usage are monitored to find potentially adverse events. Insider threats — whether malicious or accidental — can cause significant harm. Monitoring user activity on sensitive systems, detecting unusual access patterns, and flagging policy violations helps identify and respond to insider threats.
**Status**: Partially Addressed
**Evidence from Policy**: Monitoring user activity on sensitive systems, detecting unusual access patterns, and flagging policy violations helps identify and respond to insider threats.
**Gap**: The evidence indicates monitoring for insider threats and general user activity. However, the guidance suggests implementing User and Entity Behavior Analytics (UEBA) and defining baselines for normal user behavior, which is not explicitly confirmed in the snippets.
**Recommendation**: Implement User and Entity Behavior Analytics (UEBA) tools to detect anomalous activity and define baselines for normal user behavior. Ensure monitoring of privileged user activity includes enhanced logging as suggested by the implementation guidance.

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| DE.AE-07 | Auditing and Accountability Standard, Security Logging Standard, System and Information Integrity Policy, Vulnerability Scanning Standard |
| DE.AE-08 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Information Security Policy, System and Information Integrity Policy, Vulnerability Scanning Standard |
| DE.CM-02 | Auditing and Accountability Standard, Security Logging Standard, System and Information Integrity Policy, Vulnerability Scanning Standard |
| DE.CM-06 | Auditing and Accountability Standard, Security Logging Standard, System and Information Integrity Policy, Vulnerability Scanning Standard |
| DE.CM-09 | Auditing and Accountability Standard, Security Logging Standard, System and Information Integrity Policy |

---

## Detect Function — Overall Maturity Assessment
**Rating**: Partially Implemented
**Justification**: Of 6 in-scope subcategories, 1 fully addressed, 5 partially addressed, 0 not addressed. 5 subcategories are out of scope for this policy.
**Top Priority Gaps**:
1. **DE.AE-02** — The evidence confirms that security events are investigated, but it does not explicitly confirm the implementation of a 
2. **DE.AE-03** — The evidence shows logging of authentication events and user activity, but it does not explicitly confirm that these log
3. **DE.AE-04** — The evidence describes the review and escalation timeline for security alerts, but it does not explicitly state that ana


================================================================================

## Respond Function Analysis

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


================================================================================

## Recover Function Analysis

# Recover Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 8
**In Scope**: 0 | **Out of Scope**: 8
**Addressed**: 0 | **Partially Addressed**: 0 | **Not Addressed**: 0
**Overall Maturity** (in-scope only): N/A — No subcategories in scope for this policy type

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| RC.RP-01 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RC.RP-02 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RC.RP-03 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RC.RP-04 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RC.RP-05 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RC.RP-06 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Contingency Planning Policy |
| RC.CO-03 | Computer Security Threat Response Policy, Contingency Planning Policy, Cyber Incident Response Standard, Incident Response Policy |
| RC.CO-04 | Computer Security Threat Response Policy, Contingency Planning Policy, Cyber Incident Response Standard, Incident Response Policy |

---

## Recover Function — Overall Maturity Assessment
**Rating**: N/A — No subcategories in scope for this policy type
**Justification**: Of 0 in-scope subcategories, 0 fully addressed, 0 partially addressed, 0 not addressed. 8 subcategories are out of scope for this policy.


================================================================================
