#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randint
import collections, re
import copy
import sys
import itertools
import  time
import string
import codecs

def text_words(text):
    return re.findall('[a-z|éüöñğşç\'|-]+', text.lower())

def line_words(text):
    return text.split('\n')

def train(features):
    model = collections.defaultdict(lambda: 1) # For smoothing
    for f in features:
        model[f.decode('utf-8')] += 1
    return model

#NWORDS = train(words(file('../ug_kelime_ambar/uniq_merge.txt').read()))
text = file('data/udict.txt').read() # Todo: we may have problem in dict
#NWORDS = train(text_words(text))
NWORDS = train(line_words(text))

char_map = collections.defaultdict(lambda: None)
char_map.update( {
            # Multi cases, which will merge(actually override) some rules above
            # Characters in value should be single character
            u'u': [u'u', u'ö', u'ü'],
            u'o': [u'o', u'ö', u'ü'],
            u'v': [u'v', u'ö', u'ü'],
            u'e': [u'e', u'é', u'i'],
            u'a': [u'a', u'e'],
            u'g': [u'g', u'ñ', u'ğ'],
            u'h': [u'h', u'x', u'ğ'],
            u'q': [u'q', u'ç'],
            u'x': [u'x', u'ş'],
            u'y': [u'y', u'h', u'j'],
            u'ng': [u'ñ'],
            u'sh': [u'ş'],
            u'gh': [u'ğ'],
            u'ch': [u'ç'],
            u'zh': [u'j'],
            u'k': [u'k', u'q'],
            u'i': [u'i', u'é'],
            u'ë': [u'é'],
            u'z': [u'z', u'j'],
            u'j': [u'j', u'c'],
            u'n': [u'n', u'ñ'],
            u'w': [u'v']
    # Todo: maybe this list is not complete
            })

re_char_map = collections.defaultdict(lambda: None)
re_char_map.update( {
            # Multi cases, which will merge(actually override) some rules above
            u'ü': [u'ü', u'u', u'o', u'v'],
            u'ö': [u'ö', u'u', u'o', u'v'],
            u'é': [u'é', u'e', u'i', u'ë'],
            u'ñ': [u'ñ', u'n', u'ng', u'g'],
            u'ğ': [u'ğ', u'g', u'gh', u'h'],
            u'ş': [u'ş', u'x', u'sh'],
            u'ç': [u'ç', u'q', u'ch'],
            u'j': [u'j', u'zh', u'z', u'y'],
            u'e': [u'e', u'a'],
            u'q': [u'q', u'k'],
            u'i': [u'i', u'e'],
            u'x': [u'x', u'h'],
            u'h': [u'h', u'y'],
            u'v': [u'v', u'w'],
            u'j': [u'j', u'zh', u'y', u'z'],
            u'c': [u'c', u'j'],
            })

# Ensure two maps are complete inverse of each other
def check_maps(map1, map2):
    for key, value in map1.iteritems():
        if value == None:
            value = [key]
        for item in value:
            #print key, item
            list = map2[item]
            if list == None:
                list = [item]
            if key in list:
                continue
            else:
                print key, item
                return False
    return True

# This function is used for simulating user's hehaviorus of using characters
# where a user in most cases have fixed selecting behavior
# By defualt map is re_char_map
def sim_user_bhv_normal(map, num):
    maps = []
    for i in range(num):
        #print i
        new_map = copy.deepcopy(map)
        for key in new_map:
            if new_map[key] == None:
                new_map[key] = key
            else:
                llen = len(new_map[key])
                keep_pos = randint(0, llen - 1)
                #print new_map[key]
                temp = new_map[key][keep_pos]
                del new_map[key][:]
                new_map[key] = temp
            #print new_map[key]
            #print '----------------------'
        maps.append(new_map)
    return maps

# This function is used for simulating user's hehaviorus of using characters
# which simulate some crazy user who choose characters randomly, no fixed rule
# By defualt map is re_char_map
# Todo: we should change this crazy mode
def sim_user_bhv_crazy(map, num):
    maps = []
    for i in range(num):
        #print i
        new_map = copy.deepcopy(map)
        for key in new_map:
            llen = len(new_map[key])
            keep_pos = randint(0, llen - 1)
            #print new_map[key]
            temp = new_map[key][keep_pos]
            del new_map[key][:]
            new_map[key] = temp
            #print new_map[key]
            #print '----------------------'
        maps.append(new_map)
    return maps

