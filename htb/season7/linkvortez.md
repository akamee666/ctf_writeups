# LinkVortex Linux Easy Machine - Season7

## Initial Enumeration
Start by enumerating the website. Subdomain enumeration reveals a `.dev` subdomain. Directory enumeration on this subdomain shows that a `.git` repository is available.

### Key Findings:
- **Modified File in `.git`**: The `.git` repository contains a modified file with a password.
- **`robots.txt`**: This file reveals several paths, including `/ghost`, which is a login page.

---

## Gaining Access
1. **Login to `/ghost`**:
   - Use the password found in the `.git` repository.
   - Guess the user email based on the domain machine name (e.g., `admin@linkvortex.htb`).

2. **Exploit CVE-2023-40028**:
   - Once logged in, you discover that the system is vulnerable to **CVE-2023-40028**.
   - The vulnerability allows you to execute scripts from the repository.

---

## Exploring the Docker Container
After gaining access, you realize you’re inside a Docker container. While it’s easy to get lost in a rabbit hole, you remember to search for clues in the `.git` repository.

### Key Findings:
- **Project Location**: The project is located at `/var/lib/ghost`.
- **Default Configuration Files**: These files contain another set of credentials.

---

## SSH Access
Use the credentials found in the configuration files to SSH into the machine:
```bash
ssh user@linkvortex.htb
```
Do a `sudo -l` to search for exploits to privsec and you will find that this user can run a script as root.

To bypass the script you need to:
```bash
ln -s /root/root.txt xyz.txt  # normally it would be reject by the script bc script search for the words "root"/"etc" and if it finds it would unlink the file.
ln -s /home/bob/xyz.txt xyz.png # so then you link it again to a empty file which will just have a link to another file, so the grep doesn't find the "root" string
sudo CHECK_CONTENT=true /usr/bin/bash /opt/ghost/clean_symlink.sh /home/bob/xyz.png # enable CHECK_CONTENT so the script shows the content when the link is moved into quarantine and voala 
```

