## Usage - Easy Linux Machine from Hackthebox

hello :D

I have already did this machine before but somehow my VM just died and i was not able to get back the write-up that i was making ;(. I'm gonna make this machine again and trying to recreate the write-up that i have lost, i hope i can remember my thinking flow when i was in my first try. 

straight to work, start the machine and get into the htb network using the vpn file.
![](attachments/Pasted%20image%2020240502171547.png)

adding this IP to hosts file to make easy to write on browser>
![](attachments/Pasted%20image%2020240502172540.png)

Now, i normally making a scan using this command but as said before i already made this machine and this scan will only give two open ports. One is a HTTP server running on 80 and an ssh running on 22, do the scan if you want to but there is nothing much interesting. 
```bash
# nmap -Pn -sC -sV usage.htb -oX usage_scan.xml | tee usage_can.log 
```

-Pn - This flag disable the ping scan to see if the host or hosts are up and if they are, continue with the another scan such a port scan. This can be useful when you are enumerating a big network or more than one host, but in this case is useful so i disable it.

-sC - This flag is same that --script=default and it's related to the Nmap Script Engine(NSE), NSE is a feature from nmap that allow users to write and share scripts in Lua Language to useful network tasks and this scripts are executed in parallel your command runs and can be found at "/usr/share/nmap/scripts/". -sC means that nmap will use "defaults scripts" what means probably mean a bunch of scripts but it's useful(sometimes not stealth).

-sV - This flag is used to enumerate services and versions, when nmap finds a open port, he will tries to connect to get some information about what kinda of service it is and tries to guess the version. Again, is not the best choice if you are trying to be stealth again because it establish a connection from your machine to your target.

usage.htb - Is the host name that you've added to your host file, it can be just the ip address too, doesn't change much.

-oX - I'm using this flag to generate a xml output, what makes it easier to import in services like msfconsole. 

tee - The last one is a pipe and tee to send all output that is generate in terminal to perfection_scan.log file.

Taking a look at the HTTP port and there is a login page.
![](attachments/Pasted%20image%2020240502173344.png)

This page also has redirection to an reset password page, login to a admin panel and an register page as you can see right up there in the right. When i first saw this, i went straight trying default credentials and bad characters like ',$|; in all pages, fortunately when i send an single comma on the reset password page, it gives me back an 500 status code what is good signal of SQLi. 

![](attachments/Pasted%20image%2020240502173907.png)

Just to make sure if there is really an injection i enter an valid statement like two single commas to see if i get an different response.  And as you can see below, it doesn't give the 500 error response :D.
![](attachments/Pasted%20image%2020240502174210.png)

At this time my mind was like, "i probably need to dump credentials and login in somewhere". Just to record, I wasn't aware of the admin login page, cause i was using a the browser in window mode and that make those 3 links right up there on the right don't show up unless you are full screen with your browse.

Then now i need to dump credentials, do it manually is such a pain and that's when tools like sqlmap shows up to make the life easier to us.

Let's starting build our payload, first I did use Burp to get the request and just copy and paste in the "request" file. (I'm not creative with names i'm sorry)
![](attachments/Pasted%20image%2020240502180111.png)

![](attachments/Pasted%20image%2020240502180523.png)
If you are having an error saying that your request file doesn't exist, try provide the full path, might work. Make sure to say to sqlmap to don't follow redirects, I don't know why but i couldn't exploit it right if i follow these redirects, so make sure to refuse these two redirect questions.
 ![](attachments/Pasted%20image%2020240502181120.png)

Ok, first try sqlmap couldn't exploit it, let's follow the instructions and increase the risk and level flags to see what happens.

![](attachments/Pasted%20image%2020240502192709.png)

the machine fell off when sqlmap was running and my payload stopped working, so after some changes and tries it finally work, here is the payload that i have used:
```shell
sqlmap -r /home/akame0x01/capture_the_flag/htb/usage/request -p email --level 5 --risk 3 --dump --random-agent
```

Let's starting dumping, when comes to dump information I like to starting getting initial info and increasing the payload accordingly instead of use the -A flag wait for 2 days because it is dumping random stuff.

The last payload that I've used tell me that database is "usage_blog" and the DBMS is MySQL.
```shell
sqlmap -r /home/akame0x01/capture_the_flag/htb/usage/request -p email --level 5 --risk 3 --dbms=mysql --random-agent -D usage_blog --dump --tables
```

![](attachments/Pasted%20image%2020240502193456.png)
What we are looking for is probably in the admin_users table, let's see if we can dump that table.

```shell
sqlmap -r /home/akame0x01/capture_the_flag/htb/usage/request -p email --level 5 --risk 3 --dbms=mysql --random-agent -D usage_blog -T admin_users --dump
```

![](attachments/Pasted%20image%2020240503163145.png)

We're making progress, let's trying to break this hash using john. Copy and paste the hash into a file and use john the ripper. Usually in my first trying to break an hash using john, I don't specify an format cause it can guess based on the hash and if you don't provide an word list it uses an default that come within the package.
![](attachments/Pasted%20image%2020240503163601.png)

![](attachments/Pasted%20image%2020240503164700.png)

So now we have the username and the password to log in the admin panel, but first you must add the subdomain in your host file to be able to access it. Our hosts file must look like this:

![](attachments/Pasted%20image%2020240503164933.png)

![](attachments/Pasted%20image%2020240503165029.png)

![](attachments/Pasted%20image%2020240503165114.png)

https://flyd.uk/post/cve-2023-24249/
Now i go straight to the point that there is a CVE in this version of lavarel-admin, when i was making this machine before I could the file upload vulnerability but still struggling to get a shell, doing some search I find the CVE to the currently version and this poc help me to bypass it properly. Do the same and you will be able to execute commands on the host. 

You'll need Burp Suite or any tool that allow you to change the request in real time after it was sent and the PHP code that you want to execute, in my case i'll be using an reverse shell from somewhere that I forgot, just search for PHP reverse shell and you will be fine(read it before execute please).

![](attachments/Pasted%20image%2020240503165855.png)

Go straight to the Users tab on the admin panel and edit the Administrator profile, browse your PHP code with .jpg extension and make sure to intercept the request when clicking on the submit button and add an .php in the final of the filename.

![](attachments/Pasted%20image%2020240503170350.png)

After, click in the forward button to send the request and reload the page to see if it works. if it does you will have the devil file on the avatar, the download button available will provide an path to file but in my case I need to use net cat to listen on the port that i have specified in the reverse shell code before execute it. 
![](attachments/Pasted%20image%2020240503170622.png)

And there is!
![](attachments/Pasted%20image%2020240503171446.png)

The first thing that I gonna do is to get the ssh keys, do that same process to get a reverse shell whenever it fell off is quite boring
![](attachments/Pasted%20image%2020240503171856.png)

![](attachments/Pasted%20image%2020240503172343.png)

And we are in, get the user flag and just doing some search around the home directory you can easily find the xander(the another user) password :).

