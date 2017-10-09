from __future__ import division
import random
# import numpy
import math
import time
from inspect import isfunction # Need this to test whether something is a function!  Painful!
import re  # For handling regular expressions
import os  # For invoking operating system commands
import sys  # For checking object usage in the "debugging" code.
import types  # Also for checking object usage

# NOTE on the debugger:
# To activate, do this right inside any function/method:
# import pdb
# pdb.set_trace()
# Here, you can do self.property and see that property

def protected_div(x, y):
    if y == 0.0:
        return 0.0
    else:
        return x / y


def kdwait(self, seconds=1.0):
    time.sleep(seconds)


# Expr is a string, which may include variables.  Bindings is a list of pairs, with each pair = (variable value).
# Example usage: kd_eval("x + y",[('x',10),('y',13)])  => 23
def kd_eval(expr, bindings, scope=globals()):
    envir = {}
    for p in bindings:
        envir[p[0]] = p[1]
    return eval(expr, scope, envir)


def kd_makefunc(var_names, expression, envir=globals()):
    args = ""
    for n in var_names: args = args + "," + n
    return eval("(lambda " + args[1:] + ": " + expression + ")", envir)

# The reduce function was removed in Python 3.0, so just use this handmade version.  Same as a curry.
def kd_reduce(func,seq):
    res = seq[0]
    for item in seq[1:]:
        res = func(res,item)
    return res

def set_slot(obj, slot_name, value):
    setattr(obj, slot_name, value)


# This takes an object and a list of slot-value pairs
def set_slots(obj, pairs):
    for p in pairs:
        setattr(obj, p[0], p[1])


# This is a destructive operation: it modifies the slots
def map_slots(object, func, slot_names):
    for s in slot_names:
        setattr(object, s, func(getattr(object, s)))


def get_slot(obj, slot_name):
    return getattr(obj, slot_name)


def get_method(obj, method_name):
    return getattr(obj, method_name)  # Note:  Same as get_slot


def apply_method(obj, method_name, args=[]):
    func = get_method(obj, method_name)  # The args list should NOT include the object itself.
    return apply(func, args)


# An item = a slot or a method (that's probably going to get or set a slot, along with other operations)

def get_obj_item(obj, item_name):
    item = getattr(obj, item_name)
    if callable(item):
        return apply(item)
    else:
        return item


def set_obj_item(obj, item_name, value):
    item = getattr(obj, item_name)
    if callable(item):
        apply(item, [value])
    else:
        set_slot(obj, item_name, value)


def find_list_item(L, item, key=(lambda x: x)):
    for x in L:
        if item == key(x):
            return x


def list_position(L, pred):
    pos = 0
    for x in L:
        if pred(x): return pos
        pos += 1
    return False


# This takes a list of pair lists, ((key (items))(key (items))..) and returns the first pair that
# matches the key.

def assoc(key, L):
    for pair in L:
        if pair[0] == key:
            return pair
    return False


# This maps the func to each list and then appends all the results.  Thus, it assumes that
# each call to func produces a list.
def mapcan(func, Lists):
    res = []
    for L in Lists:
        res.extend(func(L))
    return res


def cadr_assoc(key, L):
    pair = assoc(key, L)
    if pair:
        return pair[1]
    else:
        return False


def find_list_items(L, item, key=(lambda x: x)):
    results = []
    for x in L:
        if item == key(x): results.append(x)
    return results


def find_list_satisfier(L, pred):
    for x in L:
        if pred(x): return x
    return None


def find_list_satisfiers(L, pred):
    results = []
    if L:
        for x in L:
            if pred(x): results.append(x)
    return results


def list_car(L): return L[0] if L else False


def list_cdr(L): return L[1:] if len(L) > 1 else []


def list_nth(L, n):
    if isinstance(L, list) and len(L) > n:
        return L[n]
    else:
        return False


def list_modnth(L, n):
    if isinstance(L, list) and number_p(n):
        return L[int(n) % len(L)]
    else:
        return False


def list_fracnth(L, frac):
    if isinstance(L, list) and number_p(frac):
        if frac >= 1.0:
            return L[-1]
        elif frac <= 0.0:
            return L[0]
        else:
            return L[int(frac * len(L))]
    else:
        return False


