# Protect Function — Executive Gap Summary
*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*

## Executive Summary

The Protect function shows a partial implementation maturity, with only two in-scope subcategories assessed. The most critical gaps involve data protection, specifically the lack of mandates for data in transit encryption (PR.DS-02) and comprehensive data-at-rest encryption and key management (PR.DS-01). Key recommendations include immediately mandating encryption for all storage locations and establishing protocols for data-in-transit protection. To address the extensive out-of-scope requirements, separate policies must be developed for all listed access control, system lifecycle, and incident response subcategories.

## Coverage Statistics

| Metric | Count |
|--------|-------|
| Total Subcategories | 22 |
| In Scope | 2 |
| Addressed | 0 |
| Partially Addressed | 1 |
| Not Addressed | 1 |
| Out of Scope | 20 |
| **Maturity Rating** | **Partially Implemented** |

## Critical Gaps

1. PR.DS-02
2. PR.DS-01

## Key Recommendations

1. Immediately mandate encryption for all data-at-rest locations and establish robust key management controls to address PR.DS-01.
2. Establish explicit policy requirements for data-in-transit encryption and required protocols to resolve the gap in PR.DS-02.
3. Develop and implement separate policies covering the 20 out-of-scope subcategories, including those related to Access Control, System Lifecycle, and Incident Response.

## Required Policy Documents

The following policy templates are needed to cover out-of-scope subcategories:

- Policy mandating data at rest protection via encryption for disks, databases, backups, and removable media.
- Policy requiring database encryption for customer information.
