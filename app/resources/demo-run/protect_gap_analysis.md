# Protect Function — Gap Analysis Report
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

**Total Subcategories**: 22
**In Scope**: 2 | **Out of Scope**: 20
**Addressed**: 0 | **Partially Addressed**: 1 | **Not Addressed**: 1
**Overall Maturity** (in-scope only): Partially Implemented

---

## In-Scope Subcategory Assessments

### PR.DS-01 — Protect: Data Security
**Status**: Partially Addressed
**Evidence from Policy**: Snippet 1: Data at rest — stored on disks, databases, backups, and removable media — must be protected against unauthorized access, tampering, and loss. Encryption is the primary control for protecting data at rest.
Snippet 2: Databases containing customer information should be encrypted.
**Gap**: The policy establishes the need for data at rest protection and identifies encryption as the primary control (Snippet 1), and specifically mandates encryption for databases containing customer information (Snippet 2). However, the evidence does not confirm that *all* storage locations (disks, backups, removable media, cloud storage, etc.) are encrypted, nor does it address the management and security of encryption keys, which are key questions for this subcategory.
**Recommendation**: The policy needs to be expanded to explicitly mandate encryption for all specified data-at-rest locations and establish controls for the secure management of encryption keys.

### PR.DS-02 — Protect: Data Security
**Status**: Not Addressed
**Evidence from Policy**: Snippet 2: Databases containing customer information should be encrypted.
**Gap**: The policy does not explicitly mandate the use of encryption for data in transit, which is the core focus of PR.DS-02 (protecting data-in-transit). While Snippet 2 addresses encryption, it does not specify *where* or *how* this encryption must be applied (i.e., in transit) or what protocols must be used, which is required by the Implementation Guidance for PR.DS-02.
**Recommendation**: The policy needs to be updated to explicitly address the protection of data in transit, including requirements for encryption protocols (e.g., TLS 1.2 or higher) and the disabling of legacy protocols, as outlined in the Implementation Guidance for PR.DS-02.

---

## Out-of-Scope Subcategories

These subcategories require separate policy documents that are not covered by the input policy:

| Subcategory | Required Policy Template(s) |
|-------------|---------------------------|
| PR.AA-01 | Access Control Policy, Account Management/Access Control Standard, Configuration Management Policy, Identification and Authentication Policy, Sanitization Secure Disposal Standard, Secure Configuration Standard, Secure System Development Life Cycle Standard |
| PR.AA-02 | Access Control Policy, Account Management/Access Control Standard, Authentication Tokens Standard, Configuration Management Policy, Identification and Authentication Policy |
| PR.AA-03 | Remote Access Standard |
| PR.AA-04 | Access Control Policy, Account Management/Access Control Standard, Authentication Tokens Standard, Configuration Management Policy, Identification and Authentication Policy |
| PR.AA-05 | Access Control Policy, Account Management/Access Control Standard, Configuration Management Policy, Identification and Authentication Policy, Sanitization Secure Disposal Standard, Secure Configuration Standard, Secure System Development Life Cycle Standard, Remote Access Standard |
| PR.AA-06 | Encryption Standard, Information Security Policy, Maintenance Policy, Media Protection Policy, Mobile Device Security, System and Communications Protection Policy |
| PR.AT-01 | Information Security Policy, Personnel Security Policy, Physical and Environmental Protection Policy, Security Awareness and Training Policy, Acceptable Use of Information Technology Resource Policy |
| PR.AT-02 | Information Security Policy, Personnel Security Policy, Physical and Environmental Protection Policy, Security Awareness and Training Policy, Access Control Policy, Account Management/Access Control Standard, Authentication Tokens Standard, Configuration Management Policy, Identification and Authentication Policy, Acceptable Use of Information Technology Resource Policy |
| PR.DS-10 | Sanitization Secure Disposal Standard, Secure Configuration Standard, Secure System Development Life Cycle Standard, Maintenance Policy, Media Protection Policy, Mobile Device Security |
| PR.DS-11 | Maintenance Policy, Media Protection Policy |
| PR.IR-01 | Remote Access Standard, Mobile Device Security, Encryption Standard, Media Protection Policy, System and Communications Protection Policy |
| PR.IR-02 | Secure Configuration Standard, Secure System Development Life Cycle Standard, Sanitization Secure Disposal Standard, Maintenance Policy |
| PR.IR-03 | Secure System Development Life Cycle Standard, System and Information Integrity Policy, 802.11 Wireless Network Security Standard |
| PR.IR-04 | System and Information Integrity Policy |
| PR.PS-01 | Configuration Management Policy |
| PR.PS-02 | Maintenance Policy |
| PR.PS-03 | Sanitization Secure Disposal Standard, Access Control Policy |
| PR.PS-04 | Identification and Authentication Policy |
| PR.PS-05 | Configuration Management Policy, Secure Configuration Standard |
| PR.PS-06 | Sanitization Secure Disposal Standard |

---

## Protect Function — Overall Maturity Assessment
**Rating**: Partially Implemented
**Justification**: Of 2 in-scope subcategories, 0 fully addressed, 1 partially addressed, 1 not addressed. 20 subcategories are out of scope for this policy.
**Top Priority Gaps**:
1. **PR.DS-02** — The policy does not explicitly mandate the use of encryption for data in transit, which is the core focus of PR.DS-02 (p
2. **PR.DS-01** — The policy establishes the need for data at rest protection and identifies encryption as the primary control (Snippet 1)