![](attachments/Pasted%20image%2020240503172632.png)

`3nc0d3d_pa$$w0rd`

The last part now is to make a privilege escalation and get the root flag, I'm not gonna lie,i couldn't figure out how to make this when i did the first time. The only reason that i have rooted this machine was someone help me giving me a nudge, i was entering in a big rabbit hole and spending a lot of time getting anywhere but after all it was quite simple.

The trick here is that xander user can run a binary called usage_management with sudo privileges. Basically this program has three options(you can rev it or debug it to understand more), backup all files inside /var/www/html/ in a zip file, backup all SQL data using sqldump and the thirty option does nothing(really), it just print out texting saying it did reset the password but it's a lie! What you need to do is create a file inside the /var/www/html/ directory and link it with the root flag inside /root/ directory so when you run usage_management again and use the option to backup the project data, it will run with sudo privileges and be able to read the flag in /root/ that is linked with the file that you've created :). 

```bash
$ cd /var/www/html
$ touch @root.txt
$ ln -s /root/root.txt root.txt
$ sudo usage_management
// choose the first option and the root flag should pop up on the terminal due some error with 7zip
```

Well, this machine was simple to exploit but not so simple to figure out where you must work on. I guess I just need to get used to Hackthebox machines instead of the thm machines, I keep up stuck for days even with the easy ones. If you have any question, feel free to reach me on any social media available on my profile.
