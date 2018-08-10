FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

RUN apt-get update
RUN apt-get install -y nginx

ADD requirements.txt /code/

RUN pip install -i https://pypi.douban.com/simple -r requirements.txt

ADD . /code/


CMD ["/bin/bash"]
