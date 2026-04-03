| Policy #:   | Title:                                   | Effective Date:   |
|-------------|------------------------------------------|-------------------|
| x.xxx       | Identification and Authentication Policy | MM/DD/YY          |

PURPOSE
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

To ensure that only properly identified and authenticated users and devices are granted access to Information Technology (IT) resources in compliance with IT security policies, standards, and procedures.

REFERENCE
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

National Institute of Standards and Technology (NIST) Special Publication (SP) 800-53a – Identification and Authentication (IA), NIST SP 800-12, NIST SP 800-63, NIST SP 800-73, NIST SP 800-76, NIST SP 800-78, NIST SP 800-100, NIST SP 800-116;

Homeland Security Presidential Directive (HSPD) 12 Policy for a Common Identification Standard for Federal Employees and Contractors; Federal Information Processing Standards (FIPS): FIPS 201, FIPS 140

POLICY
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

This policy is applicable to all departments and users of IT resources and assets.

1. IDENTIFICATION AND AUTHENTICATION

IT Department shall:

1. Ensure that information systems uniquely identify and authenticate users or processes acting on behalf of [entity] users.

1. Ensure that information systems implement multifactor authentication for network access to privileged accounts.

1. Ensure that information systems implement multifactor authentication for network access to non-privileged accounts.

1. Ensure that information systems implement multifactor authentication for local access to privileged accounts.

1. Ensure that information systems implement replay-resistant authentication mechanisms for network access to privileged accounts.

1. Ensure that information systems implement multifactor authentication for remote access to privileged and non-privileged accounts such that one of the factors is provided by a device separate from the system gaining access and the device utilizes a cryptographic strength mechanisms that protects the primary authentication token (secret key, private key or one-time password) against compromise by protocol threats including: eavesdropper, replay, online guessing, verifier impersonation and man-in-the-middle attacks.

1. Ensure that information systems accept and electronically verify Personal Identity Verification (PIV) credentials.

1. DEVICE IDENTIFICATION AND AUTHENTICATION

IT Department shall:

1. Ensure that information systems uniquely identify and authenticate all devices before establishing a network connection.

1. IDENTIFIER MANAGEMENT

IT Department, through department information systems owners, shall:

1. Ensure that the [entity] manages information system identifiers by receiving authorization from [entity defined personnel or roles] to assign an individual, group, role, or device identifier.

1. Select an identifier that identifies an individual, group, role, or device.

1. Assign the identifier to the intended individual, group, role, or device.

1. Prevent reuse of identifiers for 90 days.

1. Disable the identifier after 30 days of inactivity.

1. AUTHENTICATOR MANAGEMENT

IT Department shall:

1. Manage information system authenticators by verifying, as part of the initial authenticator distribution, the identity of the individual, group, role, or device receiving the authenticator.

1. Establish initial authenticator content for authenticators defined by the organization.

1. Ensure that authenticators have sufficient strength of mechanism for their intended use.

1. Establish and implement administrative procedures for initial authenticator distribution, for lost/compromised or damaged authenticators, and for revoking authenticators.

1. Change default content of authenticators prior to information system installation.

1. Establish minimum and maximum lifetime restrictions and reuse conditions for authenticators.

1. Change/refresh authenticators every 90 days.

1. Protect authenticator content from unauthorized disclosure and modification.

1. Require individuals and devices to implement specific security safeguards to protect authenticators.

1. Change authenticators for group/role accounts when membership to those account changes.

1. Ensure that information systems, for password-based authentication enforce minimum password complexity that must not contain the user's entire Account Name value or entire Full Name value.

1. Ensure passwords must contain characters from three of the following five categories:

1. Uppercase characters of European languages (A through Z, with diacritic marks, Greek and Cyrillic characters);

1. Lowercase characters of European languages (a through z, sharp-s, with diacritic marks, Greek and Cyrillic characters);

1. Base 10 digits (0 through 9);

1. Non-alphanumeric characters [~!@#$%^&amp;*\_-+=`|\(){}[]:;"'&lt;&gt;,.?/](mailto:~!@) ; and

1. Any Unicode character that is categorized as an alphabetic character, but is not uppercase or lowercase. This includes Unicode characters from Asian languages.

1. Require passwords to have a minimum length of 8 characters.

1. Enforce at least one changed character when new passwords are created.

1. Store and transmit only cryptographically-protected passwords.

1. Enforce password minimum and maximum lifetime restrictions of one day and 120 days respectively.

1. Prohibit password reuse for 12 generations.

1. Allow the use of a temporary password for system logons with an immediate change to a permanent password.

1. Ensure that information system, for PKI-based authentication, validates certifications by constructing and verifying a certification path to an accepted trust anchor including checking certificate status information.

1. Enforce authorized access to the corresponding private key.

1. Map the authenticated identity to the account of the individual or group.

1. Implement a local cache of revocation data to support path discovery and validation in case of inability to access revocation information via the network.

1. Require that the registration process to receive [entity defined types of and/or specific authenticators] be conducted in person or by a trusted third party before [entity defined registration authority] with authorization by [entity defined personnel or roles].

1. Ensure that the information system, for hardware token-based authentication, employs mechanisms that satisfy [entity defined token quality requirements].

1. AUTHENTICATOR FEEDBACK

IT Department shall:

1. Ensure that information systems obscure feedback of authentication information during the authentication process to protect the information from possible exploitation/use by unauthorized individuals.

1. CRYPTOGRAPHIC MODULE AUTHENTICATION

IT Department shall:

1. Ensure that information systems implement mechanisms for authentication to a cryptographic module that meet the requirements of applicable state and federal laws, directives, policies, regulations, standards, and guidance for such authentication.

1. IDENTIFICATION AND AUTHENTICATION

IT Department shall:

1. Ensure that information systems uniquely identify and authenticate non-entity users or processes acting on behalf of non-entity users.

1. Ensure that information systems accept and electronically verify Personal Identity Verification (PIV) credentials from other government agencies.

1. Ensure that information systems accept only Federal Identity, Credential, and Access Management (FICAM) Trust Framework Solutions initiative approved third-party credentials.

1. Ensure that the organization employs only FICAM-approved information system components in [entity defined information systems] to accept third-party credentials.

COMPLIANCE

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Employees who violate this policy may be subject to appropriate disciplinary action up to and including discharge as well as both civil and criminal penalties. Non-employees, including, without limitation, contractors, may be subject to termination of contractual agreements, denial of access to IT resources, and other actions as well as both civil and criminal penalties.

POLICY EXCEPTIONS

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Requests for exceptions to this policy shall be reviewed by the Chief Information Security Officer (CISO) and the Chief Information Officer (CIO). Departments requesting exceptions shall provide such requests to the CIO. The request should specifically state the scope of the exception along with justification for granting the exception, the potential impact or risk attendant upon granting the exception, risk mitigation measures to be undertaken by the IT Department, initiatives, actions and a time-frame for achieving the minimum compliance level with the policies set forth herein. The CIO shall review such requests; confer with the requesting department.

RESPONSIBLE DEPARTMENT
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Chief Information Office and Information System Owners

DATE ISSUED/DATE REVIEWED
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

| Date Issued:   | MM/DD/YYYY   |
|----------------|--------------|
| Date Reviewed: | MM/DD/YYYY   |