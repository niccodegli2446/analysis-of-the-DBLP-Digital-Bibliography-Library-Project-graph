import networkx as nx
import time
import pandas as pd
import numpy as np
import random
import math
import gc

inizio=time.time()

def graph_fill(file_name, author_var_name='author', title_var_name='title',
               stop=(False,None), K_sketch=512, Seed_sketch=1324):
    
    graph=nx.Graph()
    df=open(file_name,'r')
    header=df.readline()
    header=header.strip().split(';')

    author_index=header.index(author_var_name)
    title_index=header.index(title_var_name)
    year_index=header.index('year')

    row_count=0

    authorD={}
    pubblicationD={}
    next_id=0
    authors_sketch=K_Min(k=K_sketch, seed=Seed_sketch)
    
    for line in df:
        values = line.split(';')

        max_required_index=max(author_index, title_index, year_index)
        if len(values)<=max_required_index:
            continue
        
        if values[author_index]=='' or values[title_index]=='':
            continue

        try:
            year_val = int(values[year_index]) 
        except (ValueError, TypeError):
            continue

        if stop[0]==True:
            if row_count==stop[1]:
                break
        
        authors=values[author_index].split('|')
        pubblication=values[title_index]
        year=year_val
        
        if pubblication not in pubblicationD:
            pubblicationD[pubblication]=next_id
            next_id+=1
            graph.add_node(pubblicationD[pubblication], title=pubblication, year=year)
        
        for author in authors:
            
            if author not in authorD:
                authorD[author]=next_id
                authors_sketch.update(author)
                next_id+=1
                graph.add_node(authorD[author], name=author)
            
            graph.add_edge(authorD[author],pubblicationD[pubblication])
   
        row_count+=1
              
    df.close()
    return authorD, authors_sketch, graph

#QUESTION 1: B. Who is the author who did the largest number of papers? Report his/her name

def max_autore(author_diz, graph, anno):
    massimo=0
    
    for author_name in author_diz.keys():
        tot=0
        id_author=author_diz.get(author_name)
        
        if id_author==None or id_author not in graph:
            continue

        for paper in graph.neighbors(id_author):
            if graph.nodes[paper].get('year',0)<= anno:
                tot+=1
                    
        if tot>massimo:
            massimo=tot
            autore_massimo=author_name
                
    if massimo==0 or autore_massimo is None:
        return None
                
    return (autore_massimo, massimo)
    #return autore_massimo

#QUESTION 2: implement a class using (i). K-min (both size and jaccard estimation formulas in the slides)

class K_Min:
    def __init__(self, k, seed=0):
        self.k=k
        self.seed=seed
        self.hashes=[1.0]*k  

    def simple_hash(self, x, currentseed):
        m=2**32
        h=currentseed
        
        for c in x:
            h=(31*h+ord(c))%m
            
        return h/m

    def update(self, element):
        for i in range(self.k):
            ri=self.simple_hash(element, self.seed+i)
            
            if ri<self.hashes[i]:
                self.hashes[i]=ri
                
    def union(self, sketch_B, k=None):
        if not k:
            k=self.k
            
        union_sketch=[]
        for i in range(k):
            if self.hahshes[i]<sketch_B.hashes[i]:
                union_sketch.append(self.hahshes[i])
            else:
                union_sketch.append(sketch_B.hashes[i])

        return union_sketch
    
    def estimate_size(self, k=None):
        if not k:
            k=self.k
            
        somma_sub_sketch = sum(self.hashes[i] for i in range(k))
        
        if somma_sub_sketch==k: 
            return 0
        
        return (k/somma_sub_sketch)-1
    
    def estimate_jaccard(self, sketch_B, k=None):
        if not k:
            k=self.k
        
        count=0
        for i in range(k):
            if self.hashes[i]==sketch_B.hashes[i]:
                count+=1
            
        return count/k

#QUESTION 4: Approximate the average distance

def average_distance(Graph,anno,author_diz, alpha=0.08, epsilon=0.1):

    nodi_selezionati=set()
    for nodo in author_diz.values():
        flag=False
        for paper in Graph.neighbors(nodo):
            if Graph.nodes[paper].get('year',0)<=anno:
                flag=True
                nodi_selezionati.add(paper)
        if flag:
            nodi_selezionati.add(nodo)
            
    if not nodi_selezionati:
        return 0, 0, 0

    subgraph=Graph.subgraph(nodi_selezionati)
    lcc_nodi=max(nx.connected_components(subgraph), key=len)
    del subgraph
    sub_sub_graph=Graph.subgraph(lcc_nodi)
    del lcc_nodi
    n=sub_sub_graph.number_of_nodes()
    
    k=int((alpha/2)*(epsilon**(-2))*math.log(n))
    if k>n:
        k=n
        
    sample_nodes=random.sample(list(sub_sub_graph.nodes),k)
    tot_dist=0
    num_nodes=0
    
    for i in sample_nodes:
        dist=nx.single_source_shortest_path_length(sub_sub_graph, i).values()
        tot_dist+=sum(dist)
        num_nodes+=(len(dist) - 1)

    if num_nodes==0:
        return 0, k, n
    
    #distanza media, numero bfs, numero nodi del sottografo
    return round(tot_dist/num_nodes,3), k, n


