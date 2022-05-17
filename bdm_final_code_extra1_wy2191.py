# -*- coding: utf-8 -*-
"""BDM_Final_code_extra1_wy2191.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OU_USqCROTPd8BcAztpgz8D-qZW3ZTjc
"""


from pyspark import SparkContext
from pyspark.sql import SparkSession
from datetime import datetime
import pandas as pd
import json
import csv
from pyproj import Transformer
import shapely
from shapely.geometry import Point

nyc_supermarkets=pd.read_csv('nyc_supermarkets.csv')
nyc_cbg=pd.read_csv('nyc_cbg_centroids.csv')

markets_list_sg=nyc_supermarkets['safegraph_placekey']
markets_list_sg=set(markets_list_sg)

cbg_list=nyc_cbg['cbg_fips'].astype(str)
cbg_list=list(cbg_list)

cbg_dic=nyc_cbg.set_index('cbg_fips').to_dict()

def to_list(a):
  return [a[0],[a[1]]]

def append(a,b):
  a[0].extend(b[0])
  a[1].append(b[1])
  return a

def extend(a,b):
  a[0].extend(b[0])
  a[1].extend(b[1])
  return a



def extract_valid_records(partId, part):

  t = Transformer.from_crs(4326, 2263)

  if partId==0:
    next(part)
  for record in csv.reader(part):
    placekey, poi_cbg, visitor_home_cbgs, date_range_end, date_range_start= record[0],record[18],record[19],record[13],record[12]

    d_e=date_range_end.split('T')[0].split('-')
    e_d=d_e[0]+'-'+d_e[1]

    d_s=date_range_start.split('T')[0].split('-')
    s_d=d_s[0]+'-'+d_s[1]

    if placekey in markets_list_sg:
      if poi_cbg in cbg_list:
        if e_d=='2019-03'or s_d=='2019-03':
          vis=json.loads(visitor_home_cbgs)
          dis=[]
          cus=0
          for cbg in vis.keys():
            if cbg in cbg_list:
              sg_vis=t.transform(cbg_dic['latitude'][int(cbg)],cbg_dic['longitude'][int(cbg)])
              sg_poi=t.transform(cbg_dic['latitude'][int(poi_cbg)],cbg_dic['longitude'][int(poi_cbg)])

              dist=Point(sg_vis[0],sg_vis[1]).distance(Point(sg_poi[0],sg_poi[1]))/5280

              for d in range(vis[cbg]):
                dis.append(dist)


              cus=cus+vis[cbg]
          yield (poi_cbg,'2019-03'), (dis, cus, date_range_end, date_range_start)

        elif e_d=='2020-03'or s_d=='2020-03':
          vis=json.loads(visitor_home_cbgs)
          dis=[]
          cus=0
          for cbg in vis.keys():
            if cbg in cbg_list:
              sg_vis=t.transform(cbg_dic['latitude'][int(cbg)],cbg_dic['longitude'][int(cbg)])
              sg_poi=t.transform(cbg_dic['latitude'][int(poi_cbg)],cbg_dic['longitude'][int(poi_cbg)])

              dist=Point(sg_vis[0],sg_vis[1]).distance(Point(sg_poi[0],sg_poi[1]))/5280

              for d in range(vis[cbg]):
                dis.append(dist)
              cus=cus+vis[cbg]
          yield (poi_cbg,'2020-03'), (dis, cus, date_range_end, date_range_start) 

        elif e_d=='2020-10'or s_d=='2020-10':
          vis=json.loads(visitor_home_cbgs)
          dis=[]
          cus=0
          for cbg in vis.keys():
            if cbg in cbg_list:
              sg_vis=t.transform(cbg_dic['latitude'][int(cbg)],cbg_dic['longitude'][int(cbg)])
              sg_poi=t.transform(cbg_dic['latitude'][int(poi_cbg)],cbg_dic['longitude'][int(poi_cbg)])

              dist=Point(sg_vis[0],sg_vis[1]).distance(Point(sg_poi[0],sg_poi[1]))/5280

              for d in range(vis[cbg]):
                dis.append(dist)
              cus=cus+vis[cbg]
          yield (poi_cbg,'2020-10'), (dis, cus, date_range_end, date_range_start)

        elif e_d=='2019-10'or s_d=='2019-10':
          vis=json.loads(visitor_home_cbgs)
          dis=[]
          cus=0
          for cbg in vis.keys():
            if cbg in cbg_list:
              sg_vis=t.transform(cbg_dic['latitude'][int(cbg)],cbg_dic['longitude'][int(cbg)])
              sg_poi=t.transform(cbg_dic['latitude'][int(poi_cbg)],cbg_dic['longitude'][int(poi_cbg)])

              dist=Point(sg_vis[0],sg_vis[1]).distance(Point(sg_poi[0],sg_poi[1]))/5280

              for d in range(vis[cbg]):
                dis.append(dist)
              cus=cus+vis[cbg]
          yield (poi_cbg,'2019-10'), (dis, cus, date_range_end, date_range_start) 
        
        

def calculate_median(partId,part):
  for i in part:
    key, dis, cus =i[0],i[1][0],i[1][1]
    median=None
    if len(dis)>0:
        dis.sort()
        if sum(cus)>1:
          if sum(cus)%2==0:
            tag1=int(sum(cus)/2)
            tag2=int(tag1+1)

            median = (dis[tag1]+dis[tag2])/2

          else:
            tag=int((sum(cus)+1)/2)
            median=dis[tag]
        elif sum(cus)==1:
          median=sum(dis)
          

    yield key[0],key[1],median


if __name__=='__main__':

    #sys.argv[1]='BDM_Final'
    sc = SparkContext()
    rdd = sc.textFile('/tmp/bdm/weekly-patterns-nyc-2019-2020/*')

    spark = SparkSession(sc)

    result=rdd.mapPartitionsWithIndex(extract_valid_records)\
            .combineByKey(to_list,append, extend)\
            .mapPartitionsWithIndex(calculate_median)\
            .toDF(['cbg_fips','time','avg_dis'])


    pivotDF = result.groupBy("cbg_fips").pivot("time").mean("avg_dis").sort("cbg_fips", ascending=True)
    pivotDF.write.csv('BDM_Final_wy2191_extra1.csv')
