# Patch Management Standard
## Organization: FinServ Capital Group
## Version: 2.4 | Effective Date: September 1, 2024 | Classification: Internal

---

## 1. Purpose and Regulatory Context

This Patch Management Standard establishes the requirements for identifying, testing, and deploying security patches across FinServ Capital Group's technology infrastructure. Effective patch management is critical for maintaining the security posture required by:

- Federal Financial Institutions Examination Council (FFIEC) IT Examination Handbook
- Payment Card Industry Data Security Standard (PCI DSS) — Requirement 6
- SEC Regulation S-P (Safeguards Rule)
- NIST SP 800-40 Guide to Enterprise Patch Management Planning

Failure to maintain a current patch posture represents one of the most commonly exploited attack vectors in financial sector breaches. This standard ensures compliance with regulatory expectations and protects customer financial data.

---

## 2. Scope

This standard applies to:
- All operating systems (Windows Server, Linux/UNIX, macOS) in production, development, and testing environments
- All network devices (routers, switches, firewalls, load balancers)
- All database management systems (SQL Server, Oracle, PostgreSQL)
- All enterprise applications and middleware
- All endpoint devices (workstations, laptops) managed by FinServ Capital Group

Third-party hosted systems (SaaS applications) are excluded from this standard but are subject to vendor assessment requirements in the Vendor Management Policy.

---

## 3. Asset Inventory Requirements

**Hardware Inventory:**
An up-to-date hardware inventory is a prerequisite for effective patch management. The IT Operations team maintains a hardware asset inventory in the CMDB that includes:
- Asset identifier and serial number
- Make, model, and hardware version
- Operating system and current version
- Network location and IP address
- Asset owner and business unit
- Criticality rating (Critical, High, Medium, Low)

The hardware inventory is synchronized with the network discovery tool weekly. Discrepancies between the CMDB and discovered devices are investigated within 5 business days.

**Software Inventory:**
A software inventory is maintained for all managed systems. The inventory includes:
- Application name and version
- Vendor/publisher
- Installation date and last update
- License status
- Supported/end-of-life status

End-of-life software that cannot be patched must be mitigated through compensating controls or replaced within 90 days of reaching end-of-life status.

---

## 4. Vulnerability Identification

**Vulnerability Scanning:**
Vulnerability scans are conducted using enterprise vulnerability management tools:
- **Internal network scan:** Weekly, covering all internal IP ranges
- **Authenticated scan (workstations/servers):** Monthly, using domain credentials for comprehensive assessment
- **Database scan:** Monthly, targeting all database systems
- **Web application scan:** Quarterly (DAST) and upon major releases (SAST)

Scan results are processed and de-duplicated automatically. New vulnerabilities are reviewed by the Security Engineering team within 2 business days of scan completion.

**Threat Intelligence for Vulnerability Prioritization:**
The Security team subscribes to the following threat intelligence sources:
- CISA Known Exploited Vulnerabilities (KEV) Catalog
- FS-ISAC threat intelligence feeds (financial sector specific)
- Vendor security advisories (Microsoft MSRC, Red Hat, Oracle, Cisco)
- National Vulnerability Database (NVD) CVSS scores

Vulnerabilities listed in the CISA KEV Catalog are automatically escalated to Critical priority regardless of CVSS score, reflecting active exploitation in the wild.

---

## 5. Patch Classification and Prioritization

All patches are classified according to the following priority matrix, which considers CVSS score, active exploitation status, asset criticality, and regulatory applicability:

| Priority | Criteria | Examples |
|---|---|---|
| **Emergency** | CVSS ≥ 9.0 AND actively exploited OR CISA KEV listed | Log4Shell, ProxyLogon, PrintNightmare |
| **Critical** | CVSS ≥ 9.0 OR CVSS ≥ 7.0 AND critical asset | Remote code execution, authentication bypass |
| **High** | CVSS 7.0–8.9 on standard assets | Privilege escalation, sensitive data exposure |
| **Medium** | CVSS 4.0–6.9 | Denial of service, information disclosure |
| **Low** | CVSS < 4.0 | Configuration-only, low exploitability |

**Vulnerability Analysis Process:**
Before a vulnerability is assigned a priority, the Security Engineering team assesses:
1. Exploitability (is a public exploit available?)
2. Asset exposure (internet-facing vs. internal)
3. Business impact if exploited (data sensitivity, service criticality)
4. Compensating controls in place (network segmentation, WAF, EDR)

