# Cloudflare Tunnels - The GitOps > [!WARNING]

Credit to: [Kubecraft Community](https://www.skool.com/kubecraft)

## Install local client

Install cloudflare locally: 
```
brew install Cloudflared

```
More install options: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

## Tunnel config

Run the below command to build your tunnel: 

```bash
cloudflared tunnel create ldpi
```

## K8s

Cloudflare provides a [config file for running CloudFlare Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/deploy-tunnels/deployment-guides/kubernetes/),  but their default option is to hardcode the tunnel token, which is not GitOps friendly. 

Fear not, we can build this out with a configmap and using secrets. 
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudflared
spec:
  selector:
    matchLabels:
      app: cloudflared
  replicas: 2 # You could also consider elastic scaling for this deployment
  template:
    metadata:
      labels:
        app: cloudflared
    spec:
      containers:
      - name: cloudflared
        image: cloudflare/cloudflared:latest
        args:
        - tunnel

        # Points cloudflared to the config file, which configures what
        # cloudflared will actually do. This file is created by a ConfigMap
        # below.
        - --config
        - /etc/cloudflared/config/config.yaml
        - run
        livenessProbe:
          httpGet:
            # Cloudflared has a /ready endpoint which returns 200 if and only if
            # it has an active connection to the edge.
            path: /ready
            port: 2000
          failureThreshold: 1
          initialDelaySeconds: 10
          periodSeconds: 10
        volumeMounts:
        - name: config
          mountPath: /etc/cloudflared/config
          readOnly: true
        # Each tunnel has an associated "credentials file" which authorizes machines
        # to run the tunnel. cloudflared will read this file from its local filesystem,
        # and it'll be stored in a k8s secret.
        - name: creds
          mountPath: /etc/cloudflared/creds
          readOnly: true
      volumes:
      - name: creds
        secret:
          secretName: tunnel-credentials

      # Create a config.yaml file from the ConfigMap below.
      - name: config
        configMap:
          name: cloudflared
          items:
          - key: config.yaml
            path: config.yaml
---
# This ConfigMap is just a way to define the cloudflared config.yaml file in k8s.
# It's useful to define it in k8s, rather than as a stand-alone .yaml file, because
# this lets you use various k8s templating solutions (e.g. Helm charts) to
# parameterize your config, instead of just using string literals.
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudflared
data:
  config.yaml: |
    # Name of the tunnel you want to run
    
    tunnel: ld 

    credentials-file: /etc/cloudflared/creds/credentials.json

    # Serves the metrics server under /metrics and the readiness server under /ready
    metrics: 0.0.0.0:2000
    no-autoupdate: true

    ingress:
    - hostname: ld.phin3has.me #Set your CNAME record here 
      service: http://linkding:9090

    # This rule sends traffic to the built-in hello-world HTTP server. This can help debug connectivity
    # issues. If hello.example.com resolves and tunnel.example.com does not, then the problem is
    # in the connection from cloudflared to your local service, not from the internet to cloudflared.
    - hostname: hello.example.com
      service: hello_world
    # This rule matches any traffic which didn't match a previous rule, and responds with HTTP 404.
    - service: http_status:404
```

```
