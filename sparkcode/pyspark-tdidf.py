""" Use a TD-IDF to count words that appear in toots stored in datalake """

import time
import json
import os
import re
import numpy
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType,StructField, StringType, IntegerType
from pyspark.ml.feature import *


# config
DatalakeLocation = '/opt/data'
WarehouseLocation = '/opt/warehouse'
MinDocCount = 2   # only include words that appear in more than 1 toot
SparkRunInterval = 30 # seconds


# Build spark
spark = SparkSession.builder\
    .appName("mstdn-nlp-td-idf")\
    .master("spark://spark-master:7077")\
    .config("spark.executor.instances", 1)\
    .getOrCreate() 

os.listdir(DatalakeLocation)
NumToots = 0

Schema = StructType([ \
    StructField("id",StringType(),True), \
    StructField("username",StringType(),True), \
    StructField("content",StringType(),True), \
  ])

emptyRDD = spark.sparkContext.emptyRDD()
AllData = spark.createDataFrame(data=emptyRDD, schema=Schema)

# run spark in infinite loop
while True: 

    # grab all json files from the datalake
    for folder, subs, files in os.walk(DatalakeLocation):
        for filename in files:
            
            # read json file
            ThisFile = os.path.join(folder, filename) 
            words = spark.read.json(ThisFile)
            
            # skip any toots that are not English
            if words.collect()[0]["language"] != "en":
                continue
                
            # skip any empty contents
            if not words.collect()[0]["content"] :
                continue
            

            ## clean up the text of the toot
            # get only the fields we want
            ExtractedData = words.select("account.id", "account.username", "content")
            Text = words.collect()[0]["content"]
            
            # make all letters lowercase
            Text = Text.lower()
            
            # many toots start with <p>, so get rid of that
            if Text[0] == '<':
                Text = Text[3:]
                
            # get rid of anything after another <, if it exists
            if '<' in Text:
                Text = Text[:Text.index('<')]
            
            # replace '-' with spaces
            Text = Text.replace('-', ' ')
            
            # replace '—' with spaces
            Text = Text.replace('—', ' ')
            
            # replace ':' with spaces
            Text = Text.replace(':', ' ')
            
            # replace '&nbsp;' with spaces
            Text = Text.replace('&nbsp;', ' ')
            
            # put cleaned up text together
            Data = [(ExtractedData.collect()[0]["id"], ExtractedData.collect()[0]["username"], Text)]
            DataOut = spark.createDataFrame(data=Data,schema=Schema)
            
            # join this file into big dataset
            AllData = AllData.union(DataOut)
            
            NumToots += 1
            #print("Read in " + str(NumToots) + " toots")
            
        # shortcut to end collection early to run td-idf on less data    
        #if NumToots >= 10:
            #break
        
    ## perform the TD-IDF
    # make the data structure to run on
    df = (AllData
        .rdd
        .map(lambda x : (x.id,x.username,x.content.split(" ")))
        .toDF()
        .withColumnRenamed("_1","id")
        .withColumnRenamed("_2","username")
        .withColumnRenamed("_3","features"))

    # perform the TF
    htf = HashingTF(inputCol="features", outputCol="tf")
    tf = htf.transform(df)
    tf.show(truncate=False)

    # Perform the IDF, ignoring words that appear in less than MinDocCount toots
    idf = IDF(inputCol="tf", outputCol="idf", minDocFreq=MinDocCount)
    tfidf = idf.fit(tf).transform(tf)
    tfidf.show(truncate=False)

    df.write.parquet(os.path.join(WarehouseLocation, 'TDIDF.parquet'))

    # wait, then run again
    time.sleep(SparkRunInterval)