FROM python:3.9
ENV PYTHONUNBUFFERED 1
# 添加这两行
RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev -y
# 添加 Debian 清华镜像源
RUN echo \
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free\
    > /etc/apt/sources.list

RUN mkdir /code
WORKDIR /code
# 添加 pip 清华镜像源
RUN pip install pip -U -i https://pypi.tuna.tsinghua.edu.cn/simple
ADD requirements.txt /code/
# 添加 pip 清华镜像源
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
ADD . /code/
