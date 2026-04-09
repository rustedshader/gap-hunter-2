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
