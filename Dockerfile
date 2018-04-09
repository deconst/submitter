FROM alpine:3.7
MAINTAINER Laura Santamaria <laura.santamaria@rackspace.com>

RUN apk add --no-cache python3
RUN python3 -m ensurepip
RUN ln -s /usr/bin/python3 /usr/bin/python && \
  ln -s /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip

RUN adduser -D -g "" -u 1000 submitter

RUN mkdir -p /submitter
RUN chown -R submitter:submitter /submitter
WORKDIR submitter

COPY ./requirements.txt /submitter/requirements.txt
RUN pip install -r requirements.txt
COPY . /submitter

VOLUME /workspace
USER submitter
CMD ["python", "-m", "submitter"]