This analysis may result in adjusting the base CVSS priority up or down based on environmental context.

---

## 6. Patch Deployment Timelines

Patching must be completed within the following Service Level Agreements (SLAs) based on patch priority:

| Priority | SLA — Internet-Facing Systems | SLA — Internal Systems |
|---|---|---|
| Emergency | 24 hours | 48 hours |
| Critical | 72 hours | 7 days |
| High | 14 days | 30 days |
| Medium | 30 days | 60 days |
| Low | 90 days | 180 days |

**SLA Exceptions:**
Where business operations prevent patching within the defined SLA, an exception must be:
1. Requested by the system owner in the GRC platform
2. Approved by the CISO (for Critical and above) or IT Security Manager (for High and below)
3. Accompanied by a documented compensating controls plan
4. Reviewed every 30 days until patching is complete

---

## 7. Patch Testing and Change Management

**Testing Requirements:**
All patches are tested before deployment to production except for Emergency patches, which follow an expedited process:

- **Emergency patches:** Deploy to one representative system in production, monitor for 2 hours, then proceed with full deployment
- **Critical patches:** Test in isolated lab environment for 24 hours before production deployment
- **High and below:** Test in staging environment following standard change management procedures

**Change Management Integration:**
Patch deployments are managed through the IT Change Management process:
- Emergency patches: Emergency Change Request (approved by CISO and IT Director)
- Routine patches: Standard Change (pre-approved for recurring monthly patch cycles)
- High-impact patches: Normal Change (requires CAB review)

Monthly patch windows are established:
- Production servers: Second Tuesday of each month (Patch Tuesday) + 72 hours
- Workstations: Third Tuesday of each month
- Network devices: Fourth Thursday of each month (with network team approval)

---

## 8. Secure Configuration Baseline

**Configuration Standards:**
All managed systems must conform to configuration baselines derived from:
- CIS Benchmarks (Level 1 for standard systems, Level 2 for high-security systems)
- Vendor hardening guides
- Organizational security configuration standards

Patch deployment includes verification that configuration baselines remain intact after patching. Systems are automatically re-baselined if configuration drift is detected during post-patch scanning.

**Unauthorized Software Control:**
Only approved software may be installed on managed systems. The IT Operations team maintains an approved software list. Unauthorized software detected during vulnerability scans is flagged for removal. Users may not install software without IT approval through the software request process.

---

## 9. Compliance Monitoring

**Patch Compliance Reporting:**
Patch compliance dashboards are maintained for all asset groups:
- Real-time compliance percentage by asset group
- SLA breach tracking (open vulnerabilities past SLA)
- Trending data (30/60/90 day compliance trends)
- Exception register with compensating controls

Compliance reports are generated weekly and reviewed by the IT Security Manager. Monthly compliance summaries are presented to the CISO. Quarterly compliance reports are provided to the Audit Committee.

**Vulnerability Scanning for Compliance:**
Post-patch vulnerability scans are conducted within 48 hours of major patch deployments to verify patch effectiveness. Scan results confirming patch application are retained as evidence for regulatory and audit purposes.

---

## 10. Metrics and Key Performance Indicators

The following KPIs are tracked for the patch management program:

| KPI | Target | Measurement Frequency |
|---|---|---|
| Emergency patch SLA compliance | 100% | Per-incident |
| Critical patch SLA compliance | 95% | Monthly |
| High patch SLA compliance | 90% | Monthly |
| Mean Time to Patch (Critical) | < 5 days | Monthly |
| Patch scan coverage | 98% of managed assets | Weekly |
| Recurrence rate of same vulnerability | < 5% | Quarterly |

KPIs below target trigger a review and corrective action plan within 10 business days.

---

## 11. Roles and Responsibilities for Patch Management

| Role | Responsibilities |
|---|---|
| CISO | Approve emergency changes; review monthly compliance; accept exceptions for Critical vulnerabilities |
| IT Security Manager | Manage vulnerability scanning; review scan results; approve High and below exceptions |
| Security Engineering | Analyze vulnerabilities; assign priorities; validate patch effectiveness |
| IT Operations | Deploy patches within SLA; maintain asset inventory; document exceptions |
| System/Application Owners | Approve changes to owned systems; participate in testing; accept risk for exceptions |

---

## 12. Document Control

| Attribute | Value |
|---|---|
| Standard Owner | IT Security Manager |
| Review Frequency | Annual |
| Last Reviewed | August 2024 |
| Next Review Due | August 2025 |
| Approved By | CISO |
