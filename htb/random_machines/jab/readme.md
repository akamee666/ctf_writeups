
yoo one more machine :) 

```bash
$ sudo openvpn YourVPN.ovpn
$ sudo vim /etc/hosts
```

starting your vpn and add the machine's ip address in your host file to make it easier to remember. 

![](attachments/Pasted%20image%2020240308163722.png)

starting a nmap scan, let me explain the flag that i'm using here:

```
-Pn - This flag disable the ping scan to see if the host or hosts are up and if they are, continue with the another scan such a port scan. This can be useful when you are enumerating a big network or more than one host, but in this case is useful so i disable it.

-sC - This flag is same that --script=default and it's related to the Nmap Script Engine(NSE), NSE is a feature from nmap that allow users to write and share scripts in Lua Language to useful network tasks and this scripts are executed in parallel your command runs and can be found at "/usr/share/nmap/scripts/". -sC means that nmap will use "defaults scripts" what means probably mean a bunch of scripts but it's useful(sometimes not stealth).

-sV - This flag is used to enumerate services and versions, when nmap finds a open port, he will tries to connect to get some information about what kinda of service it is and tries to guess the version. Again, is not the best choice if you are trying to be stealth again because it establish a connection from your machine to your target.

-vv - increase verbosity because i want to see all details in output.

jab.htb - Is the host name that you've added to your host file, it can be just the ip address too, doesn't change much.

-oX - I'm using this flag to generate a xml output to import using the msfconsole after the scan is done.

tee - The last one is a pipe and tee to send all output that is generate in terminal to perfection_scan.log file.
```

After this scan is good to make another to scan through all ports using the -p- flag just to make sure, but usually i don't do it.

the result of our scan is here and let's see.

![](attachments/Pasted%20image%2020240308165550.png)

there is a lot of services that i haven't ever seen in my life so let me do some search about them, but while i'm doing this i'm gonna let enum4linux running to enumerate the netbios services available. I think this machine will take time but it's good reason to learn something new.
![](attachments/Pasted%20image%2020240308190113.png)



The official ports (TCP:5222 and TCP:5269) are listed in RFC 6120. Contrary to the claims of a previous answer, XEP-0174 does not specify a port. Thus TCP:5298 might be customary for Link-Local XMPP, but is not official.

You can use other ports than the reserved ones, though: You can make your DNS SRV record point to any machine and port you like.

File transfers (XEP-0234) are these days handled using Jingle (XEP-0166). The same goes for RTP sessions (XEP-0167). They do not specify ports, though, since Jingle negotiates the creation of the data stream between the XMPP clients, but the actual data is then transferred by other means (e.g. RTP) through that stream (i.e. not usually through the XMPP server, even though in-band transfers are possible). Beware that Jingle is comprised of several XEPs, so make sure to have a look at the whole list of XMPP extensions.