# In Python, append adds to the end of a list, but pop removes from the end as well.  So I've added
# these "list_" functions to do things the way LISP does, just to avoid confusion.

def list_push(L, item):
    L.insert(0, item)
    return L


def list_pushnew(L, item):
    if not (list_member(item, L)):
        list_push(L, item)
    return L


def list_pop(L):  return L.pop(0)  # default of python's pop op is the LAST element


def list_pushall(L, items):  L[0:0] = items  # Adds all to the front of L


def list_pushend(L, item): L.append(item)


def list_popend(L): return L.pop()


def list_pushall_end(L, items): L.extend(items)


def list_append(L1, L2): return L1 + L2


def list_cons(item, L): return [item] + L


def list_difference(L1, L2): return [x for x in L1 if not (list_member(x, L2))]


def list_to_string(L):
    s = ''
    for item in L:
        s += str(item)
    return s


def list_unique_items(L):
    items = []
    for item in L:
        list_pushnew(items, item)
    items.reverse()
    return items


def list_member(item, L):
    rem = L
    while rem and rem[0] != item:
        rem = rem[1:]  # cdr
    return rem


def list_position(item, L):
    for i in range(len(L)):
        if L[i] == item:
            return i
    return False


# This checks nested lists.
def list_rec_member(item, L):
    if item == L:
        return True
    elif isinstance(L, list):
        if len(L) > 1:
            return list_rec_member(item, list_car(L)) or list_rec_member(item, list_cdr(L))
        else:
            return list_rec_member(item, list_car(L))
    else:
        return False


# This should replace item1 by item2 anywhere in a nested list, and item1 and/or item2 can be
# a list as well.  The equality check (item == item1) does a deep (recursive) equality test, which is
# standard in Python.

def list_replace(L, item1, item2):
    def rec(L):
        if isinstance(L, list):
            for [index, item] in enumerate(L):
                if item == item1:
                    L[index] = item2
                elif isinstance(item, list):
                    rec(item)

    if L == item1:
        return item2
    else:
        rec(L)


# Recursive removal of any subtree or atom that satisfies the predicate (pred).  I had to hand code the
# iteration here to insure that ALL relevant items got deleted.  Built-in python iterators would step over
# items after a removal.

def list_remove_if(L, pred):
    def rec(L):
        z = len(L);
        i = 0
        while i < z:
            if pred(L[i]):
                L.pop(i)
                z -= 1  # Don't iterate forward, but reduce list length
            else:
                if isinstance(L[i], list):
                    rec(L[i])
                i += 1

    if isinstance(L, list): rec(L)


# Goes through any nested list and puts item2 just before (or after) each
# occurrence of item1

def list_insert_after(L, item1, item2):
    def rec(L):
        if isinstance(L, list):
            for [index, item] in enumerate(L):
                if item == item1:
                    L.insert(index + 1, item2)
                elif isinstance(item, list):
                    rec(item)

    rec(L)


# This is a little trickier than list_insert_after, since enumerate goes into an infinite loop if we are
# not careful.  Hence, the skip variable is used to insure that each occurrence of item1 is only preceded by ONE
# copy of item2.

def list_insert_before(L, item1, item2):
    def rec(L):
        skip = False
        if isinstance(L, list):
            for [index, item] in enumerate(L):
                if item == item1:
                    if skip:
                        skip = False  # But move on and ignore this occurrence of item1
                    else:
                        L.insert(index, item2)
                        skip = True  # Now we will not repeat this (ad infinitum)
                elif isinstance(item, list):
                    rec(item)

    rec(L)


## This only works on flat lists.  It finds the target and then removes a segment of length n, starting with the target.
## This does NOT side-effect the original list.

def list_remove_target_segment(L, pred, n):
    pos = list_position(L, pred)
    if pos:
        return L[0:pos] + L[pos + n:]
    else:
        return L


def boolean_true_p(x): return (isinstance(x, bool) and x)


def boolean_false_p(x): return (isinstance(x, bool) and not (x))


# This makes it easier to assign a or b to some variable z, based on the value of x.  This is named after the old
# Fortran switch function.

def switch(x, a, b):
    if x:
        return a
    else:
        return b


def forall(L, pred):
    for item in L:
        if not (pred(item)): return False
    return True


def exists(L, pred):
    for item in L:
        if pred(item): return True
    return False


