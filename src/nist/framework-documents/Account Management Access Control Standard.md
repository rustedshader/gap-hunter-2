| **[Entity]**  **Information Technology Standard**                    | **No:**                    |
|----------------------------------------------------------------------|----------------------------|
| **IT Standard**  :  **Account Management / Access Control Standard** | **Updated:**               |
|                                                                      | **Issued By:**  **Owner:** |

## 1.0 Purpose and Benefits

The purpose of this standard is to establish the rules and processes for creating, maintaining and controlling the access of a digital identity to an entity’s applications and resources for means of protecting their systems and information.

## 2.0 Authority

*[Organization information]*

## 3.0 Scope

This standard covers all systems developed by, or on behalf of the entity, that require authenticated access. This includes all development, test, quality assurance, production and other ad hoc systems.

## 4.0 Information Statement

Account management and access control includes the process of requesting, creating, issuing, modifying and disabling user accounts; enabling and disabling access to resources and applications; establishing conditions for group and role membership; tracking accounts and their respective access authorizations; and managing these functions.

1. **Account Management/Access Control Roles**

Account management and access control require that the roles of Information Owner, Account Manager and, optionally, Account Administrator and Entitlement Administrator, are defined and assigned for each resource and application.  A listing of authorized users in these roles must be documented and maintained.  The associated tasks and responsibilities for each role are described below.  Each role may belong to one or more individuals depending on the application.  In some cases, a single individual or group may be assigned more than one of these roles.

1. **Information Owner:** Information owners are people at the managerial level within an entity who:
1. Define roles and groups, as well as the corresponding level of access to resources for that role or group.
2. Determining who should have access.
3. Determine the identity assurance level for the application and/or data.
4. Review that accounts and access controls are commensurate with overall business function and that the associated rights have been properly assigned, at a minimum, annually.
5. Require business units with access to protected resources to notify account managers when accounts are no longer required, such as when users are terminated or transferred and when individual access requirements change.

1. **Account Manager:** Account managers maintain accounts.  They are the delegated custodians of protected data.  Account managers:
1. Determine the technical specifications needed to set access privileges.
2. Delegate account management functions to account administrators.
3. Create and maintain procedures used in managing accounts.
4. Perform all account administrator duties as required.

1. **Account Administrators:** Account administrators are an optional subset of the account manager role.  They do not determine procedures. System rights and/or responsibilities are assigned to them by the account manager.  All account administrator responsibilities are contained within the role of account manager should an account administrator not exist.  A subset of account administrator duties may be assigned as appropriate. For example, a role for password reset only may exist for service desk employees. Additionally, some of these responsibilities may remain with the account manager should that manager determine it is necessary.  For account management, the administrator may:
1. Enroll new users.
2. Enable/disable user accounts.
3. Create and maintain user roles and groups.
4. Assign rights and privileges to a user or group.
5. Collect data to periodically review user accounts and their associated rights.
6. Assign new authentication tokens (e.g., password resets).
1. Collect data to periodically review user accounts and their associated rights.
2. Maintain any necessary information supporting account administration activities including account management requests and approvals.

1. **Account Types**

Account types include:  Individual, Privileged, Service, Shared, Default Non-Privileged (e.g., Guest, Anonymous), Emergency, and Temporary.  All account types must adhere to all applicable rules as defined in the Authentication Tokens Standard.

1. **Individual Accounts:** An individual account is a unique account issued to a single user.  The account enables the user to authenticate to systems with a digital identity. After a user is authenticated, the user is authorized or denied access to the system based on the permissions that are assigned directly or indirectly to that user.
2. **Privileged Accounts:** A privileged account is an account which provides increased access and requires additional authorization. Examples include a network, system or security administrator account.  A privileged account may only be provided to members of the workforce whom require it to accomplish their job duties. The use of privileged accounts must be compliant with the principle of least privilege. Access will be restricted to only those programs or processes specifically needed to perform authorized business tasks and no more. There are two privileged account types - Administrative Accounts and Default Accounts.

