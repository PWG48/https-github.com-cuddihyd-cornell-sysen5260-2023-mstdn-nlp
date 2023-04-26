FROM apache/spark-py:v3.4.0
FROM python:3.8
USER root
ADD extractor/tool-extractor.py /home/tool-extractor/tool-extractor.py
RUN pip install requests
CMD [ "python", "-u", "/home/tool-extractor/tool-extractor.py" ]
