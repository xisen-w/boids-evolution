FROM debian:bookworm-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*
COPY build_runtime.py /build_runtime.py
RUN python3 /build_runtime.py

FROM scratch
COPY --from=build /runtime/ /
LABEL org.boids.sandbox="stdlib-only-v1"
USER 65534:65534
WORKDIR /sandbox/lib
ENV PATH=/usr/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONHASHSEED=0
ENTRYPOINT ["/usr/bin/python3", "-s", "-S", "-B"]
