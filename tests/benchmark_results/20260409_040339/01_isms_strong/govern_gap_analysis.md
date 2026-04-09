# Govern Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 31
**In Scope**: 17 | **Out of Scope**: 14
**Addressed**: 5 | **Partially Addressed**: 12 | **Not Addressed**: 0
**Overall Maturity** (in-scope only): Substantially Implemented

---

## In-Scope Subcategory Assessments

### GV.OC-01 — Organizational mission is understood and informs cybersecurity risk management.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Cybersecurity decisions are made with explicit awareness of this mission and what would cause the most harm if disrupted.
Snippet 2: Our cybersecurity program must align with our mission to deliver trusted technology solutions.
Snippet 7: Mission-driven cybersecurity ensures resources are allocated to protect what truly matters.
**Gap**: The evidence shows alignment between the mission and cybersecurity efforts, but it does not explicitly show that the organizational mission statement is documented and accessible to the security team, nor does it explicitly show that leadership reviews the alignment annually as suggested by the Implementation Guidance.
**Recommendation**: Document the organization's mission statement. Map critical assets and processes to that mission. Ensure the Information Security Policy references the mission explicitly and is reviewed when the mission changes.

### GV.OC-02 — Internal and external stakeholders are understood, and their needs and expectations regarding cybersecurity risk management are understood and considered. Stakeholders include employees, executives, regulators, customers, vendors, and auditors.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 2: The organization has identified the following key stakeholders with cybersecurity risk expectations: - Internal: Board of Directors, Executive Leadership (CEO, CTO, CISO), IT Operations, Legal/Compliance, HR, Software Development teams - External: Enterprise clients, regulatory bodies (SOC 2 auditors, state regulators), insurance underwriters, and third-party auditors
Snippet 3: Stakeholders include employees, executives, regulators, customers, vendors, and auditors
Snippet 9: Stakeholders include employees, executives, regulators, customers, vendors, and auditors
**Gap**: The evidence identifies stakeholders but does not explicitly detail how their specific cyberssecurity requirements are documented or mapped to policies. The guidance suggests mapping expectations and tracking changes.
**Recommendation**: Conduct a formal stakeholder analysis to map the identified internal (Board of Directors, Executive Leadership, IT Operations, Legal/Compliance, HR, Software Development teams) and external stakeholders' specific cybersecurity expectations and ensure corresponding policies address these needs. Review the Identification and Authentication Policy to confirm it addresses the authentication requirements for all identified user groups.

### GV.OC-03 — Legal, regulatory, and contractual requirements regarding cybersecurity — including privacy and civil liberties obligations — are understood and managed.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 2: The organization maintains a Legal and Regulatory Requirements Register that tracks applicable cybersecurity laws and regulations, including: State data breach notification laws... Contractual cybersecuity obligations in client Master Service Agreements (MSAs)
**Gap**: Implementation Guidance suggests assigning ownership for each requirement and reviewing the register annually and after new legislation or contract signing. The evidence confirms the existence of a register but does not explicitly confirm assignment of ownership or the annual review process.
**Recommendation**: Assign clear ownership for each entry in the Legal and Regulatory Requirements Register. Establish an annual review cadence for this register, specifically to incorporate updates from new legislation or newly signed contracts, as recommended by the Implementation Guidance.

### GV.OC-04 — Critical objectives, capabilities, and services that stakeholders depend on or expect from the organization are understood and communicated.
**Status**: Addressed
**Evidence from Policy**: Snippet 2: Critical Services Identification: The organization has identified the following critical services that stakeholders depend upon: Client data analytics platform (Tier 1 — zero tolerance for unplanned downtime)... Snippet 3: 3. Ensure 99.9% availability of Tier 1 critical services
**Gap**: None - fully addressed
**Recommendation**: Ensure the Cyber Incident Response Policy explicitly details the prioritization of recovery for Tier 1 critical services, as suggested by the Implementation Guidance.

