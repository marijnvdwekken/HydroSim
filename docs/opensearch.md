# OpenSearch
OpenSearch is an open-source dashboard that we use to [automatically ingest](https://opensearch.org/docs/latest/observing-your-data/log-ingestion/) multiple log files to monitor Apache and Scada-LTS access logs.

## Screenshots
For example, the `webserver/log/apache2/access.log` log file is read and then visualized in our OpenSearch dashboard through a log ingestion workflow.

![](https://github.com/user-attachments/assets/4616222a-3eeb-4fc8-a8e8-b2597e3ab44a)

![](https://github.com/user-attachments/assets/d1907fe0-043b-4e40-afd2-7fc72525f5fd)

## Docker configuration
It comprises of the following containers:
- `opensearch-node` - The OpenSearch core
- `opensearch-dashboards` - The OpenSearch web interface

For log ingestion it also requires:
- `fluent-bit` - Log collector that collects log data and sends it to Data Prepper
- `data-prepper` - Receives and transforms the log data into a structure format and indexes it OpenSearch

**Data flow**

![](https://opensearch.org/docs/latest/images/la.png)

The credentials for the OpenSearch dashboard are set in `opensearch/opensearch.env`, in our case `admin:Patat123!`. Note that it requires at least a lowercase character, a uppercase character, a number and a symbol otherwise OpenSearch will not accepted it and refuse to run.

## Log ingestion workflow
The log file paths are defined in the `docker-compose.yaml`. For example The `/var/log/apache2` folder in the webserver container is mapped to `./webserver/log/apache2` on the host machine, which then allows the fluent-bit container to ingest the `./webserver/log/apache2/access.log` log file to `/var/log/test.log` in the OpenSearch container.
```yml
  webserver:
    container_name: webserver
    volumes:
      - ./webserver/log/apache2:/var/log/apache2
```
```yml
  fluent-bit:
    container_name: fluent-bit
    volumes:
      - ./webserver/log/apache2/access.log:/var/log/test.log
```

## Testing
When visiting the (WordPress) web server on http://127.0.0.1/80 the `access.log` will be updated and should be automatically ingested to the OpenSearch dashboard.

This can also be manually tested by adding a line to the log file. If might require using `sudo nano` instead if it requires elevated access, since the log files are supposed to be read-only.
```
echo '63.173.168.120 - - [04/Nov/2021:15:07:25 -0500] "GET /search/tag/list HTTP/1.0" 200 5003' >> ./webserver/log/apache2/access.log
```
