# OpenSearch
OpenSearch is an open-source dashboard that we use to [automatically ingest](https://opensearch.org/docs/latest/observing-your-data/log-ingestion/) multiple logs to monitor Apache web traffic and the Scada-LTS access_log.

![](https://opensearch.org/docs/latest/images/la.png)

## Monitoring
For the monitoring of the web server and Scada-LTS
Multiple log files can be ingested but currently only `webserver/log/apache2/access.log` is being 

access.log
![](https://github.com/user-attachments/assets/4616222a-3eeb-4fc8-a8e8-b2597e3ab44a)

OpenSearch
![](https://github.com/user-attachments/assets/d1907fe0-043b-4e40-afd2-7fc72525f5fd)

## Setup
It comprises of the following containers:
- `opensearch-node`
- `opensearch-dashboards`
For log ingestion it also requires:
- `fluent-bit`
- `data-prepper`

The password for the OpenSearch dashboard is set in `opensearch/opensearch.env`, in our case `admin:Patat123!`. Note that it requires at least a lowercase character, a uppercase character, a number and a symbol otherwise it will not be accepted.