def integer_p(item): return type(item) == int


def float_p(item): return type(item) == float


def number_p(item): return type(item) in [int, float]


def string_p(item): return isinstance(item, basestring)  # Covers both byte and unicode strings.


def string_explode(s):
    "Generate a list of characters (singleton strings) from a string"
    items = []
    for i in range(len(s)):
        items.append(s[i])
    return items

def strings_explode(strings):
    "Returns one huge list of all the exploded strings"
    items = []
    for s in strings:
        items.extend(string_explode(s))
    return items

def merge_strings(strings, gap=' '):
        return kd_reduce((lambda x, y: x + gap + y), strings)

def gen_freqs(items):
    " Creates a dictionary of pairs (item : frequency)"
    fc = {}
    for item in items:
        if item in fc.keys():
            fc[item] = fc[item] + 1
        else:
            fc[item] = 1
    size = len(items)
    for key in fc.keys():
        fc[key] = fc[key]/size
    return fc

def list_p(item): return type(item) == list


def number_list_p(L):
    return type(L) == list and forall(L, (lambda x: number_p(x)))


def normalize_list(elems):
    s = sum(elems)
    if s != 0:
        return [elem / s for elem in elems]
    else:
        return []


def general_sum(elems, prop_func=(lambda x: x)):
    return sum(map(prop_func, elems))


def general_avg(elems, prop_func=(lambda x: x)):
    if elems:
        return sum(map(prop_func, elems)) / len(elems)


def general_variance(elems, prop_func=(lambda x: x), avg=None):
    if not (avg): avg = general_avg(elems, prop_func=prop_func)
    if len(elems) > 1:
        sum = 0
        for elem in elems:
            sum += (prop_func(elem) - avg) ** 2
        return (sum / len(elems))
    else:
        return 0


def general_stdev(elems, prop_func=(lambda x: x), avg=None):
    return math.sqrt(general_variance(elems, prop_func=prop_func, avg=avg))


def logistic(x, k):
    return 1 / (1 + math.exp(k - x))


def n_of(count, item):
    if isfunction(item):
        return [item() for i in range(count)]
    else:
        return [item for i in range(count)]

def n_calls(count, func): return [func() for i in range(count)]

def n_strings(count,base,gap=''):
    return merge_strings(n_of(count,base),gap=gap)

def num_satisfiers(elems, predicate):
    count = 0
    for elem in elems:
        if predicate(elem): count += 1
    return count


# Find the positions of all elems that satisfy the predicate
def pos_satisfiers(elems, predicate):
    positions = []
    for i in range(len(elems)):
        if predicate(elems[i]): positions.append(i)
    return positions


# Gens a number cycle, starting at a, going (up or down) to b, and then back to a.  If size is even, b is repeated in
# the middle of the list.

def gen_cycle(a, b, size):
    mid = int(round(size / 2.0) - 1)
    dx = (b - a) / mid
    elems = []
    for i in range(mid + 1):
        elems.append(a + i * dx)
    if (mid + 1) * 2 == size:
        start = 0
    else:
        start = 1
    for j in range(start, mid + 1):
        elems.append(b - j * dx)
    return elems


def biased_coin_toss(prob=.5):
    if random.uniform(0, 1) <= prob:
        return True
    else:
        return False

def fair_coin_toss(): return biased_coin_toss(0.5)

def randab(a, b):
    return a + (b - a) * random.uniform(0, 1)


def randelem(elems):
    return elems[random.randint(0, len(elems) - 1)]


def randelems(elems, count):
    elems2 = list(elems)
    rands = []
    for i in range(min(len(elems2), count)):
        elem = randelem(elems2)
        elems2.remove(elem)
        rands.append(elem)
    return rands


# This version can have repeats
def randelems2(elems, count):
    return [randelem(elems) for i in range(count)]


def stochpick(elems, prop_func=(lambda x: x), sum=0):
    if sum == 0: sum = general_sum(elems, prop_func)
    randnum = random.uniform(0, sum)
    running_sum = 0
    for elem in elems:
        running_sum += prop_func(elem)
        if running_sum >= randnum: return elem