### GV.OC-05 — Outcomes of activities and the current cybersecurity risk posture are used to inform the types of risk management approaches applied and modified at all levels of the organization.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Outcomes from security assessments, penetration tests, vulnerability scans, and incident post-mortems are used to inform risk management strategy.
Snippet 2: Outcomes of activities and the current cybersecurity risk posture are used to inform the types of risk management approaches applied and modified at all levels of the organization.
Snippet 5: Key risk indicators (KRIs) and their trends
Status of remediation plans for identified vulnerabilities
Results of security assessments and audits
Incident summary and lessons learned
**Gap**: The evidence shows that outcomes inform risk management strategy and approaches, but it does not explicitly confirm the frequency or mechanism for presenting risk posture summaries to senior leadership as suggested in the Implementation Guidance.
**Recommendation**: Establish a formal, documented process for reporting cybersecurity risk posture summaries (including KRIs, assessment results, and incident lessons learned) to senior leadership on a regular cadence (e.g., quarterly), as recommended by the Implementation Guidance.

### GV.RM-01 — Risk management objectives are established and agreed to by organizational stakeholders.
**Status**: Addressed
**Evidence from Policy**: Snippet 3: The organization's risk management objectives, formally approved by the Executive Leadership Team, are: 1. Reduce the likelihood of a material data breach affecting client data by 30% year-over-year
2. Maintain regulatory compliance across all applicable frameworks
3. Ensure 99.9% availability of Tier 1 critical services
Snippet 4: The Board of Directors is ultimately accountable for the organization's cybersecurity risk posture.
Snippet 5: All information security policies are derived from the organization's risk assessment findings and strategic security objectives.
**Gap**: None - fully addressed
**Recommendation**: The policy clearly documents specific, measurable risk management objectives (reducing breach likelihood by 30%, maintaining compliance, ensuring 99.9% availability). To fully align with implementation guidance, ensure a formal cross-functional workshop is documented where all major stakeholders (including Executive Leadership Team and Board of Directors) formally agree on these objectives and the prioritization derived from them. Ensure a schedule for annual review and update of these objectives is established within the Risk Management Standard or Information Security Policy.

### GV.RM-02 — Risk appetite and risk tolerance statements are established, communicated, and maintained.
**Status**: Partially Addressed
**Evidence from Policy**: Acme Technologies Inc. has formally established risk appetite statements approved by the Board of Directors; Risks are prioritized based on their risk score and alignment with organizational risk appetite.
**Gap**: The evidence confirms that risk appetite statements are established, but it does not explicitly confirm that these statements are 'communicated' to risk owners or 'maintained' according to the implementation guidance (e.g., categorization by risk type, review after major changes).
**Recommendation**: Update the Information Security Risk Management Standard to include a section detailing how risk appetite and tolerance statements are communicated to risk owners and the schedule for their periodic review, as suggested by the Implementation Guidance.

### GV.RM-03 — Cybersecurity risk management activities and outcomes are included in enterprise risk management (ERM) processes. Cybersecurity should not operate in a silo — it must feed into and receive input from the broader ERM program. This enables holistic risk visibility and informed resource allocation.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 3: Cybersecurity risk is integrated into the Enterprise Risk Management (ERM) program. The CISO participates in quarterly ERM governance meetings and the enterprise risk register includes cybersecurity risk items.
**Gap**: The evidence shows that cybersecurity risk items are in the enterprise risk register and the CISO attends ERM governance meetings. However, the guidance suggests aligning reporting cycles and ensuring risks are escalated through ERM channels when appropriate, which is not explicitly detailed as fully addressed.
**Recommendation**: Align cybersecurity risk reporting cycles with ERM reporting cycles. Ensure the CISO or security lead has a seat at ERM governance meetings to ensure holistic visibility and informed resource allocation.

### GV.RM-04 — Strategic direction that describes appropriate risk response options is established and communicated.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 3: The organization employs four risk response strategies: Mitigate, Transfer, Accept, Avoid
Snippet 5: For each identified risk, a risk treatment plan is developed specifying the selected response (mitigate, transfer, accept, avoid), responsible owner, implementation timeline, and success criteria.
**Gap**: The evidence shows that the organization *employs* the four strategies and *develops* treatment plans for identified risks. However, the requirement specifically asks to 'define and communicate its preferred approaches to handling identified risks' and to 'Include decision trees or criteria for choosing a response type.'
**Recommendation**: Develop a formal document (e.g., an Information Security Risk Management Standard) that explicitly defines and communicates the organization's *preferred* risk response strategies for different risk categories, including decision trees or criteria for selecting a response type. Train risk owners on how to apply these defined strategies.

