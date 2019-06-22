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

Some character sets are defined. '{%lower}' means lowercase alphabets.

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

### parallel execution
```
> time python3 bruteforce_satoshi.py k1 'or?????'
start...
found: orbital
python3 bruteforce_satoshi.py k1 'or?????'  19.26s user 0.03s system 99% cpu 19.297 total
> time python3 bruteforce_satoshi.py k1 'or?????' -p 2
start...
found: orbital
python3 bruteforce_satoshi.py k1 'or?????' -p 2  27.63s user 0.70s system 178% cpu 15.886 total
> time python3 bruteforce_satoshi.py k1 'or?????' -p 4
start...
found: orbital
python3 bruteforce_satoshi.py k1 'or?????' -p 4  30.11s user 0.86s system 276% cpu 11.197 total
```