def stochpick_subset(elems, subset_size, prop_func=(lambda x: x)):
    items = list(elems)  # copies the elems list
    subset = []
    sum = general_sum(elems, prop_func)
    for i in range(subset_size):
        item = stochpick(items, prop_func, sum=sum)
        if item:
            sum = sum - prop_func(item)
            subset.append(item)
            items.remove(item)
    diff = subset_size - len(subset)
    if diff > 0:
        if diff < len(items):
            subset.extend(randelems(items, diff))
        else:
            subset.extend(items)
    return subset

    # The python manual says that it is faster to sort in ascending order (the default) and then


# do a reverse afterwards, as opposed to sorting by a different comparator function.

def kd_sort(elems, prop_func=(lambda x: x), dir='increase'):
    elems.sort(key=prop_func)  # default of the sort func is increasing order
    if dir == 'decrease' or dir == 'decr':
        elems.reverse()


def first_n(elems, n, prop_func=(lambda x: x), dir='decrease'):
    rev = True if dir == 'decrease' else False
    ranked = sorted(elems, key=prop_func, reverse=rev)  # This COPIES the list, while sort does not.
    return ranked[0:n]


def partition(elems, prop_func=(lambda x: x), eq_func=(lambda x, y: x == y)):
    kd_sort(elems, prop_func=prop_func)
    partition = []
    subset = False
    last_key = False
    counter = 0
    for elem in elems:
        new_key = apply(prop_func, [elem])
        if not (subset) or last_key != new_key:
            if subset: partition.append(subset)
            subset = [elem]
            last_key = new_key
        else:
            subset.append(elem)
    if subset: partition.append(subset)
    return partition


def sorted_partition(elems, elem_prop=(lambda x: x), subset_prop=(lambda ss: len(ss)), eq_func=(lambda x, y: x == y),
                     dir="decrease"):
    p = partition(elems, prop_func=elem_prop, eq_func=eq_func)
    kd_sort(p, prop_func=subset_prop, dir=dir)
    return p


# Loads in all lines of a file

def load_file_lines(fid):
    return [line.rstrip() for line in open(fid, 'r').readlines()]
    # rstrip strips the newline character.

def big_string_from_file(fid):
    return merge_strings(load_file_lines(fid))

def find_file_lines(fid, test):
    good_lines = []
    for l in load_file_lines(fid):
        if test(l): good_lines.append(l)
    return good_lines

def find_matching_file_lines(fid, target_string):
    return find_file_lines(fid, (lambda l: l.find(target_string) >= 0))

def calc_char_freqs(fid):
    "Create a dictionary with pairs (char : freq) based on the entire file"
    return gen_freqs(lowercase_chars_from_file(fid))

def lowercase_chars_from_file(fid):
    return [c.lower() for c in strings_explode(load_file_lines(fid))]

def file_dump_strings(fid,strings):
    with open(fid,'w') as f:
        for s in strings:
            f.write(s+'\n') # Add newline at end of each string

def string_to_ascii(str): return [ord(x) for x in str]
def ascii_to_string(ascii_list): return merge_strings([chr(c) for c in ascii_list], gap='')

def string_to_ascii_bits(str):
    return merge_strings([integer_to_bitstring(i,8,least_first=False) for i in string_to_ascii(str)],gap='')

def ascii_bits_to_string(bitstring):
    return merge_strings([chr(bitstring_to_integer(s,least_first=False)) for s in group(bitstring,8)],gap='')

# Count the occurrences of the target string in all active lines of code: exclude
# commented lines.

def count_active_targets(fid, target_string, comment_symbol='#'):
    count = 0
    for l in load_file_lines(fid):
        l = l.strip()
        if len(l) > 0 and l[0] != comment_symbol:
            count += l.count(target_string)
    return count


# **** MIT PRESS ************

# Code for picking out graphics-file names in my latex files.  This assumes
# that all occurrences of \includegraphics occur at the beginning of a line or
# at least that no '{' precedes it; and it assumes that no line has more than one
# occurrence.
# Commented lines are ignored.

def find_graphics_filenames(latex_fid, comment_symbol='#'):
    names = []
    lines = find_matching_file_lines(latex_fid, "\\includegraphics")
    regex = re.compile("\{\S+\}")
    for l in lines:
        if l[0] != comment_symbol:
            m = regex.search(l)
            fid = l[m.start() + 1: m.end() - 1].strip()
            fid = strip_outer_parens(strip_outer_quotes(fid))
            names.append(fid + '.pdf')
    return names


