# Dog Linux Easy Machine - Season7

## Initial Enumeration
1. **Find `.git` Directory**:
   - Discover the `.git` directory on the target machine.
   - Inspect the `settings.php` file to find MySQL credentials (username and password).

2. **Search for User Email**:
   - Use the MySQL credentials to search for the user email in the database.
   - The email can be found at:
     ```
     http://10.10.11.58/files/config_83dddd18e1ec67fd8ff5bba2453c7fb3/active/
     ```

---

## Gaining Access
1. **Log in as Admin**:
   - Use the discovered credentials to log in as the admin user.

2. **Exploit Backdrop CMS**:
   - Exploit the Backdrop CMS by uploading a malicious `shell.tar.gz` file.
   - **Note**: The author made it look like a `.zip` file was required, causing confusion and wasting time.

3. **Obtain a Reverse Shell**:
   - After uploading the shell, establish a reverse shell to gain access to the target machine.

---

## Privilege Escalation
1. **Log in as `johncusack`**:
   - Use the same password found earlier to log in as the user `johncusack`.

2. **Exploit `bee` Binary**:
   - Discover that `johncusack` can run the `bee` binary with root privileges.
   - Use this privilege escalation vector to execute a script and read the root flag.
   - Run script to read root flag using johncusack root priviliges

---