# Simulate how user miss using characters
def sim_err(pstr, map):
    new_pstr = ''
    for pchar in pstr:
        pl = map[pchar]
        if pl == None:
            new_pstr += pchar
        else:
            #print (len(pl) - 1),  pl[randint(0, len(pl)-1)]
            #new_pstr = new_pstr.join(pl[randint(0, len(pl)-1)])
            new_pstr += pl[randint(0, len(pl)-1)]
            #print new_pstr

        #print randint(0, len(pl)-1)
        #new_pstr.join(pl[randint(0, len(pl)-1)])
    #print new_pstr
    return new_pstr

# Create all cases in which one is the user really want to write
# Here we use string
def rep_set(pstr):
    com_set = char_com(pstr)
    org = com_set[-1]
    del com_set[-1]
    print 'The number of combination set: ', len(com_set)
    all_ver = []
    map = {}
    start_time = time.time()
    for iset in com_set:
        new_pstr = copy.deepcopy(pstr)
        map.update(zip(org, iset))
        new_map = {ord(k): ord(v[0]) for k, v in map.items()} # Todo: I should use v instead of v[0]
        new_pstr = new_pstr.translate(new_map)
        all_ver.append(new_pstr)
    print("--- new set generation time: %s seconds ---" % (time.time() - start_time))
    return all_ver

# Char gradient part
# # Todo: If you don't use this function, pls del. it.
# def spe_char_rep(pstr, ff , tt):
#    return  pstr.replace(ff, '#' + tt)

# Todo: character gradient descent is very simple
def char_grad(pstr, map):
    cr = correct_ratio(pstr.split())
    print 'Original correct ratio: %f' % cr
    plist = list(pstr)
    uclist = list(set(plist)) # unique char list
    flag = len(pstr) * [False]
    # Todo : we can do some random here, for restarting the starting point
    for key in map.keys():
        if key not in uclist:
            continue
        mlist = map[key]
        if mlist == None:
            continue
        for rc in mlist:
            if rc == key:
                continue
            print key, rc
            new_plist = copy.deepcopy(plist)
            new_flag = copy.deepcopy(flag)
            for ind, char in enumerate(new_plist):
                if new_flag[ind] == False and key == char:
                    new_plist[ind] = rc
                    new_flag[ind] = True
            new_pstr = "".join(new_plist)
            #print ': ' + new_pstr
            new_cr = correct_ratio(new_pstr.split())
            print 'New generated correct ratio: %f' % new_cr
            if new_cr >= cr:
                print 'Yes, I am big'
                plist = new_plist
                flag = new_flag
                cr = new_cr
        print 'Current correct ratio is: %f' % cr
    print '-'*10
    print 'Final correct ratio is: %f' % cr
    #do some calculation
    return  "".join(plist)

# Todo: we should check this place, it produce too much case
def char_com(pstr):
    single_char_list = list(set(pstr))
    temp_ll = []
    #temp_ll.append(single_char_list)
    for char in single_char_list:
        cand = char_map[char]
        if cand == None:
            cand = char
        temp_ll.append(cand)
    rst = list(itertools.product(*temp_ll));
    rst.append(single_char_list)
    return rst
    #print char_com

# Todo: maybe I did not use this function
def rep_char(words, ff, tt):
    for word in words:
        word.replace(ff, tt)
    return words

# Replace double characters
def pre_process(pstr):
    # Replace sh, gh, ch, zh, ng
    mlist = [('sh', u'ş'), ('gh', u'ğ'), ('ch', u'ç'), ('zh', u'j'), ('ng', u'ñ')]
    for i in mlist:
        #print i
        #print i[0], i[1]
        pstr = pstr.replace(i[0], i[1])
    return pstr

#### Evaluation Functions ####
# How many words in text are correct according to dictionary
def correct_ratio(words):
    wdslen = len(words)
    count = 0
    #print NWORDS['yaxşi']
    for word in words:
        #print word, NWORDS[word] # Todo: we have bug here
        if NWORDS[word] > 1:
            count += 1
    return float(count)/wdslen

