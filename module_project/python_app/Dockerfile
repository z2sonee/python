FROM python:3.7.9-alpine3.12

WORKDIR /usr/src

RUN pip install pymysql
RUN pip install prettytable

COPY ./Module_project.py ./

CMD ["python", "Module_project.py"]