##### MAIN #####
print('\n')
names_rows=['book', 'article', 'incollection','inproceedings', 'mastersthesis', 'phdthesis', 'proceedings']
names_columns=[1960, 1970, 1980, 1990, 2000, 2010, 2020, 2023]
mat_Q1=pd.DataFrame(None, index=names_rows, columns=names_columns, dtype=object)
mat_Q2=pd.DataFrame(None, index=names_rows, columns=names_columns, dtype=object)
mat_authors_size=pd.DataFrame(None, index=names_rows, columns=['stima k=512','errore %','stima k=256','errore %',
                                                               'stima k=128','errore %','stima k=64','errore %','realtà'], dtype=object)

authors_sketch_tot={}
authors_size={}

stop=True
nrow=1000

# Book Graph
autori_dict, sketch, Graph = graph_fill('out-dblp_book.csv', stop=(stop, nrow))
q1_ans = [max_autore(autori_dict, Graph, anni) for anni in names_columns]
q2_ans = [average_distance(Graph, anni, autori_dict) for anni in names_columns]
authors_sketch_tot['book']=sketch
authors_size['book']=len(autori_dict)
mat_Q1.loc['book']=q1_ans
mat_Q2.loc['book']=q2_ans
book=time.time()
print(f"TEMPO PARZIALE DI ESECUZIONE book: {(book - inizio) / 60:.2f} minuti")
del Graph
del autori_dict
del sketch
del q1_ans
del q2_ans
gc.collect()

# Article Graph
autori_dict, sketch, Graph = graph_fill('out-dblp_article.csv', stop=(stop, nrow))
q1_ans = [max_autore(autori_dict, Graph, anni) for anni in names_columns]
q2_ans = [average_distance(Graph, anni, autori_dict) for anni in names_columns]
authors_sketch_tot['article']=sketch
authors_size['article']=len(autori_dict)
mat_Q1.loc['article']=q1_ans
mat_Q2.loc['article']=q2_ans
article=time.time()
print(f"TEMPO PARZIALE DI ESECUZIONE article: {(article - book) / 60:.2f} minuti")
del Graph
del autori_dict
del sketch
del q1_ans
del q2_ans
gc.collect()

# Incollection Graph
autori_dict, sketch, Graph = graph_fill('out-dblp_incollection.csv', stop=(stop, nrow))
q1_ans = [max_autore(autori_dict, Graph, anni) for anni in names_columns]
q2_ans = [average_distance(Graph, anni, autori_dict) for anni in names_columns]
authors_sketch_tot['incollection']=sketch
authors_size['incollection']=len(autori_dict)
mat_Q1.loc['incollection']=q1_ans
mat_Q2.loc['incollection']=q2_ans
incollection=time.time()
print(f"TEMPO PARZIALE DI ESECUZIONE incollection: {(incollection - article) / 60:.2f} minuti")
del Graph
del autori_dict
del sketch
del q1_ans
del q2_ans
gc.collect()

# Inproceedings Graph
autori_dict, sketch, Graph = graph_fill('out-dblp_inproceedings.csv', stop=(stop, nrow))
q1_ans = [max_autore(autori_dict, Graph, anni) for anni in names_columns]
q2_ans = [average_distance(Graph, anni, autori_dict) for anni in names_columns]
authors_sketch_tot['inproceedings']=sketch
authors_size['inproceedings']=len(autori_dict)
mat_Q1.loc['inproceedings']=q1_ans
mat_Q2.loc['inproceedings']=q2_ans
inproceedings=time.time()
print(f"TEMPO PARZIALE DI ESECUZIONE inproceedings: {(inproceedings - incollection) / 60:.2f} minuti")
del Graph
del autori_dict
del sketch
del q1_ans
del q2_ans
gc.collect()

# Mastersthesis Graph
autori_dict, sketch, Graph = graph_fill('out-dblp_mastersthesis.csv', stop=(stop, nrow))
q1_ans = [max_autore(autori_dict, Graph, anni) for anni in names_columns]
q2_ans = [average_distance(Graph, anni, autori_dict) for anni in names_columns]
authors_sketch_tot['mastersthesis']=sketch
authors_size['mastersthesis']=len(autori_dict)
mat_Q1.loc['mastersthesis']=q1_ans
mat_Q2.loc['mastersthesis']=q2_ans
mastersthesis=time.time()
print(f"TEMPO PARZIALE DI ESECUZIONE mastersthesis: {(mastersthesis - inproceedings) / 60:.2f} minuti")
del Graph
del autori_dict
del sketch
del q1_ans
del q2_ans
gc.collect()

