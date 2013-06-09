#coding=utf8
import difflib
from abc import ABCMeta, abstractmethod

def levenshtein(s1, s2):
    l1 = len(s1)
    l2 = len(s2)

    matrix = [range(l1 + 1)] * (l2 + 1)
    for zz in range(l2 + 1):
        matrix[zz] = range(zz,zz + l1 + 1)
    for zz in range(0,l2):
        for sz in range(0,l1):
            if s1[sz] == s2[zz]:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
            else:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
    return float(matrix[l2][l1])

def weight(s, i):
    m = len(s) / 2.0
    w_mid = 100.0 / float(len(s))
    w_inc = w_mid ** 2
    dist = abs(m - i)
    if i <= m:
        return w_mid + dist * w_inc
    else:
        return w_mid - dist * w_inc

def levenshtein2(s1, s2):
    l1 = len(s1)
    l2 = len(s2)

    matrix = [range(l2 + 1)] * (l1 + 1)

    for i in range (l1 + 1):
        matrix[i][0] = i

    for j in range (l2 + 1):
        matrix[0][j] = j


    for i in range(0,l1):
        for j in range(0,l2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            matrix[i][j] = min(
                matrix[i-1][j] + 1, matrix[i][j-1] + 1, matrix[i-1][j-1] + cost)
            matrix[i][j] *= weight(s1, i)
    return matrix[l1][l2]

def mydiff(s1, s2):
    matcher = difflib.SequenceMatcher(None, s1, s2)

    count = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'delete':
            count += 1
            #print 'Remove %s from positions [%d:%d]' % (s1[i1:i2], i1, i2)
            #del s1[i1:i2]

        elif tag == 'equal':
            count -= 1
            #print 'The sections [%d:%d] of s1 and [%d:%d] of s2 are the same' % (
            #    i1, i2, j1, j2)

        elif tag == 'insert':
            count += 1
            #print 'Insert %s from [%d:%d] of s2 into s1 at %d' % (
            #    s2[j1:j2], j1, j2, i1)
            #s1[i1:i2] = s2[j1:j2]

        elif tag == 'replace':
            count += 1
            #print 'Replace %s from [%d:%d] of s1 with %s from [%d:%d] of s2' % (
            #    s1[i1:i2], i1, i2, s2[j1:j2], j1, j2)
            #s1[i1:i2] = s2[j1:j2]
    return count
    return float(len(s2))/float(count)

class Analyzer():
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def _simimilarity_dicts(self, matrix1, matrix2):
        if len(matrix1) == 0 and len(matrix2) == 0:
            return 1.0
        sumary = 0.0
        factor = 0.0
        keys = {}.fromkeys(matrix1.keys(), matrix2.keys()).keys()
        for k in keys:
            f1 = matrix1[k] if matrix1.has_key(k) else 0.0
            f2 = matrix2[k] if matrix2.has_key(k) else 0.0
            sumary += f1 * f2
            factor += max(f1, f2) ** 2
        return sumary / factor if factor > 0 else 0

    def _simimilarity_lists(self, seq1, seq2):
        lev = float(levenshtein(seq1, seq2))
        p = 1.0 / max(len(seq1), len(seq2))
        sim = 1 if lev == 0.0 else 1 - lev * p

        return sim

    @abstractmethod
    def sim_functions(self, func1, func2):
        """Определение меры схожести функций"""

    @abstractmethod
    def sim_programs(self, prog1, prog2):
        """Определение меры схожести программ"""