_all_chapters_ = ['evann/ch1-intro', 'evann/ch2-emergence', 'general/ch3-search', 'general/ch4-representation',
                  'evolution/ch5-evolalgs', 'neural/ch6-ann-intro', 'neural/ch7-ann-rep',
                  'evolution/ch8-ea-rep', 'evann/ch9-brainevo', 'neural/ch10-synaptune', 'neural/ch11-rl-nn',
                  'evann/ch12-evann', 'neural/ch13-infotheo', 'general/ch14-conclusion', 'evolution/ch15-ea-apx',
                  'neural/ch16-ann-apx']


def get_full_chapter_fids(): return [fid + '.tex' for fid in _all_chapters_]


# Go through a latex file and find all calls to includegraphics.  Each
# call will involve one PDF file.  Get all those file names, in order, and then
# copy them to a new directory and RENAME all files to the format:
# fig_(chapter index)_(order in file index) with padding zeros on the indices:
# e.g. fig_002_012 for the 12th figure in chapter 2. 
# base_dir is the high-level dir containing one subdir per chapter.

def mitpress_figs(latex_fid, chap_num, base_dir, base_name='fig_', index_len=3, strip=False):
    new_dir = base_dir + '/' + 'chapter' + str(chap_num)
    os.system('mkdir ' + new_dir)
    sc = str(chap_num)
    basefid = new_dir + '/' + base_name + '0' * (index_len - len(sc)) + sc + '_'
    fnames = find_graphics_filenames(latex_fid, comment_symbol='%')
    count = 1
    for fid in fnames:
        if strip: fid = strip_filepath_prefix_dots(fid)
        sc = str(count)
        newfid = basefid + '0' * (index_len - len(sc)) + sc + '.pdf'
        os.system('cp ' + fid + ' ' + newfid)
        count += 1


# Call this while in directory keithd/core/classes/ssai/book/
def mitpress_all_figs():
    os.system('mkdir all-figures')
    fids = get_full_chapter_fids()
    chapter = 1
    for fid in fids:
        mitpress_figs(fid, chapter, 'all-figures', strip=True)
        chapter += 1


def show_chapter_figure_counts():
    fids = get_full_chapter_fids()
    chapter = 1
    for fid in fids:
        count = count_active_targets(fid, "\\includegraphics", '%')
        print('Chapter ' + str(chapter) + ' Count ' + str(count) + '\n')
        chapter += 1


# **********************************************

# This loads files (typically spec files) that are written for lisp and converts them to more
# python-friendly specs by replacing hyphens (except minus signs) by underscores 
# and "?"(that are symbol suffixes) by "_p".

def load_lispy_file_lines(fid):
    return convert_lispy_strings(load_file_lines(fid))


def convert_lispy_strings(strings):
    return replace_booleans(replace_question_marks(replace_hyphens(remove_comments(strings))))


# Breaks a big string into a list of tokens = strings and numbers.  This also recognizes lists within
# the string and preserves them as sublists in the final list(s) returned.
def tokenize(str): return strings_to_lists(separate_parens(str).split(), converter=str_to_sym)


# Reads in file, tokenizes everything, and returns one big list.
def squash_file(fid):
    return kd_reduce(list_append, map(tokenize, convert_lispy_strings(load_lispy_file_lines(fid))))


# Split a list at the target item

def split_at(L, target, include=False):
    first_half = []
    while L and L[0] != target:
        first_half.append(L[0])
        L = L[1:]  # cdr
    if L:
        second_half = {True: L, False: L[1:]}[include]
        return [first_half, second_half]
    else:
        return [first_half, []]

def group(L,size):
    groups = []; lmax = len(L); loc = 0
    while loc < lmax:
        groups.append(L[loc:min(loc+size,lmax)])
        loc += size
    return groups


# The nth item returned is everything between the nth and n+1st target expression (e.g. a string)
def gather_multi_delimited_items(L, targets):
    groups = []
    rem = split_at(L, list_pop(targets))[1]
    while targets:
        pair = split_at(rem, list_pop(targets))
        groups.append(pair[0])
        rem = pair[1]
    return groups + [rem]


