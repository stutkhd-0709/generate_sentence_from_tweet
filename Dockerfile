FROM python:3.8

WORKDIR /work

RUN apt-get update \
    && apt-get install -y mecab mecab-utils libmecab-dev \
    && pip install -U pip

RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git /mecab-ipadic-neologd \
    && /mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -u -n -y -p /var/lib/mecab/dic/mecab-ipadic-neologd \
    && update-alternatives --install /var/lib/mecab/dic/debian mecab-dictionary /var/lib/mecab/dic/mecab-ipadic-neologd 100 \
    && rm -rf /mecab-ipadic-neologd

COPY requirements.txt /work/

RUN pip install -r requirements.txt