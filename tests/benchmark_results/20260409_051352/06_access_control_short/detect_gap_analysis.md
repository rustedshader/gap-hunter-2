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
