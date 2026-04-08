FROM postgres:18.1-alpine3.23

ARG PG_PARTMAN_VERSION=v5.2.4
ARG PG_PARTMAN_BGW_DBNAME=auth
ARG PG_PARTMAN_BGW_INTERVAL=3600
ARG PG_PARTMAN_BGW_ROLE=postgres

RUN set -eux; \
    apk add --no-cache --virtual .build-deps \
      build-base \
      clang19 \
      llvm19 \
      git \
      postgresql18-dev; \
    git clone --depth 1 --branch "${PG_PARTMAN_VERSION}" \
      https://github.com/pgpartman/pg_partman.git /tmp/pg_partman; \
    make -C /tmp/pg_partman install; \
    rm -rf /tmp/pg_partman; \
    apk del .build-deps; \
    printf "\n# pg_partman bgw\nshared_preload_libraries = 'pg_partman_bgw'\npg_partman_bgw.dbname = '%s'\npg_partman_bgw.interval = %s\npg_partman_bgw.role = '%s'\n" \
      "${PG_PARTMAN_BGW_DBNAME}" \
      "${PG_PARTMAN_BGW_INTERVAL}" \
      "${PG_PARTMAN_BGW_ROLE}" \
      >> /usr/local/share/postgresql/postgresql.conf.sample