### GV.RM-06 — A standardized method for calculating, documenting, categorizing, and prioritizing cybersecurity risks is established and communicated.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 2: The organization uses a semi-quantitative risk scoring methodology based on likelihood (1–5) × impact (1–5) = risk score (1–25). Snippet 3: All information security policies are derived from the organization's risk assessment findings and strategic security objectives. Snippet 5: Risks are prioritized based on their risk score and alignment with organizational risk appetite.
**Gap**: The evidence shows a specific semi-quantitative methodology is used (Snippet 2), but it does not explicitly confirm that this method is 'standardized,' 'documented in the Risk Assessment Policy,' or that 'all risk assessors are trained on the method' as required by the Implementation Guidance.
**Recommendation**: Update the Risk Assessment Policy to formally document the semi-quantitative risk scoring methodology (likelihood x impact) and include a section detailing the training requirements for all personnel who perform risk assessments. Ensure the risk register format is consistent organization-wide.

### GV.RR-01 — Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving. Leadership must model good cybersecurity behavior and set expectations from the top.
**Status**: Addressed
**Evidence from Policy**: Snippet 2: Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving. Leadership must model good cybersecurity behavior and set expectations from the top.
Snippet 8: Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving. Leadership must model good cybersecurity behavior and set expectations from the top.
**Gap**: None - fully addressed
**Recommendation**: Document executive-level cybersecurity responsibilities formally, as suggested by Implementation Guidance. Ensure cyberssecurity culture expectations are included in leadership performance reviews to meet all implementation guidance requirements.

### GV.RR-02 — Roles, responsibilities, and authorities related to cybersecurity risk management are established, communicated, understood, and enforced.
**Status**: Addressed
**Evidence from Policy**: Snippet 4: A comprehensive RACI (Responsible, Accountable, Consulted, Informed) matrix is maintained and documents cybersecurity responsibilities for all roles. Snippet 5: Policy owners are assigned for each policy and are accountable for enforcement and annual review. Enforcement mechanisms include: Policy attestation required annually from all staff; Non-compliance investigated by HR with potential disciplinary action. Snippet 10: Compliance with this ISMS Policy is mandatory for all in-scope personnel. Snippet 2: Each regulatory requirement is assigned an owner responsible for ongoing compliance tracking.
**Gap**: None - fully addressed
**Recommendation**: Ensure that the cyberssecurity responsibilities documented in the RACI matrix are explicitly included in job descriptions and onboarding processes, as suggested by the Implementation Guidance.

### GV.RR-03 — Adequate resources are allocated commensurate with the cybersecurity risk strategy, roles, responsibilities, and policies.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 2: Adequate resources are allocated commensurate with the cybersecurity risk strategy, roles, responsibilities, and policies. Without sufficient budget, staffing, and tooling, even the best policies cannot be executed.
Snippet 4: The cybersecurity budget is formally tied to identified risks and documented in the annual budget request. Resource gap analysis is presented to leadership annually.
**Gap**: The guidance suggests documenting resource requirements for each cybersecurity role and control, tracking resource allocation vs. plan throughout the year, and ensuring staffing levels are adequate for defined responsibilities.
**Recommendation**: Document specific resource requirements for each cybersecurity role and control. Establish a formal process to track resource allocation against the plan throughout the year, as suggested by the Implementation Guidance.

### GV.SC-02 — Cybersecurity roles and responsibilities for suppliers, customers, and partners are established, communicated, and coordinated internally and externally. All parties in the supply chain must understand their cybersecurity obligations.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: The policy applies to all employees, contractors, consultants, and third parties who access, process, or manage organizational information systems.
Snippet 2: Stakeholder cybersecurity requirements are documented in the Stakeholder Expectations Register, reviewed semi-annually, and updated following organizational changes or regulatory developments.
**Gap**: The evidence indicates that while the policy applies to third parties (Snippet 1) and stakeholder requirements are documented (Snippet 2), there is no direct evidence provided that these responsibilities are explicitly defined in vendor/partner contracts, internal owners are assigned for each relationship, or that vendors know how to report incidents.
**Recommendation**: Define specific cybersecurity responsibilities within all vendor and partner contracts. Assign an internal owner for each significant third-party relationship. Include clear third-party cybersecurity requirements in onboarding materials.

