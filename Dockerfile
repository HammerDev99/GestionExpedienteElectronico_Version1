FROM python:3.9.6
WORKDIR /gestionexpedienteelectronico_version1
COPY requirements.txt /gestionexpedienteelectronico_version1/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /gestionexpedienteelectronico_version1/requirements.txt
COPY . /gestionexpedienteelectronico_version1
CMD bash -c "while true; do sleep 1; done"