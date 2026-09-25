import numpy as np
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import xlrd
import collections
from shapely.geometry import Polygon
import random
#import geopandas

data_dir="C:/Users/a.saffarian/Datasets/Carvajal Datasets/"
# Class to load FLG9A data

class Costs:
    def get_costs(self,name,ID):
        # wst = xlrd.open_workbook(data_dir + "cost_data.xlsx")
        # #sheets = wst.sheet_names()
        # sh = wst.sheet_by_name(name)
        # costs = collections.defaultdict(int)
        # for i in range(1, sh.nrows):
        #     d = sh.row_values(i, 0, 6)
        #     costs[int(d[0])]=float(d[ID])
        # return costs

        wst=pd.read_excel(data_dir + "cost_data.xlsx",engine="openpyxl",sheet_name=name)
        costs = collections.defaultdict(int)
        for i in wst.iterrows():
            costs[i[1]["ID"]]=float(i[1][ID])
        return costs



class FLG9A(Costs):
    name="flg9a"
    def __init__(self,max_area,time_periods,data_id):
        self.id=data_id
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f1=open(data_dir+"flg9a_area.area",'r')
        area={}
        ct=0
        node_set=[]
        n_nodes=0
        for i in f1.readlines():
            if ct==0:
                n=i.strip().split("\n")
                n_nodes=int(n[0])
                ct=1
            else:
                data=i.strip().split(" ")
                area[int(data[0])]=float(data[1])
                node_set.append(int(data[0]))
        f1.close()
        self.nodes=n_nodes
        self.node_set=np.array(node_set)
        f1 = open(data_dir + "flg9a_newarea.area", "rb")
        ar = pickle.load(f1)
        f1.close()
        self.area_set=ar

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.20 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 60
        self.H = 40

    def adjacency(self):
        f2=open(data_dir+"flg9a_strong.adjacency",'r')
        #f2=open(data_dir+"distance_500.adjacency",'r')
        adj={}
        ind=0
        ct=0
        for i in f2.readlines():
            if ct==0:
                ct=1
                continue
            elif ct==1:
                k=i.strip().split(" ")
                ind=int(k[0])
                ct=2
            elif ct==2:
                k=i.strip().split(" ")
                adj[ind]=list([int(j) for j in k])
                ct=1
        f2.close()
        self.adj=adj

    def age_volume_profit(self):
        name="flg9a_ac"+str(self.id)+".age"
        f2=open(data_dir+name,'r')
        age={}
        for i in f2.readlines():
            c=[int(k) for k in i.strip().split(" ")]
            age[c[0]]=c[1]
        f2.close()

        name = "flg9a_ac" + str(self.id) + "_total.volume"
        f3 = open(data_dir+name, 'r')
        vol=[]
        ct=0
        for i in f3.readlines():
            if ct==0 or ct==1:
                ct+=1
                continue
            if len(i.strip().split(" "))==1:
                continue
            else:
                voli=[float(k) for k in i.strip().split(" ")]
                vol.append(voli[:self.T])
        f3.close()

        name = "flg9a_ac" + str(self.id) + "_total.profit"
        f4 = open(data_dir+name, 'r')
        profit = []
        ct = 0
        for i in f4.readlines():
            if ct == 0 or ct == 1:
                ct += 1
                continue
            if len(i.strip().split(" ")) == 1:
                continue
            else:
                prof = [float(k) for k in i.strip().split(" ")]
                profit.append(prof[:self.T])
        f4.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"flg9a_mini_cl_strong.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"flg9a_mini_cl_strong.p","wb")
        #f1 = open(data_dir+"flg9a_mini_cl_500d.p", "wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        wst = xlrd.open_workbook(data_dir + "point_datasets.xlsx")
        sheets = wst.sheet_names()
        sh = wst.sheet_by_name('flg9a_points')
        vertices = collections.defaultdict(list)
        for i in range(1, sh.nrows):
            d = sh.row_values(i, 0, 3)
            vertices[int(d[0])].append((float(d[1]), float(d[2])))

        self.point_set=vertices

    def plot_data(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
            plt.text(np.average(cord[:,0]),np.average(cord[:,1]),"{0}".format(i))
        plt.show()

    def plot_data_without_name(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
            #plt.text(np.average(cord[:,0]),np.average(cord[:,1]),"{0}".format(i))
        plt.show()

    def plot_soln_data(self, a, d, text, nodes, centre, rad):
        fig, ax = plt.subplots()
        font = {'family': 'serif',
                'color': 'black',
                'weight': 'normal',
                'size': 4,
                }
        for k in range(len(rad)):
            random.seed(k+6)
            r = random.random()
            g = 0.80 + random.gauss(0.05, 0.1)
            b = random.random()
            r1 = 0.80 + random.gauss(0.05, 0.1)
            g1 = random.random()
            b1 = random.random()
            g2 = 0.80 + random.gauss(0.05, 0.1)
            b2 = 0.60
            r2 = 0.80 + random.gauss(0.05, 0.1)
            colors = (r1, g1, b1)
            colors1 = (r, g, b)
            colors2 = (r2,g2,b2)
            cir = plt.Circle((centre[0][k + 1], centre[1][k + 1]), radius=rad[k + 1], color="b", alpha=0.2)
            ax.add_patch(cir)
            for i in self.node_set:
                if i in nodes:
                    cord = []
                    for j in self.point_set[i]:
                        cord.append(list(j))
                    cord = np.array(cord)
                    plt.plot(cord[:, 0], cord[:, 1], 'b', linewidth=0.2)
                    # plt.text(sum(cord[:, 0]) / len(cord[:, 0]), sum(cord[:, 1]) / len(cord[:, 1]), i, fontdict=font)
                    for j in a:
                        if i in a[j]:
                            ax.fill(cord[:, 0], cord[:, 1], color=colors, alpha=1.0)
                    # if i not in a and i not in c:
                    # ax.fill(cord[:,0],cord[:,1],color='r',alpha=0.4)
                    # if i in c and i not in a:
                    # ax.fill(cord[:, 0], cord[:, 1], color='g', alpha=0.7)
                    if i in d:
                        ax.fill(cord[:, 0], cord[:, 1], color=colors1, alpha=0.9)
        plt.title(text)
        plt.axis('scaled')
        plt.savefig("1FLG9A_03A_06B.png", dpi = 1200)
        plt.show()

# Class to load ELDorado data
class ElDorado(Costs):
    name="eldo"
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f1=open(data_dir+"eldo_area.area",'r')
        area={}
        ct=0
        n_nodes=0
        node_set=[]
        for i in f1.readlines():
            if ct==0:
                n=i.strip().split("\n")
                n_nodes=int(n[0])
                ct=1
            else:
                data=i.strip().split(" ")
                area[int(data[0])]=float(data[1])
                node_set.append(int(data[0]))
        f1.close()
        self.nodes=n_nodes
        self.node_set=np.array(node_set)
        f1 = open(data_dir + "eldo_newarea.area", "rb")
        ar = pickle.load(f1)
        f1.close()
        self.area_set=ar

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.20 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 20
        self.H = 30

    def adjacency(self):
        f2=open(data_dir+"eldo_point.adjacency",'r')
        adj={}
        ind=0
        ct=0
        for i in f2.readlines():
            if ct==0:
                ct=1
                continue
            elif ct==1:
                k=i.strip().split(" ")
                ind=int(k[0])
                ct=2
            elif ct==2:
                k=i.strip().split(" ")
                if k==['']:
                    adj[ind]=[]
                else:
                    adj[ind]=list([int(j) for j in k])
                ct=1
        f2.close()
        self.adj=adj

    def age_volume_profit(self):
        f2=open(data_dir+"eldo_age.age",'r')
        age={}
        for i in f2.readlines():
            c=[int(k) for k in i.strip().split(" ")]
            age[c[0]]=c[1]
            if c[1]<0:
                age[c[0]]=0
        f2.close()

        f3 = open(data_dir+"eldo_volume.volume", 'r')
        vol=[]
        ct=0
        for i in f3.readlines():
            if ct==0 or ct==1:
                ct+=1
                continue
            if len(i.strip().split(" "))==1:
                continue
            else:
                voli=[float(k) for k in i.strip().split(" ")]
                vol.append(voli[:self.T])
        f3.close()

        f4 = open(data_dir+"eldo_profit.profit", 'r')
        profit = []
        ct = 0
        for i in f4.readlines():
            if ct == 0 or ct == 1:
                ct += 1
                continue
            if len(i.strip().split(" ")) == 1:
                continue
            else:
                prof = [float(k) for k in i.strip().split(" ")]
                profit.append(prof[:self.T])
        f4.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"eldo_mini_cl_point.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"eldo_mini_cl_point.p","wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        wst = xlrd.open_workbook(data_dir + "point_datasets.xlsx")
        sheets = wst.sheet_names()
        sh = wst.sheet_by_name('eldo_points')
        vertices = collections.defaultdict(list)
        for i in range(1, sh.nrows):
            d = sh.row_values(i, 0, 3)
            vertices[int(d[0])].append((float(d[1]), float(d[2])))

        self.point_set = vertices

    def plot_data(self,a):
        for i in a:
            cord = []
            for j in self.point_set[i]:
                cord.append(list(j))
            cord = np.array(cord)
            plt.plot(cord[:, 0], cord[:,1], 'b', linewidth = 0.1)
            #if self.node_type[i] == "O":
            #    plt.plot(cord[:, 0], cord[:, 1], 'b', linewidth = 0.1)
            #else:
            #    plt.plot(cord[:, 0], cord[:, 1], 'r', linewidth = 0.1)
        plt.axis('scaled')
        plt.show()
        #plt.savefig("eldo_points.pdf",dpi=1200)

    def plot_soln_data(self, a, d, text, nodes, centre, rad):
        fig, ax = plt.subplots()
        font = {'family': 'serif',
                'color': 'black',
                'weight': 'normal',
                'size': 4,
                }
        for k in range(len(rad)):
            random.seed(k + 6)
            r = random.random()
            g = 0.80 + random.gauss(0.05, 0.1)
            b = random.random()
            colors = (r, g, b)
            colors1 = (r + 0.05, g + 0.05, b + 0.05)
            cir = plt.Circle((centre[0][k + 1], centre[1][k + 1]), radius=rad[k + 1], color="b", alpha=0.2)
            ax.add_patch(cir)
            for i in self.node_set:
                if i in nodes:
                    cord = []
                    for j in self.point_set[i]:
                        cord.append(list(j))
                    cord = np.array(cord)
                    plt.plot(cord[:, 0], cord[:, 1], 'b', linewidth = 0.1)
                    #plt.text(sum(cord[:, 0]) / len(cord[:, 0]), sum(cord[:, 1]) / len(cord[:, 1]), i, fontdict=font)
                    if i in a[k + 1]:
                        ax.fill(cord[:, 0], cord[:, 1], color=colors, alpha=1.0)
                    # if i not in a and i not in c:
                    # ax.fill(cord[:,0],cord[:,1],color='r',alpha=0.4)
                    # if i in c and i not in a:
                    # ax.fill(cord[:, 0], cord[:, 1], color='g', alpha=0.7)
                    if i in d:
                        ax.fill(cord[:, 0], cord[:, 1], color=colors1, alpha=0.9)
        plt.title(text)
        plt.axis('scaled')
        plt.show()
        plt.savefig("optpoint_eldo"+text+".pdf",dpi=1200)

# Class to load ShulKell data
class ShulKellA:
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()

    def node_areas(self):
        f1=open(data_dir+"shkl_area.area",'r')
        area={}
        ct=0
        n_nodes=0
        node_set=[]
        for i in f1.readlines():
            if ct==0:
                n=i.strip().split("\n")
                n_nodes=int(n[0])
                ct=1
            else:
                data=i.strip().split(" ")
                area[int(data[0])]=float(data[1])
                node_set.append(int(data[0]))
        f1.close()
        self.nodes=n_nodes
        self.node_set=np.array(node_set)
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.20 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 60
        self.H = 40

    def adjacency(self):
        f2=open(data_dir+"shkl_line.adjacency",'r')
        adj={}
        ind=0
        ct=0
        for i in f2.readlines():
            if ct==0:
                ct=1
                continue
            elif ct==1:
                k=i.strip().split(" ")
                ind=int(k[0])
                ct=2
            elif ct==2:
                k=i.strip().split(" ")
                if k==['']:
                    adj[ind]=[]
                else:
                    adj[ind]=list([int(j) for j in k])
                ct=1
        f2.close()
        self.adj=adj

    def age_volume_profit(self):
        f2=open(data_dir+"shkl_age.age",'r')
        age={}
        for i in f2.readlines():
            c=[int(k) for k in i.strip().split(" ")]
            age[c[0]]=c[1]
        f2.close()

        f3 = open(data_dir+"shkl_volume.volume", 'r')
        vol=[]
        ct=0
        for i in f3.readlines():
            if ct==0 or ct==1:
                ct+=1
                continue
            if len(i.strip().split(" "))==1:
                continue
            else:
                voli=[float(k) for k in i.strip().split(" ")]
                vol.append(voli[:self.T])
        f3.close()

        f4 = open(data_dir+"shkl_profit.profit", 'r')
        profit = []
        ct = 0
        for i in f4.readlines():
            if ct == 0 or ct == 1:
                ct += 1
                continue
            if len(i.strip().split(" ")) == 1:
                continue
            else:
                prof = [float(k) for k in i.strip().split(" ")]
                profit.append(prof[:self.T])
        f4.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"shkl_mini_cl_line.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"shkl_mini_cl_line.p","wb")
        pickle.dump(var,f1)
        f1.close()

    def plot_soln_data(self, a, d, text, nodes, centre, rad):
        fig, ax = plt.subplots()
        font = {'family': 'serif',
                'color': 'black',
                'weight': 'normal',
                'size': 4,
                }
        for k in range(len(rad)):
            random.seed(k + 6)
            r = random.random()
            g = 0.80 + random.gauss(0.05, 0.1)
            b = random.random()
            colors = (r, g, b)
            colors1 = (r + 0.05, g + 0.05, b + 0.05)
            cir = plt.Circle((centre[0][k + 1], centre[1][k + 1]), radius=rad[k + 1], color="b", alpha=0.2)
            ax.add_patch(cir)
            for i in self.node_set:
                if i in nodes:
                    cord = []
                    for j in self.point_set[i]:
                        cord.append(list(j))
                    cord = np.array(cord)
                    plt.plot(cord[:, 0], cord[:, 1], 'b', linewidth=0.2)
                    # plt.text(sum(cord[:, 0]) / len(cord[:, 0]), sum(cord[:, 1]) / len(cord[:, 1]), i, fontdict=font)
                    if i in a[k + 1]:
                        ax.fill(cord[:, 0], cord[:, 1], color=colors, alpha=1.0)
                    # if i not in a and i not in c:
                    # ax.fill(cord[:,0],cord[:,1],color='r',alpha=0.4)
                    # if i in c and i not in a:
                    # ax.fill(cord[:, 0], cord[:, 1], color='g', alpha=0.7)
                    if i in d:
                        ax.fill(cord[:, 0], cord[:, 1], color=colors1, alpha=0.9)
        plt.title(text)
        plt.axis('scaled')
        plt.show()

# Class to load NBCL5A data
class NBCL5A:
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f1=open(data_dir+"nbcl_area.area",'r')
        area={}
        ct=0
        n_nodes=0
        node_set=[]
        for i in f1.readlines():
            if ct==0:
                n=i.strip().split("\n")
                n_nodes=int(n[0])
                ct=1
            else:
                data=i.strip().split(" ")
                area[int(data[0])]=float(data[1])
                node_set.append(int(data[0]))
        f1.close()
        self.nodes=n_nodes
        self.node_set=np.array(node_set)
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.2 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 60
        self.H = 40

    def adjacency(self):
        f2=open(data_dir+"nbcl_line.adjacency",'r')
        adj={}
        ind=0
        ct=0
        for i in f2.readlines():
            if ct==0:
                ct=1
                continue
            elif ct==1:
                k=i.strip().split(" ")
                ind=int(k[0])
                ct=2
            elif ct==2:
                k=i.strip().split(" ")
                if k==['']:
                    adj[ind]=[]
                else:
                    adj[ind]=list([int(j) for j in k])
                ct=1
        f2.close()
        self.adj=adj

    def age_volume_profit(self):
        f2=open(data_dir+"nbcl_age.age",'r')
        age={}
        for i in f2.readlines():
            c=[int(k) for k in i.strip().split(" ")]
            age[c[0]]=c[1]
        f2.close()

        f3 = open(data_dir+"nbcl_total.volume", 'r')
        vol=[]
        ct=0
        for i in f3.readlines():
            if ct==0 or ct==1:
                ct+=1
                continue
            if len(i.strip().split(" "))==1:
                continue
            else:
                voli=[float(k) for k in i.strip().split(" ")]
                vol.append(voli[:self.T])
        f3.close()

        f4 = open(data_dir+"nbcl_total.profit", 'r')
        profit = []
        ct = 0
        for i in f4.readlines():
            if ct == 0 or ct == 1:
                ct += 1
                continue
            if len(i.strip().split(" ")) == 1:
                continue
            else:
                prof = [float(k) for k in i.strip().split(" ")]
                profit.append(prof[:self.T])
        f4.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"nbcl_mini_cl_line.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"nbcl_mini_cl_line.p","wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        f1 = open(data_dir+"nbcl_points.txt", "r")
        point_set = {}
        ct = 0
        temp = 0
        for i in f1.readlines():
            if ct == 0:
                ct += 1
                continue
            else:
                c = i.strip().split("\t")
                a = int(c[0])
                if temp != a:
                    point_set[a] = []
                point_set[a].append((float(c[1]), float(c[2])))
                temp = a
        self.point_set=point_set
        f1.close()

    def plot_data(self,a):
        fig,ax=plt.subplots()
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b',linewidth=0.001)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_aspect(0.6)
        plt.savefig("point_nbcl5a.pdf", dpi=1200)

    def plot_soln_data(self,a,text):
        fig,ax=plt.subplots()
        for i in self.node_set:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b',linewidth=0.001)
            if i in a:
                ax.fill(cord[:,0],cord[:,1],color='b',alpha=0.7,linewidth=0.001)
            plt.title("NBCL5A: Old-growth patch for "+text)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_aspect(0.6)
        plt.savefig("optpoint_nbcl5a"+text+".pdf", dpi=1200)

# Class to load ButterCreek data
class ButterCreek(Costs):
    name="btck"
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f1=open(data_dir+"btck_area.area",'r')
        area={}
        ct=0
        n_nodes=0
        node_set=[]
        for i in f1.readlines():
            if ct==0:
                n=i.strip().split("\n")
                n_nodes=int(n[0])
                ct=1
            else:
                data=i.strip().split(" ")
                area[int(data[0])]=float(data[1])
                node_set.append(int(data[0]))
        f1.close()
        self.nodes=n_nodes
        self.node_set=np.array(node_set)
        f1 = open(data_dir + "btck_newarea.area", "rb")
        area= pickle.load(f1)
        f1.close()
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.20 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 15
        self.H = 20

    def adjacency(self):
        f2=open(data_dir+"btck_line.adjacency",'r')
        adj={}
        ind=0
        ct=0
        for i in f2.readlines():
            if ct==0:
                ct=1
                continue
            elif ct==1:
                k=i.strip().split(" ")
                ind=int(k[0])
                ct=2
            elif ct==2:
                k=i.strip().split(" ")
                if k==['']:
                    adj[ind]=[]
                else:
                    adj[ind]=list([int(j) for j in k])
                ct=1
        f2.close()
        self.adj=adj

    def age_volume_profit(self):
        f2 = open(data_dir+"btck_new_age.p", "rb")
        age = pickle.load(f2)
        f2.close()

        f3=open(data_dir+"btck_volume.volume","rb")
        vol=pickle.load(f3)
        f3.close()

        f4 = open(data_dir+"btck_new_profit.p", "rb")
        profit = pickle.load(f4)
        f4.close()

        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"btck_mini_cl_line.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"btck_mini_cl_line.p","wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        wst = xlrd.open_workbook(data_dir + "point_datasets.xlsx")
        sheets = wst.sheet_names()
        sh = wst.sheet_by_name('btck_points')
        vertices = collections.defaultdict(list)
        for i in range(1, sh.nrows):
            d = sh.row_values(i, 0, 3)
            vertices[int(d[0])].append((float(d[1]), float(d[2])))

        self.point_set = vertices

    def plot_data(self,a):
        fig,ax=plt.subplots()
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b',linewidth=0.1)
            ax.fill(cord[:, 0], cord[:, 1], color='b', alpha=0.3, linewidth=0.1)
        #ax.set_yticklabels([])
        #ax.set_xticklabels([])
        #ax.set_aspect(1.0)
        plt.show()
        #plt.savefig("point_buttercreek.pdf", dpi=1200)

    def plot_soln_data(self, a, text, nodes, centre, rad):
        fig, ax = plt.subplots()
        cir = plt.Circle(centre, radius=rad, color="b", alpha=0.2)
        ax.add_patch(cir)
        for i in nodes:
            cord=[]
            print(i)
            for j in self.point_set[i]:
                cord.append(list(j))
            if cord!=[]:
                cord=np.array(cord)
                plt.plot(cord[:,0],cord[:,1],'b',linewidth=0.001)
                if i in a:
                    ax.fill(cord[:,0],cord[:,1],color='b',alpha=0.7,linewidth=0.001)
                plt.title("Buttercreek: Old-growth patch for "+text)
        #ax.set_yticklabels([])
        #ax.set_xticklabels([])
        #ax.set_aspect(1.0)
        plt.show()
        #plt.savefig("optpoint_buttercreek"+text+".pdf", dpi=1200)

# Class to load Hardwicke data
class Hardwicke(Costs):
    name="hard"
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        # f1 = open(data_dir + "hard_newarea.area", "rb")
        # area = pickle.load(f1)
        # f1.close()
        # n_nodes=len(area)
        # node_set=list(area.keys())
        # self.nodes=n_nodes
        # self.node_set=np.array(node_set)
        # self.area_set=area
        f1=pd.read_csv(data_dir+"hardwicke_addtarea.csv")
        n_nodes=len(f1)
        area={i[1]["ID"]:i[1]["Area"] for i in f1.iterrows()}
        types={i[1]["ID"]:i[1]["Type"] for i in f1.iterrows()}
        node_set=list(area.keys())
        self.nodes=n_nodes
        self.node_set=np.array(node_set)
        self.area_set=area
        self.node_type=types

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.20 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 45
        self.H = 40

    def adjacency(self):
        f1 = open(data_dir+"hard_adjace2.txt", "r")
        oldi = 1
        temp = []
        adj = {}
        for i in f1.readlines():
            c = i.strip().split(",")
            ind = int(c[0])
            if ind != oldi:
                adj[oldi] = temp
                temp = []
                oldi = ind
            else:
                temp.append(int(c[1]))
                oldi = ind

        f1.close()
        self.adj=adj

    def age_volume_profit(self):
        f = open(data_dir+"hard_age.txt", "r")
        f.readline()
        age = {}
        for i in f.readlines():
            c = i.strip().split("\t")
            age[int(c[0])] = int(c[1])
        f.close()

        f = open(data_dir+"hard_volume.volume", "rb")
        vol=pickle.load(f)
        f.close()

        f = open(data_dir+"hard_profit.profit", "rb")
        profit=pickle.load(f)
        f.close()

        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"hard_mini_cl.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"hard_mini_cl.p","wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        # wst = xlrd.open_workbook(data_dir + "point_datasets.xlsx",engine="openpyxl")
        # sheets = wst.sheet_names()
        # sh = wst.sheet_by_name('hard_points')
        # vertices = collections.defaultdict(list)
        # for i in range(1, sh.nrows):
        #     d = sh.row_values(i, 0, 3)
        #     vertices[int(d[0])].append((float(d[1]), float(d[2])))
        #
        # self.point_set = vertices

        #wst=pd.read_excel(data_dir + "point_datasets.xlsx",engine="openpyxl",sheet_name="hard_points")
        wst = pd.read_csv(data_dir + "harwicke_new_points.csv")#, engine="openpyxl", sheet_name="hard_points")

        vertices=collections.defaultdict(list)
        for i in wst.iterrows():
            vertices[int(i[1]["ID"])].append((round(i[1]["X"],4),round(i[1]["Y"],4)))
        self.point_set=vertices.copy()


    def plot_data(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            if self.node_type[i]=="O":
                plt.plot(cord[:,0],cord[:,1],'b', linewidth = 0.2)
            else:
                plt.plot(cord[:, 0], cord[:, 1], 'b', linewidth = 0.2)
        plt.axis('scaled')
        plt.show()

    def plot_soln_data(self, a, d, text, nodes, centre, rad):
        fig, ax = plt.subplots()
        font = {'family': 'serif',
                'color': 'black',
                'weight': 'normal',
                'size': 4,
                }
        for k in range(len(rad)):
            random.seed(k + 6)
            r = random.random()
            g = 0.80 + random.gauss(0.05, 0.1)
            b = random.random()
            r1 = 0.80 + random.gauss(0.05, 0.1)
            g1 = random.random()
            b1 = random.random()
            g2 = 0.80 + random.gauss(0.05, 0.1)
            b2 = 0.60
            r2 = 0.80 + random.gauss(0.05, 0.1)
            colors = (r1, g1, b1)
            colors1 = (r, g, b)
            colors2 = (r2, g2, b2)
            cir = plt.Circle((centre[0][k + 1], centre[1][k + 1]), radius=rad[k + 1], color="b", alpha=0.2)
            ax.add_patch(cir)
            for i in self.node_set:
                if i in nodes:
                    cord = []
                    for j in self.point_set[i]:
                        cord.append(list(j))
                    cord = np.array(cord)
                    plt.plot(cord[:, 0], cord[:, 1], 'b', linewidth=0.2)
                    #plt.text(sum(cord[:, 0]) / len(cord[:, 0]), sum(cord[:, 1]) / len(cord[:, 1]), i, fontdict=font)
                    for j in a:
                        if i in a[j]:
                            ax.fill(cord[:, 0], cord[:, 1], color=colors, alpha=1.0)
                    # if i not in a and i not in c:
                    # ax.fill(cord[:,0],cord[:,1],color='r',alpha=0.4)
                    # if i in c and i not in a:
                    # ax.fill(cord[:, 0], cord[:, 1], color='g', alpha=0.7)
                    if i in d:
                        ax.fill(cord[:, 0], cord[:, 1], color=colors1, alpha=0.9)
        plt.title(text)
        plt.axis('scaled')
        plt.savefig("Pic.png", dpi = 1200)
        plt.show()
# Class to load Random 20x20 data
class Random400:
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f = open(data_dir+"random20x20_area.p", "rb")
        area=pickle.load(f)
        f.close()
        self.nodes=len(area.keys())
        self.node_set=np.array(list(area.keys()))
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.20 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 70
        self.H = 40

    def adjacency(self):
        f = open(data_dir+"random20x20_adj.p", "rb")
        adj=pickle.load(f)
        f.close()
        self.adj=adj

    def age_volume_profit(self):
        f = open(data_dir+"random20x20_age.p", "rb")
        age=pickle.load(f)
        f.close()
        f = open(data_dir+"random20x20_profit.p", "rb")
        profit=pickle.load(f)
        f.close()
        f = open(data_dir+"random20x20_volume.p", "rb")
        vol=pickle.load(f)
        f.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"random20x20_mini_cl.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"random20x20_mini_cl.p","wb")
        #f1 = open(data_dir+"flg9a_mini_cl_500d.p", "wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        f = open(data_dir+"random20x20_points.p", "rb")
        point_set=pickle.load(f)
        f.close()
        self.point_set=point_set

    def plot_data(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
        plt.show()

    def plot_soln_data(self,a,text): 
        fig,ax=plt.subplots()
        for i in self.node_set:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
            if i in a:
                ax.fill(cord[:,0],cord[:,1],color='b',alpha=0.7)
            plt.title("20x20: Old-growth patch for "+text)
        plt.show()

# Class to load Random 10x10 data
class Random100:
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f = open(data_dir+"random10x10_area.p", "rb")
        area=pickle.load(f)
        f.close()
        self.nodes=len(area.keys())
        self.node_set=np.array(list(area.keys()))
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.2 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 60
        self.H = 40

    def adjacency(self):
        f = open(data_dir+"random10x10_adj.p", "rb")
        adj=pickle.load(f)
        f.close()
        self.adj=adj

    def age_volume_profit(self):
        f = open(data_dir+"random10x10_age.p", "rb")
        age=pickle.load(f)
        f.close()
        f = open(data_dir+"random10x10_profit.p", "rb")
        profit=pickle.load(f)
        f.close()
        f = open(data_dir+"random10x10_volume.p", "rb")
        vol=pickle.load(f)
        f.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"random10x10_mini_cl.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"random10x10_mini_cl.p","wb")
        #f1 = open(data_dir+"flg9a_mini_cl_500d.p", "wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        f = open(data_dir+"random10x10_points.p", "rb")
        point_set=pickle.load(f)
        f.close()
        self.point_set=point_set

    def plot_data(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
        plt.show()

    def plot_soln_data(self,a,text):
        fig,ax=plt.subplots()
        for i in self.node_set:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
            if i in a:
                ax.fill(cord[:,0],cord[:,1],color='b',alpha=0.7)
            plt.title("10x10: Old-growth patch for "+text)
        plt.show()

# Class to load Random 5x10 data
class Random50:
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f = open(data_dir+"random5x10_area.p", "rb")
        area=pickle.load(f)
        f.close()
        self.nodes=len(area.keys())
        self.node_set=np.array(list(area.keys()))
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.2 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 60
        self.H = 40

    def adjacency(self):
        f = open(data_dir+"random5x10_adj.p", "rb")
        adj=pickle.load(f)
        f.close()
        self.adj=adj

    def age_volume_profit(self):
        f = open(data_dir+"random5x10_age.p", "rb")
        age=pickle.load(f)
        f.close()
        f = open(data_dir+"random5x10_profit.p", "rb")
        profit=pickle.load(f)
        f.close()
        f = open(data_dir+"random5x10_volume.p", "rb")
        vol=pickle.load(f)
        f.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"random5x10_mini_cl.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"random5x10_mini_cl.p","wb")
        #f1 = open(data_dir+"flg9a_mini_cl_500d.p", "wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        f = open(data_dir+"random5x10_points.p", "rb")
        point_set=pickle.load(f)
        f.close()
        self.point_set=point_set

    def plot_data(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
        plt.show()

    def plot_soln_data(self,a,text):
        fig,ax=plt.subplots()
        for i in self.node_set:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
            if i in a:
                ax.fill(cord[:,0],cord[:,1],color='b',alpha=0.7)
            plt.title("5x10: Old-growth patch for "+text)
        plt.show()

# Class to load Random 10x20 data
class Random200:
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f = open(data_dir+"random20x10_area.p", "rb")
        area=pickle.load(f)
        f.close()
        self.nodes=len(area.keys())
        self.node_set=np.array(list(area.keys()))
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.2 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 60
        self.H = 40

    def adjacency(self):
        f = open(data_dir+"random20x10_adj.p", "rb")
        adj=pickle.load(f)
        f.close()
        self.adj=adj

    def age_volume_profit(self):
        f = open(data_dir+"random20x10_age.p", "rb")
        age=pickle.load(f)
        f.close()
        f = open(data_dir+"random20x10_profit.p", "rb")
        profit=pickle.load(f)
        f.close()
        f = open(data_dir+"random20x10_volume.p", "rb")
        vol=pickle.load(f)
        f.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"random20x10_mini_cl.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"random20x10_mini_cl.p","wb")
        #f1 = open(data_dir+"flg9a_mini_cl_500d.p", "wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        f = open(data_dir+"random20x10_points.p", "rb")
        point_set=pickle.load(f)
        f.close()
        self.point_set=point_set

    def plot_data(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
        plt.show()

    def plot_soln_data(self,a,text):
        fig,ax=plt.subplots()
        for i in self.node_set:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
            if i in a:
                ax.fill(cord[:,0],cord[:,1],color='b',alpha=0.7)
            plt.title("20x10: Old-growth patch for "+text)
        plt.show()

# Class to load Random 30x30 data
class Random900:
    def __init__(self,max_area,time_periods):
        self.A_max=max_area
        self.T=time_periods
        self.node_areas()
        self.constants()
        self.adjacency()
        self.age_volume_profit()
        self.min_clust()
        self.store_data()

    def node_areas(self):
        f = open(data_dir+"random30x30_area.p", "rb")
        area=pickle.load(f)
        f.close()
        self.nodes=len(area.keys())
        self.node_set=np.array(list(area.keys()))
        self.area_set=area

    def constants(self):
        k = list(self.area_set.values())
        k = np.array(k)
        self.A_min = 0.2 * np.sum(k)
        self.L = 0.15
        self.U = 0.15
        self.O_age = 60
        self.H = 40

    def adjacency(self):
        f = open(data_dir+"random30x30_adj.p", "rb")
        adj=pickle.load(f)
        f.close()
        self.adj=adj

    def age_volume_profit(self):
        f = open(data_dir+"random30x30_age.p", "rb")
        age=pickle.load(f)
        f.close()
        f = open(data_dir+"random30x30_profit.p", "rb")
        profit=pickle.load(f)
        f.close()
        f = open(data_dir+"random30x30_volume.p", "rb")
        vol=pickle.load(f)
        f.close()
        self.init_age=age
        self.volume=np.array(vol)
        self.profit=np.array(profit)

    def min_clust(self):
        f1=open(data_dir+"random30x30_mini_cl.p","rb")
        min_cl=pickle.load(f1)
        f1.close()
        self.min_cl=min_cl

    def save_min_cl(self,var):
        f1=open(data_dir+"random30x30_mini_cl.p","wb")
        #f1 = open(data_dir+"flg9a_mini_cl_500d.p", "wb")
        pickle.dump(var,f1)
        f1.close()

    def store_data(self):
        f = open(data_dir+"random30x30_points.p", "rb")
        point_set=pickle.load(f)
        f.close()
        self.point_set=point_set

    def plot_data(self,a):
        for i in a:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
        plt.show()

    def plot_soln_data(self,a,text):
        fig,ax=plt.subplots()
        for i in self.node_set:
            cord=[]
            for j in self.point_set[i]:
                cord.append(list(j))
            cord=np.array(cord)
            plt.plot(cord[:,0],cord[:,1],'b')
            if i in a:
                ax.fill(cord[:,0],cord[:,1],color='b',alpha=0.7)
            plt.title("30x30: Old-growth patch for "+text)
        plt.show()


# if __name__=="__main__":
#     ID = 1
#     #U = np.array(list(range(1, nu + 1)))
#     area_p=0.05 #0.2,0.5
#     min_comp = 0
#     bud_p = 0.1 #0.5,1
#
#     flgid = 5
#
#     # A_max: Maximum area of the instance. Choose from one of these options
#     # 1) 48.6 - for FLG9A instances.
#     # 2) 40   - for Hardwicke and Shulkell and Random
#     # 3) 80   - for NBCL5A instance.
#     # 4) 120  - for El Dorado and Buttercreek.
#     A_max = 40
#
#     # T: Time periods: The value is 3 for the given model.
#     T = 3
#
#     # Yt: Number of years in each time period. Set this to 10 for El Dorado instance, 5 otherwise.
#     Yt = 5
#
#     #Data = lfd.FLG9A(A_max, T, flgid)  ## Import Data for FLG9A (5 instances)
#     #Data=lfd.ButterCreek(A_max,T) ## Import Data for Buttercreek
#     # Data=ld.NBCL5A(A_max,T)      ## Import Data for NBCL5A
#     #Data=ElDorado(A_max,T)    ## Import Data for El Dorado
#     # Data=lfd.ShulKellA(A_max,T)   ## Import Data for Shulkell
#     Data = Hardwicke(A_max, T)  ## Import Data for Hardwicke
#     # Data=ld.Random50(A_max,T)     ## Import Data for random instance. Change the numbers among
#     ## a) 50 b) 100 c) 200 d) 400 e) 900
#
#     min_area = Data.A_min  ### - in same format
#     nodes = Data.node_set  ### - in same format
#     area = Data.area_set  ### - in same format
#
#     min_area = area_p * sum(area.values())
#     print("min ", min_area)
#     print("total ", sum(area.values()))
#     print("ratio ", min_area / sum(area.values()))
#
#     cost=Data.get_costs(Data.name,ID)
#     neighbours = Data.adj  ### - in same format
#     vertices = Data.point_set  ### - in same format
#
#     centers = {}
#     for i in vertices.keys():
#         x = 0
#         y = 0
#         for j in vertices[i][:len(vertices[i]) - 1]:
#             x += j[0]
#             y += j[1]
#         x = x / (len(vertices[i]) - 1)
#         y = y / (len(vertices[i]) - 1)
#         centers[i] = (x, y)
#
#
#     distance = {}
#     for i in centers.keys():
#         for j in centers.keys():
#             distance[i, j] = ((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2) ** 0.5
#     xlim = 140  ## 100 each for flg9a, (175,75) for hardwicke, (430,80) for el dorado
#     ylim = 140
#     Data.plot_data(nodes)
#     # Uncovered = [Point(node_xy[i]) for i in uncovered]
#     # newdata = geopandas.GeoDataFrame(geometry=Uncovered)
#     # newdata.to_file(resdir + f"LA_uncovered_{task[0]}_{NOS}_{root}.shp")
#     # #
#     # Hard=[]
#     # for i in Data.point_set.keys():
#     #     print(f"point {i} converted")
#     #     Hard.append(Polygon(Data.point_set[i]))
#     # # newd=geopandas.GeoDataFrame(geometry=Hard)
#     # # newd.to_file(data_dir+f"Hardwicke_maporig_shapefile.shp")
#     #
#     # #import arcgis
#     # import pandas as pd
#     # hard_pts=pd.read_csv(data_dir+"harwicke_new_points.csv")
#     # new_patches=collections.defaultdict(list)
#     # area_patches={}
#     # type_patches={}
#     # for i in hard_pts.iterrows():
#     #     new_patches[int(i[1]["ID"])].append((i[1]["X"],i[1]["Y"]))
#     #
#     # for i in new_patches.keys():
#     #     area_patches[i]=Polygon(new_patches[i]).area
#     #     type_patches[i]=hard_pts["TYPE"][hard_pts.ID==i].unique()[0]
#
#
#     ## create new dataframe:
#     # df={"ID":[],"Area":[],"Type":[]}
#     # for i in new_patches.keys():
#     #     df["ID"].append(i)
#     #     df["Area"].append(area_patches[i])
#     #     df["Type"].append(type_patches[i])
#     #
#     # df=pd.DataFrame(df)
#     # df.to_csv(data_dir+"hardwicke_addtarea.csv")
#     newadj=collections.defaultdict(list)
#     for i in nodes:
#         for j in nodes:
#             if j>i:
#                 tval=Polygon(Data.point_set[i]).intersection(Polygon(Data.point_set[j])).is_empty
#                 if not tval:
#                     newadj[i].append(j)
#                     newadj[j].append(i)
#
#     # for k in nodes:
#     #     if Data.node_type[k]=="N":
#     #         for i in nodes:
#     #             cord = []
#     #             for j in Data.point_set[i]:
#     #                 cord.append(list(j))
#     #             cord = np.array(cord)
#     #             if i not in newadj[k] and i!=k:
#     #                 plt.plot(cord[:, 0], cord[:, 1], 'b',lw=0.1)
#     #             elif i==k:
#     #                 plt.plot(cord[:, 0], cord[:, 1], 'r')
#     #             else:
#     #                 plt.plot(cord[:, 0], cord[:, 1], 'g')
#     #         plt.axis('scaled')
#     #         plt.show()
#
#     # f1=open(data_dir+"hard_adjace2.txt","w")
#     # for i in newadj.keys():
#     #     for j in newadj[i]:
#     #         f1.write(f"{i},{j}\n")
#     # f1.close()