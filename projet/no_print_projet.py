# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from wrapper import *
#import test

#variable global
cpt = 0

#pour changer la variable debug utiliser
#set_debug(boolean)

def try_del(key, dico):
    try:
        del dico[key]
        #print('key {} suprimé avec succèes !'.format(key))
    except KeyError:
        pass

def delete_iddle(dico, list_key):
    for i in range(len(list_key)):
        b = list_key[i]
        if b:
            try_del(i,dico)
    

def check_color_in(j, line, color):
    """ j : int plus grandes cases, lines : array, color : int {blanc : 0, noir = 1, indeter = -1}"""
    for i in range(0, j+1):
        if line[i] == color:
            return True
    return False

def T(j, l, S):
    if l == -1:
        return True
    sl = S[l]
    if (j == sl - 1):
        #si on considere le dernier element de la serie.
        if l == 0:
            return True
        return False
    if ( j > (sl - 1)):
        return (T(j-sl-1, l-1,S) or T(j-1, l, S))


def possible_block(j, l, line):
    for i in range(0,l):
        if line[j-i] == 0:
            return False
        if j - i < 0:
            return False
    #dernier car
    if line[j - i - 1] == 1:
        return False
    return True

#il faut utiliser la memoisation

def T2(j, l, S, line,dico):
    key = (j, l) + tuple(line)
    if key in dico:
        return dico[key]
    if j < 0 and l >= 0:
        dico[key] = False
        return False
    if j < 0 and l < 0:
        dico[key] = True
        return True   
    if l == -1:
        if line[j] == 1:
            dico[key] = False
            return False
        if j == 0:
            dico[key] = True
            return True
        dico[key] = T2(j-1,l,S,line[:-1],dico)
        return dico[key]
    sl = S[l]
    if sl == 0:
        b =  check_color_in(j, line, 1)
        dico[key] = not(b)
        return not(b)
    #il faut verifier que chaque case n'est pas noir
    if (j == sl - 1):
        if l == 0 and not(check_color_in(j, line, 0)):
            dico[key] = True
            return True
        
        dico[key] = False
        return False
    if (j>(sl - 1)):
        #cas noir
        if line[j] == 1:
            if not(possible_block(j, sl, line)):
                dico[key] = False
                return False
            dico[key] =  T2(j-sl-1, l-1,S, line[:j-sl],dico)
            return dico[key]
        #cas blanc
        if line[j] == 0:
            dico[key] =  T2(j-1, l, S,line[:-1],dico)
            return dico[key]
        #cas non determiner
        #Quand on a pas de bloc forcement vrai.... du coup on peut toujours placer un bloc sur une case indeterminer
        if not(possible_block(j, sl, line)):
            dico[key] = T2(j-1, l, S,line[:-1],dico)
            return dico[key]
           
        b1 = T2(j-sl-1, l-1,S, line[:j-sl],dico)
        b2 = T2(j-1, l, S,line[:-1],dico)
        dico[key] = b1 or b2
        return dico[key]
#        return b1 or b2


def color_case(i, S, vecteur,dico):
    if vecteur[i] != -1:
        #cas ou la case est deja coloré
        return True
    v = np.copy(vecteur)
    #black
    v[i] = 1
    black = T2(len(v)-1,len(S)-1,S,v,dico)
    #white
    v[i] = 0
    white = T2(len(v)-1,len(S)-1,S,v,dico)
    if not(black) and not(white):
        #la grille n'a pas de solution
        print("il n'y a pas de solution possible pour : i = {}, S = {}, vecteur = {}".format(i,S,vecteur))
        return False
    if black and white:
        #on ne peut rien affirmer
        return None
    if black:
        #on colorie le vecteur en noir
        vecteur[i] = 1
        return i
    vecteur[i] = 0
    return i

@timer
def coloration_longue(A, lines, col):
    N, M = A.shape
    L = set([i for i in range(N)])
    C = set([i for i in range(M)])
    lineDico = dict()
    colDico = dict()
    cpt = 0
    while L != set() or C != set():
        toSee = [True for j in range(M)]
        for i in L:
            complete = True
            li = lines[i]
            #print('i :', i)
            linecolor = A[i]
            if i not in lineDico:
                lineDico[i] = dict()
            for j in range(M):
                new = color_case(j, li, linecolor,lineDico[i])
                if new is False:
                    return False
                if new is not None and new is not True:
                    complete = False
                    C.add(new)
                if new is None:
                    complete = False
                    toSee[j] = False
            #Si la ligne est complete, on la supprime du dictionnaire
            if complete:
                #print('suppression de la ligne : ' , i)
                del lineDico[i]
        delete_iddle(colDico, toSee)
        L = set()
        toSee =[True for i in range(N)]
        for j in C:
            cj = col[j]
            colcolor = A[:,j]
            complete = True
            if j not in colDico:
                colDico[j] = dict()
            
            for i in range(N):
                new = color_case(i, cj, colcolor,colDico[j])
                if new is False:
                    return False
                if new is not None and new is not True:
                    L.add(new)
                    complete = False
                if new is None:
                    #on ne peut toujours pas determiner la case
                    complete = False
                    toSee[i] = False
            #suppression de la colone du dictionnaire si complete
            if complete:
                #print('supression de la colonne : ', j)
                del colDico[j]
        delete_iddle(lineDico, toSee)
        C = set()
        cpt += 1
    return A

#---------------------------------------------------------
    
@timer
def coloration(A, lines, col):
    N, M = A.shape
    L = set([i for i in range(N)])
    C = set([i for i in range(M)])
    lineDico = dict()
    colDico = dict()
    cpt = 0
    while L != set() or C != set():
        for i in L:
            complete = True
            li = lines[i]
            if i not in lineDico:
                lineDico[i] = dict()
            linecolor = A[i]
            for j in range(M):
                new = color_case(j, li, linecolor,lineDico[i])
                if new is False:
                    return False
                if new is not None and new is not True:
                    C.add(new)
        L = set()
        for j in C:
            cj = col[j]
            colcolor = A[:,j]
            if j not in colDico:
                colDico[j] = dict()
            for i in range(N):
                new = color_case(i, cj, colcolor,colDico[j])
                if new is False:
                    return False
                if new is not None and new is not True:
                    L.add(new)
        C = set()
        cpt += 1
    return A
                
                
    
def read_file(fname):
    f = open(fname,'r')
    b = False
    l = []
    col = []
    for line in f:
        split = line.split()
        if len(split) != 0 and split[0] == "#":
            b = True
        else:
            split = line.split()
            #element vide:
            if len(split) == 0:
                split = [0]
            else:
                split = [int(i) for i in split]
            if not(b):
                l.append(split)
            else:
                col.append(split)
    f.close()
    d1 = len(l)
    d2 = len(col)
    Mat = np.zeros((d1,d2)) - np.ones((d1,d2))
    return l, col, Mat

def draw(Matrice):
    plt.imshow(Matrice, cmap='binary', interpolation='nearest')
    plt.colorbar()
    plt.show()
    

if __name__ == "__main__":
    #l'instance 4 ne marche pas avec ma memoisation alors qu'elle marche sans
    lines, col ,Mat = read_file('instances/8.txt')
    A = coloration_longue(Mat, lines, col)
    #print('A : ', A)
    draw(A)
#plt.show()
