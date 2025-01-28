# OpenSearch
OpenSearch is an open-source dashboard that we use to [automatically ingest](https://opensearch.org/docs/latest/observing-your-data/log-ingestion/) multiple log files to monitor Apache and Scada-LTS access logs.

## Screenshots
For example, the `webserver/log/apache2/access.log` log file is read and can be visualized in our OpenSearch dashboard.

![](https://github.com/user-attachments/assets/4616222a-3eeb-4fc8-a8e8-b2597e3ab44a)

![](https://github.com/user-attachments/assets/d1907fe0-043b-4e40-afd2-7fc72525f5fd)

## Docker configuration
![](https://opensearch.org/docs/latest/images/la.png)

It comprises of the following containers:
- `opensearch-node`
- `opensearch-dashboards`

For log ingestion it also requires:
- `fluent-bit`
- `data-prepper`

The credentials for the OpenSearch dashboard are set in `opensearch/opensearch.env`, in our case `admin:Patat123!`. Note that it requires at least a lowercase character, a uppercase character, a number and a symbol otherwise it will not be accepted.