# Phdthesis Graph
autori_dict, sketch, Graph = graph_fill('out-dblp_phdthesis.csv', stop=(stop, nrow))
q1_ans = [max_autore(autori_dict, Graph, anni) for anni in names_columns]
q2_ans = [average_distance(Graph, anni, autori_dict) for anni in names_columns]
authors_sketch_tot['phdthesis']=sketch
authors_size['phdthesis']=len(autori_dict)
mat_Q1.loc['phdthesis']=q1_ans
mat_Q2.loc['phdthesis']=q2_ans
phdthesis=time.time()
print(f"TEMPO PARZIALE DI ESECUZIONE phdthesis: {(phdthesis - mastersthesis) / 60:.2f} minuti")
del Graph
del autori_dict
del sketch
del q1_ans
del q2_ans
gc.collect()

# Proceedings Graph
autori_dict, sketch, Graph = graph_fill('out-dblp_proceedings.csv', author_var_name='editor', stop=(stop, nrow))
q1_ans = [max_autore(autori_dict, Graph, anni) for anni in names_columns]
q2_ans = [average_distance(Graph, anni, autori_dict) for anni in names_columns]
authors_sketch_tot['proceedings']=sketch
authors_size['proceedings']=len(autori_dict)
mat_Q1.loc['proceedings']=q1_ans
mat_Q2.loc['proceedings']=q2_ans
proceedings=time.time()
print(f"TEMPO PARZIALE DI ESECUZIONE proceedings: {(proceedings - phdthesis) / 60:.2f} minuti")
del Graph
del autori_dict
del sketch
del q1_ans
del q2_ans
gc.collect()


#QUESTION 3: Let S be {article,book,incollection,inproceedings,mastersthesis,phdthesis,proceedings}.
#Use the class implemented in QUESTION 2 to I. Estimate the number of distinct authors for each x in S.
#For each pair x,y with x,y in S, estimate the Jaccard coefficient between the set of authors of x and y.

def jaccard_estimation_k(k):
    mat_authors_jac_est=pd.DataFrame(1.0, index=names_rows, columns=names_rows)
    mat_authors_jac_est=pd.DataFrame(np.triu(mat_authors_jac_est), index=names_rows, columns=names_rows)

    for i in authors_sketch_tot.keys():
        for j in authors_sketch_tot.keys():
            if i==j or mat_authors_jac_est.at[i, j]==0:
                continue
            else:
                jac_est=authors_sketch_tot[i].estimate_jaccard(authors_sketch_tot[j],k)
                mat_authors_jac_est.at[i, j]=jac_est
                mat_authors_jac_est.at[j, i]=jac_est

    return mat_authors_jac_est

for name in authors_sketch_tot.keys():
    realta=authors_size.get(name)
    size_k512=int(authors_sketch_tot.get(name).estimate_size(k=512))
    size_k256=int(authors_sketch_tot.get(name).estimate_size(k=256))
    size_k128=int(authors_sketch_tot.get(name).estimate_size(k=128))
    size_k64=int(authors_sketch_tot.get(name).estimate_size(k=64))
    row=[size_k512,(size_k512-realta)/size_k512*100, size_k256,(size_k256-realta)/size_k256*100,
         size_k128,(size_k128-realta)/size_k128*100, size_k64,(size_k64-realta)/size_k64*100,realta]
    mat_authors_size.loc[name]=row

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print('\n')
print('#### QUESTION 1 ####')
print(mat_Q1.loc[:,:1990])
print(mat_Q1.loc[:,2000:])
print('\n')
print('#### QUESTION 3 ####')
print('Authors Jaccard estimation k=512')
print(jaccard_estimation_k(k=512))
print('Authors Jaccard estimation k=256')
print(jaccard_estimation_k(k=256))
print(' AuthorsJaccard estimation k=128')
print(jaccard_estimation_k(k=128))
print(' Authors Jaccard estimation k=64')
print(jaccard_estimation_k(k=64))
print('\n')
print('Authors size estimation')
print(mat_authors_size)
print('\n')
print('####  QUESTION 4 ####')
print('(Distanza Media, numero BFS eseguite, nodi totali nella LCC)')
print(mat_Q2)

print('\n')
fine=time.time()
print(f"TEMPO TOTALE DI ESECUZIONE: {(fine - inizio) / 60:.2f} minuti")





