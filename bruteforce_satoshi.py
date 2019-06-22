import sys
import hmac
import hashlib
import itertools
import urllib.request
import ssl
import re

FILE_NAME = 'encrypted_msgs.txt'

LOWER = list('abcdefghijklmnopqrtsuvwxyz')
UPPER = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
NUMBER = list('0123456789')

charsets = {
    'lower': LOWER,
    'upper': UPPER,
    'alpha': LOWER + UPPER,
    'number': NUMBER,
    'alnum': LOWER + UPPER + NUMBER,
    'space': list(' '),
}


def fetch_encryptedMsg(problem_id):
    url = f'https://satoshistreasure.xyz/{problem_id}'
    matcher = re.compile(r"^\s*encryptedMsg\s*=\s*'([^']*)'")

    try:
        with urllib.request.urlopen(url, context=ssl.SSLContext()) as response:
            for line in response:
                ma = matcher.match(line.decode('utf-8'))
                if ma:
                    return ma[1]
    except:
        pass
    return None


def get_encryptedMsg(problem_id):
    cache = {}
    try:
        with open(FILE_NAME, 'r') as fp:
            for line in fp:
                id, msg = line.rstrip().split(',', 1)
                cache[id] = msg
    except:
        pass

    if problem_id in cache:
        return cache[problem_id]
    
    msg = fetch_encryptedMsg(problem_id)
    if msg is None:
        raise RuntimeError(f'cannot fetch {problem_id}')
    
    cache[problem_id] = msg
    try:
        with open(FILE_NAME, 'w') as fp:
            print(f'write cache data to {FILE_NAME}...')
            for id in cache:
                fp.write(f'{id},{cache[id]}\n')
    except:
        pass
    
    return msg


def find_unescaped_char(s, end):
    i = 0
    result = []
    while i < len(s):
        c = s[i]
        if c == end:
            return (i, ''.join(result))
        elif c == '\\':
            if i + 1 < len(s):
                i += 1
                c = s[i]
        result.append(c)
        i += 1

    if end is None:
        return (len(s), ''.join(result))
    else:
        return (-1, None)


def find_unescaped_char_and_split(s, end):
    i = 0
    result = []
    current = []
    while i < len(s):
        c = s[i]
        if c == end:
            result.append(''.join(current))
            return (i, result)
        elif c == ',':
            result.append(''.join(current))
            current = []
        elif c == '\\':
            if i + 1 < len(s):
                i += 1
                c = s[i]
            current.append(c)
        else:
            current.append(c)
        i += 1

    if end is None:
        result.append(''.join(current))
        return (len(s), result)
    else:
        return (-1, None)


def eval_word_list(words):
    results = []
    for word in words:
        if word[0] == '%' and len(word) > 1:
            results.extend(charsets[word[1:]])
        else:
            results.append(word)
    return results


def parse_pattern(pat, default_charset=charsets['alpha']):
    parsed = []
    i = 0
    while i < len(pat):
        c = pat[i]
        if c == '\\':
            if i + 1 < len(pat):
                i += 1
                c = pat[i]
            parsed.append([c])
        elif c == '{':
            j, words = find_unescaped_char_and_split(pat[i+1:], '}')
            if j < 0:
                raise RuntimeError('cannot find close paren')
            if j > 0:
                parsed.append(eval_word_list(words))
            i += j + 1
        elif c == '[':
            j, chars_str = find_unescaped_char(pat[i+1:], ']')
            if j < 0:
                raise RuntimeError('cannot find close paren')
            if j > 0:
                parsed.append(list(chars_str))
            i += j + 1
        elif c == '?':
            parsed.append(default_charset)
        else:
            parsed.append([c])
        i += 1
    return parsed


def main(problem_id, pattern, n_rescan=0, charset='%lower', flag_list=False, flag_count=False, parallel=1):
    default_charset = eval_word_list(find_unescaped_char_and_split(charset, None)[1])

    encryptedMsg = get_encryptedMsg(problem_id)
    parsed_pattern = parse_pattern(pattern, default_charset=default_charset)

    if n_rescan == 0:
        candidates = (''.join(prod) for prod in itertools.product(*parsed_pattern))
    else:
        candidates_list = []
        rescan_indices = [i for i in range(len(parsed_pattern)) if len(parsed_pattern[i]) == 1 and len(parsed_pattern[i][0]) == 1]
        if len(rescan_indices) < n_rescan:
            raise RuntimeError('too large n_rescan')
        for indices in itertools.combinations(rescan_indices, n_rescan):
            tmp_parsed = parsed_pattern.copy()
            for i in indices:
                tmp_parsed[i] = default_charset
            candidates_list.append( (''.join(prod) for prod in itertools.product(*tmp_parsed)) )
        candidates = itertools.chain(*candidates_list)

    if flag_list or flag_count:
        count = 0
        for candidate in candidates:
            if flag_list:
                print(candidate)
            count += 1
        print(f'total: {count} candidates')
        exit(0)
    else:
        print(f'start...')

    expected = encryptedMsg[0:64]
    msg = encryptedMsg[64:].encode()

    if parallel <= 1:
        for i, candidate in enumerate(candidates):
            key = hashlib.sha256(candidate.encode()).hexdigest().encode()
            computed = hmac.new(key, msg, hashlib.sha256).hexdigest()
            if computed == expected:
                print(f'found: {candidate}')
                break
            if i != 0 and i % 1000000 == 0:
                print(f'...{i}')
    else:
        from concurrent.futures import ProcessPoolExecutor
        i = 0
        with ProcessPoolExecutor(max_workers=parallel) as executor:
            for candidate, computed in executor.map(
                lambda passphrase: (passphrase, hmac.new(hashlib.sha256(passphrase.encode()).hexdigest().encode(), msg, hashlib.sha256).hexdigest()),
                candidates, chunksize=1000):
                if computed == expected:
                    print(f'found: {candidate}')
                    break
                i += 1
                if i != 0 and i % 1000000 == 0:
                    print(f'...{i}')



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_id', help='https://satoshistreasure.xyz/?????')
    parser.add_argument('pattern', help='ex: a?c[de]{fg,hi}{%%alpha,%%number}')
    parser.add_argument('-c', '--count', dest='count', action='store_true', default=False, help='count candidates then exit')
    parser.add_argument('-l', '--list', dest='list', action='store_true', default=False, help='show candidates then exit')
    parser.add_argument('-r', '--rescan', dest='rescan', default=0, help='replace N single chars to ? by rotation. default: 0')
    parser.add_argument('-d', '--dic', '--dictionary', dest='dictionary', default=None, help='you can refer the dictionary as %%dic')
    parser.add_argument('-s', '--charset', dest='charset', default='%lower', help='default: %%lower')
    parser.add_argument('-p', '--parallel', dest='parallel', type=int, default=1, help='number of CPUs to use')
    args = parser.parse_args()
    if args.dictionary is not None:
        with open(args.dictionary, 'r') as fp:
            dictionary = [line.strip() for line in fp]
            charsets['dic'] = dictionary
    main(args.problem_id, args.pattern, n_rescan=args.rescan, charset=args.charset, flag_list=args.list, flag_count=args.count, parallel=args.parallel)
