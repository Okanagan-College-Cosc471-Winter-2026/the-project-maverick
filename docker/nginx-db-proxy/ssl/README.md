# SSL Certificates

Place your SSL certificate files here:

- `server.crt` — certificate (PEM format)
- `server.key` — private key (PEM format)

## Option 1: Let's Encrypt (production)

```bash
certbot certonly --standalone -d your.domain.com
cp /etc/letsencrypt/live/your.domain.com/fullchain.pem docker/nginx-db-proxy/ssl/server.crt
cp /etc/letsencrypt/live/your.domain.com/privkey.pem   docker/nginx-db-proxy/ssl/server.key
```

## Option 2: Self-signed (testing only)

```bash
openssl req -x509 -newkey rsa:4096 -keyout docker/nginx-db-proxy/ssl/server.key \
  -out docker/nginx-db-proxy/ssl/server.crt -days 365 -nodes \
  -subj "/CN=localhost"
```

## Connecting

Clients must use `sslmode=require` (or higher) in their connection string:

```
postgresql://user:pass@your.host:5432/dbname?sslmode=require
```
