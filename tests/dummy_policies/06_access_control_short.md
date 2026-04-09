# Access Control and Identity Management Policy
## Organization: Nexus Software Ltd.
## Version: 1.1 | Effective Date: January 2025 | Classification: Internal

---

## 1. Purpose and Scope

This policy establishes requirements for managing user identities, controlling access to information systems, and protecting organizational resources from unauthorized access. It applies to all employees, contractors, and third parties accessing Nexus Software Ltd. systems.

Access to systems is granted based on the principle of least privilege. Users receive only the minimum access required to perform their job duties. All access rights are tied to business need and reviewed regularly.

---

## 2. Identity Management and User Provisioning

All users must have a unique individual account. Shared accounts are prohibited. User accounts are created through a formal provisioning process requiring manager approval and documented business justification.

Account provisioning follows the joiner-mover-leaver process:
- **New hires:** Accounts created within 1 business day of start date following HR notification.
- **Role changes:** Access rights reviewed and adjusted within 3 business days of role change.
- **Terminations:** All accounts disabled within 4 hours of termination notification from HR. Privileged accounts are disabled immediately upon notification.

User identities are maintained in the central identity directory. Service accounts are documented with an assigned owner and reviewed quarterly.

---

## 3. Authentication Requirements

Multi-factor authentication (MFA) is mandatory for:
- All remote access to organizational systems
- Access to systems containing sensitive or confidential data
- All administrative and privileged accounts
- Cloud platform consoles and management interfaces

Password requirements:
- Minimum 12 characters with complexity (uppercase, lowercase, number, symbol)
- Maximum 90-day expiration for standard accounts; 60 days for privileged accounts
- No reuse of previous 10 passwords
- Account lockout after 5 failed attempts with 15-minute lockout period

Single sign-on (SSO) is used for all corporate applications where technically feasible. Authentication events are logged centrally for audit purposes.

---

## 4. Access Control and Authorization

Access rights are assigned based on role-based access control (RBAC). Access roles are defined for each system and mapped to job functions. Users are assigned to roles, not granted individual permissions where avoidable.

Network access is controlled through:
- Firewall rules restricting traffic to authorized services and ports
- Network segmentation separating sensitive systems from general corporate networks
- VPN required for all remote access; split tunneling is prohibited

Physical and logical access controls are aligned: server room access requires both a valid proximity badge and a system account with appropriate rights.

Privileged access (administrator, root, service account) requires additional approval from the IT Security team. Privileged sessions are recorded where technically feasible.

---

## 5. Access Reviews and Monitoring

**Quarterly access reviews:** All user access rights are reviewed quarterly by system owners. Accounts with no activity in the past 60 days are flagged for validation or removal. Reviews are documented and retained for 12 months.

**User activity monitoring:** User activity on systems containing sensitive data is logged and monitored for:
- Unauthorized access attempts and repeated authentication failures
- Access to data outside normal job scope
- Bulk data downloads or exports
- Access outside normal business hours

Security alerts from access monitoring are reviewed within 4 hours during business hours and escalated on-call after hours.

**Audit logging:** All authentication events, access grants and revocations, and privileged actions are logged with sufficient detail to support forensic investigation. Logs are retained for 12 months minimum and protected from modification.

---

## 6. Compliance and Enforcement

Compliance with this policy is mandatory. Violations including sharing credentials, accessing unauthorized systems, or circumventing access controls will result in disciplinary action up to and including termination.

Exceptions require written approval from the IT Security Manager and must be reviewed every 90 days. All exceptions are logged in the exception register.

Annual policy review is conducted by the IT Security Manager. The policy is updated when significant changes occur in technology, organizational structure, or threat landscape.

---

*Policy Owner: IT Security Manager | Approved by: CTO | Last Reviewed: December 2024*