def gather_multi_delimited_items2(L, targets):
    groups = []
    remains = L;
    last_match = False
    while remains:
        pair = split_at_sat(remains, (lambda x: list_member(x, targets)), include=True)
        if last_match and pair[0]:
            groups.append([last_match, pair[0]])
        remains = pair[1]
        if pair[1]:
            last_match = pair[1][0]
            remains = pair[1][1:]
    return groups


def split_at_sat(L, predicate, include=False):
    first_half = []
    while L and not (apply(predicate, L[0:1])):
        first_half.append(L[0])
        L = L[1:]  # cdr
    if L:
        second_half = {True: L, False: L[1:]}[include]
        return [first_half, second_half]
    else:
        return [first_half, []]


# Detect keyword strings as those beginning with a colon (as in Lisp) and as done in ann-topology files
def keyword_p(s): return isinstance(s, str) and s[0] == ":"


def wildcard_p(s): return isinstance(s, str) and s[0] == "?"


# Here, strings is a list of strings, often the result of tokenizing a single file line
def keyword_line_p(strings): return keyword_p(strings[0])


def strip_keyword_colon(str): return str[1:]


def strip_wildcard(str): return str[1:]


# Aside from numbers or booleans, all else is just treated as a string.
# Python doesn't have true symbols (a la Lisp)

def str_to_sym(str):
    if is_integer(str):
        return int(str)
    elif is_float(str):
        return float(str)
    elif str == "false" or str == "False":
        return False
    elif str == "true" or str == "True":
        return True
    else:
        return str


def strip_sign(str):
    if str[0] == '+' or str[0] == '-':
        return str[1:]
    else:
        return str


def is_list_start(str):
    return str[0] == '(' or str[0] == '['


def is_list_end(str):
    return str[0] == ')' or str[0] == ']'


def is_integer(str):
    x = strip_sign(str)
    return x.isdigit()  # built-in python operator for detecting any string containing ONLY digits


def is_float(str):
    x = strip_sign(str)
    loc = x.find('.')
    lx = len(x)
    if loc == 0:
        return x[1:].isdigit()
    elif loc == lx - 1:
        return x[:-1].isdigit()
    elif loc > 0 and loc < lx - 1:
        return x[0:loc].isdigit() and x[loc + 1:].isdigit()
    else:
        return False


# This takes a list of strings, some of which might be list delimiters (i.e. parens), and returns another list, which can now
# include sublists.  Each individual item is also sent to the converter function.  See tokenize for an example of usage.  There
# the converter is str_to_sym (string to symbol: number or boolean).

def strings_to_lists(strings, converter=(lambda x: x)):
    items = []

    def pop_to_mark():
        val = list_pop(items)
        l = []
        while not (val == "$$$"):
            list_push(l, val)
            val = list_pop(items)
        list_push(items, l)

    for s in strings:
        if is_list_end(s):
            pop_to_mark()
        elif is_list_start(s):
            list_push(items, "$$$")
        else:
            list_push(items, converter(s))

    items.reverse()
    return items


    # Substitute underscores for hyphens, but only hyphens that come after an alphanumeric.  Those that


# come before an alphanumeric are considered minus signs and left as is.

def replace_hyphens(strings):
    return [re.sub(r'(\w+)-', r'\1_', s) for s in strings]


# This adds whitespace before and after parentheses (even if whitespace already existed there).
def separate_parens(s):
    return re.sub(r'(\(|\)|\[|\])', r' \1 ', s)


# This replaces all question marks at the end of symbols by "_p", as only the latter is an acceptable argument name in python.
# E.g., the argument 'empty?' is changed to 'empty_p'.
def replace_question_marks(strings):
    return [re.sub(r'(\w+)\?( |$)', r'\1_p\2', s) for s in strings]


# Lisp comments begin with a ";", while pythons begin with #.  So everything after either of these is ignored.
def remove_comments(strings):
    return [re.sub(r'(.*?)(;|#)+(.*$)', r'\1', s) for s in strings]


def replace_booleans(strings): return replace_ts(replace_nils(strings))


def replace_ts(strings):
    return [re.sub(r'(\b)(t|true)(\b)', r'\1True\3', s) for s in strings]


def replace_nils(strings):
    return [re.sub(r'(\b)(nil|false)(\b)', r'\1False\3', s) for s in strings]