1. **Administrative Accounts:** Accounts given to a user that allow the right to modify the operating system or platform settings, or those which allow modifications to other accounts.  These accounts must:
1. be at an Identity Assurance Level commensurate with the protected resources to which they access.
2. not have user-IDs that give any indication of the user’s privilege level, e.g., supervisor, manager, administrator, or any flavor thereof.
3. be internally identifiable as an administrative account per a standardized naming convention.
4. be revoked in accordance with organizational requirements

1. **Default Privileged Accounts:** Default privileged accounts (e.g., root, Administrator) are provided with a particular system and cannot be removed without affecting the functionality of the system. Default privileged accounts must:
1. be disabled if not in use or renamed if technically possible.
2. only be used for the initial system installation or as a service account.  When technically feasible, alerts must be issued to the appropriate personnel when there is an attempt to log-in with the account for access.
3. not use the initial default password provided with the system.
4. have password known or accessible by at least two individuals within the SE, if password is known by anyone. As such, restrictions for shared accounts, outlined below, must be followed.
1. be restricted to specific devices and hours when possible.
2. never be used interactively by a user for any purpose other than the initial system installation or if absolutely required for system troubleshooting or maintenance. Wherever technically feasible, administrators should leverage “switch user” (SU) or “run as” for executing processes as service accounts.
3. never be for any purpose beyond their initial scope.
4. be internally identifiable as a service account per a standardized naming convention, where possible.
5. not allow its password to be reset according to any standardized and/or forced schedule.  However, should an employee with knowledge of said password leave the entity, that password must be changed immediately.
6. have password known or accessible by at least two individuals within the entity, if password is known by anyone. As such, restrictions for shared accounts, outlined below, must be followed.
1. be restricted to specific devices and hours when possible.
2. wherever technically feasible, have its users log on to the system with their individual accounts and “switch user” (SU) or “run as” the shared account.
3. have strictly limited permissions and access only to the system(s) required.
1. have limited rights and permissions.
2. only be allowed after a risk assessment
3. have compensatory controls that include restricted network access.
4. be assigned a password that the user cannot change but that is changed monthly, at a minimum, by an administrator.
5. not allow the account to be assigned for delegation by another account.
6. have a log maintained of users to whom the password is given.
3. T **emporary Accounts:** Temporary accounts are intended for short-term use and include restrictions on creation, point of origin, usage (i.e., time of day, day of week), and must have start and stop dates. An entity may establish temporary accounts as a part of normal account activation procedures when there is a need for short-term accounts without the demand for immediacy in account activation, such as for vendors, manufacturers, etc. These accounts must have strictly limited permissions and access only to the systems required.
2. **Account Management and Access Control Functions**

Automated mechanisms must be employed to monitor the use and management of accounts.  These mechanisms must allow for usage monitoring and notification of atypical account usage. Thresholds for alerting should be set based on the criticality of the system or assurance level of the account.

Staff in the appropriate account management/access control role(s) must be notified when account management activities occur, such as, accounts are no longer required, users are terminated or transferred, or system usage or need-to-know changes.  This should be automated where technically possible.

Automated access control policies that enforce approved authorizations for information and system resources must be in place within systems.  These access control polices could be identity, role or attribute based.

By default, no one has access unless authorized.

The Identity Assurance Level (IAL) of a system determines the degree of certainty required when proofing the identity of a user.  The following table describes the level of confidence associated with each IAL.

| *Identity Assurance Level*   | *Description*                                            |
|------------------------------|----------------------------------------------------------|
| 1                            | Low or no confidence in the asserted identity’s validity |
| 2                            | Confidence in the asserted identity’s validity           |
| 3                            | High confidence in the asserted identity’s validity      |
|                              |                                                          |

Table 1 reflects the standards for account management at each assurance level.

**Table 1 – Account Management Standards per Identity Assurance Level**

