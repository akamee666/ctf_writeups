## Runner - Medium Linux Machine from Hackthebox

hello :D

To begin, start the machine in hackthebox website and start your vpn as well. Also I always like to keep the IP address on my hosts file because i forgot the it very often so...

![](attachments/Pasted%20image%2020240505154300.png)

Your hosts file must look like this or similar, let's start with a nmap scan to see what we have got here.

```bash
$ sudo nmap -Pn -sC -sV runner.htb -oX usage_scan.xml | tee usage_can.log 
```

I always use this command to my first recon, if you are not sure what these flags does you can search in the nmap documentation or see other of my writeups like the Usage, there an explanation about them there. There is the result:

![](attachments/Pasted%20image%2020240505155418.png)

Few hours have already passed and I'm still very lost, the nginx website doesn't have anything useful. Neither links, inputs or anything, just an website about runners. Neither the nagios one have something, the only thing i get an valid response from http://runner.htb:8000/version and http://runner.htb:8000/health but nothing useful as you can see.

![](attachments/Pasted%20image%2020240505173908.png)

It is obvious that I'm missing something in the enumeration. I'm gonna still trying different enumerations like vhosts and subdomains, because I think I will find something in this nagios running on port 8000, during my searching i have found a lot of rce-vulnerabilities related to this program, all of them related to an plugin that comes pre-installed or old libraries that are still being use for some reason. But I'm not finding the path to explore these vulnerabilities and even didn't see if it's really exploitable, so i will continue the enumeration and when i find something useful i come back here explaining what i have made.  