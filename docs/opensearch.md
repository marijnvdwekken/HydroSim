# OpenSearch
OpenSearch is an open-source dashboard that we use to [automatically ingest](https://opensearch.org/docs/latest/observing-your-data/log-ingestion/) multiple logs to monitor Apache web traffic and the Scada-LTS access_log.

![](https://opensearch.org/docs/latest/images/la.png)

## Setup
With `docker compose up` OpenSearch should be set up and configured properly. It comprises of the following containers:
- `opensearch-node`
- `opensearch-dashboards`
For log ingestion it also requires:
- `fluent-bit`
- `data-prepper`

The password for the OpenSearch dashboard is set in `opensearch/opensearch.env`, in our case `admin:Patat123!`. Note that it requires at least a lowercase character, a uppercase character, a number and a symbol otherwise it will not be accepted.