|                                                                                                                                                                                                                                                                                                                                      | Identity Assurance Levels   | Identity Assurance Levels   | Identity Assurance Levels   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------|-----------------------------|-----------------------------|
| Category                                                                                                                                                                                                                                                                                                                             | 1                           | 2  .                        | 2                           |
| Account disabled automatically after  *x*  days of inactivity                                                                                                                                                                                                                                                                        | 1096                        | 90                          | 90                          |
| Send notification  *x*  days before account disabled                                                                                                                                                                                                                                                                                 | 30                          | 30                          | 14                          |
| Account locked after  *x*  number of consecutive failed login attempts                                                                                                                                                                                                                                                               | 10                          | 5                           | 3                           |
| Account creation requires an authoritative attribute that ties the user to their account. For example, this could be an employee ID, driver’s license ID, tax ID, or unique individual email address.                                                                                                                                | No                          | Yes                         | Yes                         |
| Email notification will be sent to the user for the following events:  - Token change (password, pre-registered knowledge token, out of band (OOB) token information) - Account disabled due to invalid attempts - Forgotten User Identification (UID) issued - Account attribute change (e.g., name change) - Account re-activation | If known                    | Yes                         | Yes                         |
| Self-service functionality allowed                                                                                                                                                                                                                                                                                                   | Yes                         | Yes                         | No                          |

For all Assurance Levels, the following must be adhered to.

1. **Creating New Accounts:** To create an account, there must be a valid access authorization based on an approved business justification and a request must be made to create the account.
2. **Modifying Account Attributes (i.e., changing users’ names, demographics, etc.):** Modifications must only be made by the authenticated user or an authorized account manager.
3. **Enabling Access:** Access is granted, based on the principle of least privilege, with a valid access authorization.
4. **Modifying Access:** **Access modifications must include a valid authorization.  When there is a position change (not including separation), access is immediately reviewed and removed when no longer needed.**
5. **Disabling Accounts/Removing Access:**

1. **De-provisioning Upon Separation** : All user accounts (including privileged) must be disabled immediately upon separation. In addition, credentials must be revoked in accordance with organizational requirements, and access attributes must be removed.  Self-service mechanisms may not be used to re-enable the account.

1. **Inactivity Disable:** When an account is disabled due to inactivity, access attributes may remain unchanged if deemed appropriate by the information owner.
1. Access to privileged accounts must be reviewed every six months (minimally) to determine whether or not they are still needed.
2. Information owners must review account authorizations and/or user access assignments on an annual basis (minimally) to determine if all access is still needed.
3. Accounts or records of the account must be archived after 5 years of inactivity or after specific audit purposes are met.
6. **Secure Log on Procedures:** Where technically feasible, access must be controlled by secure log-on procedures as follows:
1. Must display the following information on completion of a successful log-on:
1. Date and time of the previous successful log-on; and
2. Details of any unsuccessful log-on attempts since the last successful log-on.

1. **Session Inactivity Lock:** Sessions must be locked after a maximum inactivity period of 15 minutes.  Session inactivity locks are temporary actions taken when users stop work and move away from their immediate vicinity but do not want to log out because of the temporary nature of their absences.  Users must re-authenticate to unlock the session.
2. **Connection Time-out:** Sessions must be automatically terminated after 18 hours or after “pre-defined” conditions such as targeted responses to certain types of incidents.
3. **Logging/Auditing/Monitoring:** All account activity must be logged and audited in accordance with the Security Logging Standard.  The ability to modify or delete audit records must be limited to a subset of privileged accounts. Any modification to access attributes must be recorded and traceable to a single individual.

## 5.0 Compliance

This standard shall take effect upon publication. Compliance is expected with all enterprise policies and standards. Policies and standards may be amended at any time.

If compliance with this standard is not feasible or technically possible, or if deviation from this policy is necessary to support a business function, entities shall request an exception through the Chief Information Security Officer’s exception process.

## 6.0 Definitions of Key Terms

| Term   | Definition   |
|--------|--------------|
|        |              |

## 7.0 Contact Information

Submit all inquiries and requests for future enhancements to the standard owner at:

**[Entity Address]**

## 8.0 Revision History

This standard shall be reviewed at least once every year to ensure relevancy.

| **Date**   | **Description of Change**   | **Reviewer**   |
|------------|-----------------------------|----------------|
|            |                             |                |

## 9.0 Related Documents

- Authentication Tokens Standard
- Security Logging Standard
- [NIST Special Publication 800-63-3 Digital Identity Guidelines](https:/nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63-3.pdf)