### GV.SC-03 — Cybersecurity supply chain risk management is integrated into cybersecurity and enterprise risk management, risk assessment, and improvement processes.
**Status**: Addressed
**Evidence from Policy**: Snippet 2: Cybersecurity supply chain risk management is integrated into cybersecurity and enterprise risk management, risk assessment, and improvement processes. Third-party risks must appear in the enterprise risk register and be assessed using the same standards as internal risks. Integration prevents blind spots.
Snippet 6: Cybersecurity supply chain risk management is integrated into cybersecurity and enterprise risk management, risk assessment, and improvement processes. Third-party risks must appear in the enterprise risk register and be assessed using the same standards as internal risks. Integration prevents blind spots.
**Gap**: None - fully addressed
**Recommendation**: None - fully addressed

### GV.SC-05 — Requirements to address cybersecurity risks in supply chains are established, prioritized, and integrated into contracts and other types of agreements with suppliers and other relevant third parties.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Requirements to address cybersecurity risks in supply chains are established, prioritized, and integrated into contracts and other types of agreements with suppliers and other relevant third parties. Contractual cybersecurity requirements are one of the most effective mechanisms for managing third-party risk — they create legally enforceable obligations.
**Gap**: The evidence confirms that requirements are established and integrated into contracts. However, it does not explicitly confirm that these contractual requirements include specific elements like breach notification timelines or a right-to-audit clause, which are suggested by the Implementation Guidance.
**Recommendation**: Develop a formal review process to ensure all new vendor contracts include standard cybersecurity clauses such as defined breach notification timelines and a right-to-audit clause for high-criticality suppliers, as recommended in the Implementation Guidance.

### GV.SC-07 — Risks posed by suppliers, products, and services are understood, recorded, prioritized, assessed, responded to, and monitored over the course of the relationship.
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: The risks posed by a supplier, their products and services, and other third parties are understood, recorded, prioritized, assessed, responded to, and monitored over the course of the relationship.
**Gap**: The evidence shows that the process is understood, but it does not explicitly detail the required periodic reassessment cycles for suppliers (e.g., annually for critical), nor does it explicitly detail a process to respond when a supplier's security posture deteriorates, as suggested by the Implementation Guidance.
**Recommendation**: Update the policy or supporting procedures to explicitly define and mandate periodic reassessment cycles for all suppliers based on their criticality. Furthermore, document the specific response procedures for when a supplier's security posture deteriorates, ensuring this aligns with the risk treatment planning process mentioned in Snippet 4.

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| GV.OV-01 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.OV-02 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.OV-03 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.PO-01 | Personnel Security Policy, Physical and Environmental Protection Policy, Security Awareness and Training Policy |
| GV.PO-02 | Personnel Security Policy, Physical and Environmental Protection Policy, Security Awareness and Training Policy |
| GV.RM-05 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.RM-07 | Information Security Policy, Information Security Risk Management Standard, Risk Assessment Policy |
| GV.RR-04 | Information Security Policy, Personnel Security Policy, Physical and Environmental Protection Policy, Security Awareness and Training Policy |
| GV.SC-01 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-04 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-06 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-08 | Computer Security Threat Response Policy, Cyber Incident Response Standard, Incident Response Policy, Systems and Services Acquisition Policy |
| GV.SC-09 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |
| GV.SC-10 | Identification and Authentication Policy, Security Assessment and Authorization Policy, Systems and Services Acquisition Policy |

---

## Govern Function — Overall Maturity Assessment
**Rating**: Substantially Implemented
**Justification**: Of 17 in-scope subcategories, 5 fully addressed, 12 partially addressed, 0 not addressed. 14 subcategories are out of scope for this policy.
**Top Priority Gaps**:
1. **GV.OC-01** — The evidence shows alignment between the mission and cybersecurity efforts, but it does not explicitly show that the org
2. **GV.OC-02** — The evidence identifies stakeholders but does not explicitly detail how their specific cyberssecurity requirements are d
3. **GV.OC-03** — Implementation Guidance suggests assigning ownership for each requirement and reviewing the register annually and after 
