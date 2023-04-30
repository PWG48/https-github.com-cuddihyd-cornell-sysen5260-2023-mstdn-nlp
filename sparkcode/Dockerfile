FROM apache/spark-py:v3.4.0
FROM python:3.8
USER root
RUN python3 -m pip install --upgrade pip setuptools wheel                                                                                                                                                                                                
RUN python3 -m pip install -r /tmp/requirements.txt  
RUN python3 -m pip install numpy
ADD sparkcode/pyspark-tdidf.py /home/sparkcode/pyspark-tdidf.py
CMD [ "python", "-u", "/home/sparkcode/pyspark-tdidf.py" ]
