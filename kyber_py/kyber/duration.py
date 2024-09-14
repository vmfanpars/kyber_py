from time import time

def keygenTime(kyber, n):
    tt = []
    from tqdm import tqdm
    for i in tqdm(range(n)):
        tic = time()
        kyber._cpapke_keygen()
        toc = time()
        tt.append((toc-tic)*1000)   # for convert from second to milisecond
    tt = format((sum(tt)/len(tt)),'.3f')
    return tt

def encapsTime(kyber, pk, n):
    tt = []
    from tqdm import tqdm
    for i in tqdm(range(n)):
        tic = time()
        kyber.encaps(pk)
        toc = time()
        tt.append((toc-tic)*1000)
    tt = format((sum(tt)/len(tt)),'.3f')
    return tt

def decapsTime(kyber, sk, c, n):
    tt = []
    from tqdm import tqdm
    for i in tqdm(range(n)):
        tic = time()
        kyber.decaps(sk,c)
        toc = time()
        tt.append((toc-tic)*1000)
    tt = format((sum(tt)/len(tt)),'.3f')
    return tt