# How many words in text are same as original text
def eval(pstr1, pstr2):
    words1 = pstr1.split(' ')
    words2 = pstr2.split(' ')
    #all_len = max(len(words1), len(words2))
    if len(words1) != len(words2):
        return 0 # Size is different
    count = 0
    for word1, word2 in zip(words1, words2):
        if (word1 == word2):
            count += 1
    #print count
    return float(count)/len(words1)

def map_hard_level(map):
    counter=collections.Counter(map.values())
    temp = counter.values()
    return float(sum(temp))/len(temp)


########### Test creation ################
# Create test case
# dir:
# str:
# map:
def get_orginal_data(dir = '', str = '', map = None):
    if str == '' and dir == '':
        print 'No valid input'
        return None
    elif str != '' and dir != '':
        print 'Multiple valid inputs'
        return None
    elif str != '' and dir == '':
        pstr = str
    elif str == '' and dir != '':
        ifile = codecs.open(dir, 'r', encoding='utf-8')
        pstr = ifile.read()
        pstr = pstr.replace(u'\ufeff', '')
    else:
        print 'Unexpected case'
        return
    return pstr

# Get test data
def create_test_data(pstr):
    # Start
    pflag = True
    #pflag = False
    map = sim_user_bhv_normal(re_char_map, 1)
    print 'Hard level: ', map_hard_level(map[0])
    if pflag:
        print 'Original text: %s' % pstr
    list = pstr.split()
    cr = correct_ratio(pstr.split())
    print 'Original text correct ratio: %f' % cr
    new_pstr = sim_err(pstr, map[0])
    if pflag:
        print 'Before DC2SC preprocess: %s' % new_pstr # DC2SC: double character to single character
    new_pstr = pre_process(sim_err(pstr, map[0]))
    if pflag:
        print 'After DC2SC preprocess:  %s' % new_pstr
    print "Initial similar ratio: ", eval(new_pstr, pstr)
    print "Initial correct ratio: ", correct_ratio(new_pstr.split())
    return new_pstr

########### Test part ####################
# todo: merge two cases

def test1(pstr, fpstr):
    pflag = True
    rl  = [] # correct ratio
    new_pstr_list = rep_set(fpstr)
    # check with dictionary
    start_time = time.time()
    for i in new_pstr_list:
        cr = correct_ratio(i.split())
        #print i, cr
        rl.append(cr)
    print("--- correct ratio testing cost %s seconds ---" % (time.time() - start_time))
    # Find the biggest one
    max_v = max(rl)
    print 'the correct ratio according to dict %f' % max_v
    max_list = [i for i, j in enumerate(rl) if j == max_v]
    for i in max_list:
        if pflag:
            print new_pstr_list[i]
            print pstr
        print 'After correction the similarity with original: %f' % (eval(new_pstr_list[i], pstr))
        print '-'*10
    #Todo: here we will implement Ngram-method
    #print len(rl)
    #print rl
    # print new_pstr
    #sys.exit()

# char grad
def test2(new_pstr):
    pflag = True
    pflag = False
    fpstr = char_grad(new_pstr, char_map)
    print 'After correction the similarity with original: %f' % (eval(fpstr, pstr))
    if pflag:
        print 'Final output:'
        print fpstr
    #Todo: here we will implement Ngram-method
    #print len(rl)
    #print rl
    # print new_pstr
    #sys.exit()

### RUN ###

# def translate_non_alphanumerics(to_translate, translate_to=u'_'):
#     not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
#     translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
#     return to_translate.translate(translate_table)
#
# table = maketrans(, )

#print spe_char_rep('osman', 's' , 't')
#pstr = create_test_data(dir = 'data/test_data/test2_tug.txt')
pstr = '' # original
fpstr = '' # false
pstr = get_orginal_data(dir = 'data/test.txt')
fpstr = create_test_data(pstr)
# test with files
print '-' * 50
print '[info] checking list 1: ' ,check_maps(char_map, re_char_map)
print '[info] checking list 2: ' ,check_maps(re_char_map, char_map)
print '=' * 50
print 'Character brute-force'
test1(pstr, fpstr)
sys.exit()
print '='*50
print 'Character gradient descent:'
test2(pstr)