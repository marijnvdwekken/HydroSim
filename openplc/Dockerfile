FROM debian:bookworm-slim   

# Ref https://github.com/thiagoralves/OpenPLC_v3/blob/master/Dockerfile 
ARG script
ARG database

# Install applications
RUN apt-get update && apt-get -y \
install git sqlite3 python3 python3-pip python3-venv \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Install OpenPLC_v3
RUN git clone https://github.com/thiagoralves/OpenPLC_v3.git
WORKDIR /OpenPLC_v3
RUN ./install.sh docker
RUN sed -i 's/`pkg-config --cflags --libs libmodbus` -lsnap7/`pkg-config --cflags --libs libmodbus` -lrt -lsnap7/' /OpenPLC_v3/webserver/scripts/compile_program.sh
RUN mkdir -p /docker_persistent /docker_persistent/st_files /workdir \
    && touch /docker_persistent/mbconfig.cfg \
    && touch /docker_persistent/persistent.file \
    && cp /OpenPLC_v3/webserver/openplc.db /docker_persistent/openplc.db \
    && mv /OpenPLC_v3/webserver/openplc.db /OpenPLC_v3/webserver/openplc_default.db \
    && cp /OpenPLC_v3/webserver/dnp3.cfg /docker_persistent/dnp3.cfg \
    && mv /OpenPLC_v3/webserver/dnp3.cfg /OpenPLC_v3/webserver/dnp3_default.cfg \
    && cp -r /OpenPLC_v3/webserver/st_files/ /docker_persistent/st_files/ \
    && mv /OpenPLC_v3/webserver/st_files /OpenPLC_v3/webserver/st_files_default \
    && cp /OpenPLC_v3/webserver/active_program /docker_persistent/active_program \
    && mv /OpenPLC_v3/webserver/active_program /OpenPLC_v3/webserver/active_program_default \
    && ln -s /docker_persistent/mbconfig.cfg /OpenPLC_v3/webserver/mbconfig.cfg \
    && ln -s /docker_persistent/persistent.file /OpenPLC_v3/webserver/persistent.file \
    && ln -s /docker_persistent/openplc.db /OpenPLC_v3/webserver/openplc.db \
    && ln -s /docker_persistent/dnp3.cfg /OpenPLC_v3/webserver/dnp3.cfg \
    && ln -s /docker_persistent/st_files /OpenPLC_v3/webserver/st_files \
    && ln -s /docker_persistent/active_program /OpenPLC_v3/webserver/active_program \
    && ln -s /OpenPLC_v3/webserver /workdir/webserver

# copy PLC script and database script over
RUN mkdir /OpenPLC_v3/scripts
COPY $script /OpenPLC_v3/scripts/script.st
COPY $database /OpenPLC_v3/database.sh
COPY entrypoint.sh /OpenPLC_v3/entrypoint.sh
RUN chmod +x /OpenPLC_v3/entrypoint.sh /OpenPLC_v3/database.sh

EXPOSE 502
EXPOSE 8080
EXPOSE 20000
EXPOSE 43628

ENTRYPOINT ["/OpenPLC_v3/entrypoint.sh"]
