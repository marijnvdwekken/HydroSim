FROM opensearchproject/data-prepper:latest

# Add config file and pipelines dir from build context
COPY --chown=data_prepper:data_prepper data-prepper-config.yaml /usr/share/data-prepper/config/data-prepper-config.yaml
COPY --chown=data_prepper:data_prepper log_pipeline.yaml /usr/share/data-prepper/pipelines/log_pipeline.yaml