def strip_outer_quotes(s):
    if s[0] in ["\'", "\""]: s = s[1:]
    if s[-1] in ["\'", "\""]: s = s[:-1]
    return s


def strip_outer_parens(s):
    if s[0] in ["(", "[", "{"]: s = s[1:]
    if s[-1] in [")", "]", "}"]: s = s[:-1]
    return s


# This bundles up keyword-value pairs into a dictionary, which Python can then use directly in calls to functions
# with default (keyword) arguments.

def bundle_keyword_args(arguments):
    dict = {}
    while arguments and keyword_p(arguments[0]):
        dict[strip_keyword_colon(arguments[0])] = arguments[1]
        arguments = arguments[2:]
    return dict


# This version returns a list of pairs (instead of a dictionary)
def bundle_keyword_args2(arguments):
    pairs = []
    while arguments and keyword_p(arguments[0]):
        pairs.append([strip_keyword_colon(arguments[0]), arguments[1]])
        arguments = arguments[2:]
    return pairs


# These can be used in python calls to __init__ routines.  This first option is for
# including the keywords as a dictionary object, to be used by python as the 3rd argument to apply.
# The 2nd option is for init routines that have a 'keyargs' argument, which I handle explicitly (in calls to
# set_slots(self,keyargs)).  For this option, the keyargs need to be a list of pairs.
def bundle_keyword_string(s): return bundle_keyword_args(tokenize(s))


def bundle_keyword_strings(strings): return bundle_keyword_args(mapcan(tokenize, strings))


def bundle_keyword_string2(s): return bundle_keyword_args2(tokenize(s))


def bundle_keyword_strings2(strings): return bundle_keyword_args2(mapcan(tokenize, strings))


# **** Trigonometry

def kd_atan(dx, dy):
    if dx == 0:
        return (math.pi / 2.0)
    else:
        return math.atan(dy / dx)


# ***** RUNNING AVERAGER *****

class running_averager():
    def __init__(self):
        self.reset()

    def reset(self):
        self.running_average = 0.0
        self.elem_count = 0.0

    def update(self, newval):
        self.elem_count += 1
        self.running_average = (newval + self.running_average * (self.elem_count - 1)) / self.elem_count


# A history object maintains a list of limited size.  New (recent) values are added to the front of the
# list, while old values are popped off the end of the list.

class history():
    def __init__(self, maxsize):
        self.maxsize = maxsize
        self.clear()

    def clear(self):
        self.size = 0
        self.values = []

    def add(self, val):
        self.values.insert(0, val)
        self.size += 1
        if self.size > self.maxsize:
            self.values.pop()
            self.size -= 1

    def get(self, index):
        return self.values[index] if 0 <= index < self.size else 0.0

    def window_avg(self, index, width):
        sum = 0;
        count = min(width, self.size - index)
        if count > 0:
            for i in range(count):
                sum += self.values[index + i]
            return sum / count
        else:
            return 0.0

#  ******* Bit - Integer Conversions *******
#  In all of these routines, the LEAST significant bits come first in the bit lists and bit strings.  To get
#  the most significant bits first, use the "least_first=False" option.

def bits_to_integer (bits,least_first=True):
    if least_first:
        bits2 = bits
    else:
        bits2 = bits.copy()
        bits2.reverse()
    sum = 0
    for b in range(len(bits2) - 1, -1, -1):
        sum = sum * 2 + bits2[b]
    return sum

def integer_to_bits(int, min_size=False,least_first=True):
    remains = int
    bits = []
    while remains > 0:
        bits.append(remains % 2)
        remains = remains // 2
    if min_size: # pad with zeros
        for i in range(min_size - len(bits)): bits.append(0)
    if not(least_first): bits.reverse()
    return bits

def integer_to_bitstring(int, min_size=False,least_first=True):
    return list_to_string(integer_to_bits(int,min_size,least_first=least_first))

def bitstring_to_integer (bits,least_first=True):
    return bits_to_integer([int(bs) for bs in string_explode(bits)],least_first=least_first)

# ********  Some debugging stuff

def get_refcounts():
    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr(m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount(o)
                # sort by refcount
    pairs = map(lambda x: (x[1], x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs


def print_object_counts(num=20):
    for n, c in get_refcounts()[:num]:
        print ('%10d %s' % (n, c.__name__))
