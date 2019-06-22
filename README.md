# bruteforce_satoshi
A tool for brute-forcing passpharases of Satoshi's Treasure

## usage
This tool requires python 3.5 or later.

```
> python3 bruteforce_satoshi.py k1 '[ao]r?i{tal,t}'
write cache data to encrypted_msgs.txt...
start...
found: orbital
```

### pattern syntax
You can use '?' and '[abc]' and '{abc,def,hij}' as shell expansions.

Some character sets is defined. '{%lower}' means lowercase alphabets.

'?' is replaced to '{%lower}' by default.
You can specify default charsets by '-s' option.

ex: `-s %alpha,%number,-,.`

'-l' option is useful for testing.
```
> python3 bruteforce_satoshi.py k1 '[ao]rbi{tal,t}' -l
orbit
arbit
arbital
orbital
total: 4 candidates
```

Or, you can use '-c' option.
```
> python3 bruteforce_satoshi.py k1 'or?????' -c
total: 11881376 candidates
```

### using a dictionary file
```
> cat dictionary.txt
black
white
hole
star
> python3 bruteforce_satoshi.py --dic dictionary.txt k3 '{%dic}{%dic}'
write cache data to encrypted_msgs.txt...
start...
found: blackhole
```
