import json
from base64 import b64decode
from pwn import * # remote

# The flaw that allows us to capture the flag is that a character
# is not allowed to map onto itself, so by process of elimination,
# we can figure out what each character must be. There is on the
# order of 1/100 chance per character of mapping to itself, and
# multiplying by a 20-char flag length gives us about 2000 successful
# requests on average that we'll need to find the entire solution.

def json_recv(r):
    line = r.recvline()
    return json.loads(line.decode())

def json_send(r, to_send):
    request = json.dumps(to_send).encode()
    r.sendline(request)

if __name__ == '__main__':
    FLAG_LENGTH = 20
    DEBUG = False
    if DEBUG:
        r = remote('socket.cryptohack.org', 13370, level='debug')
    else:
        r = remote('socket.cryptohack.org', 13370)

    # Need to clear the buffer first
    r.recvline()

    # The printable ASCII characters, the valid chars for our flag.
    # We will whittle down the possible chars to 1 for each position.
    # Use sets, as they make this type of operation intuitive.
    sifted = [set(range(32, 127)) for i in range(FLAG_LENGTH)]
    errors = 0
    ciphers = 0

    # Until there is only one possible value for every position in sifted
    while FLAG_LENGTH != len([s for s in sifted if len(s) == 1]):
        json_send(r, {'msg': 'request'})
        received = json_recv(r)
        if 'ciphertext' in received:
            ciphers += 1
            cipher = b64decode(received['ciphertext'])
            print(cipher)
            for pos, val in enumerate(cipher):
                sifted[pos] -= {val}
        else:
            errors += 1

    # sifted will look something like [{99}, {114}, ...] at this point
    # Convert each single element set to a list, capture the value,
    # convert it to a character, and then stringify the whole thing
    flag = ''.join([chr(list(s)[0]) for s in sifted])

    print()
    print('Flag:', flag)
    print('Ciphers:', ciphers)
    print('Errors:', errors)
