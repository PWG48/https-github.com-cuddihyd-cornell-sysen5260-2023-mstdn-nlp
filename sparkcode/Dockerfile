FROM apache/spark-py:v3.4.0
FROM python:3.10
USER root
RUN python3 -m pip install --upgrade pip setuptools wheel    
RUN pip install pyspark
RUN apt-get update
RUN apt-get install default-jdk -y                                                                                                                                                                                            
#RUN python3 -m pip install -r requirements.txt  
RUN python3 -m pip install numpy
COPY ./ /home/sparkcode/
CMD [ "python", "-u", "/home/sparkcode/tfidf/pyspark-tdidf.py" ]
