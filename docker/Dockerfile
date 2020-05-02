FROM python:3.7

RUN echo "deb [ arch=amd64 ] https://downloads.skewed.de/apt buster main" >> /etc/apt/sources.list
RUN apt-key adv --keyserver keys.openpgp.org --recv-key 612DEFB798507F25
RUN apt-get update && apt-get install -y python3-graph-tool

WORKDIR /usr/local/lib/python3.7/site-packages
RUN touch dist-packages.pth
RUN echo "/usr/lib/python3/dist-packages" >> dist-packages.pth

WORKDIR /home

RUN pip install poetry