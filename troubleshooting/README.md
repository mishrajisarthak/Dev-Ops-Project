# Kubernetes Troubleshooting Scenarios & Runbook

This guide contains two deliberate failure scenarios to demonstrate root-cause analysis and remediation on Kubernetes.

---

## Scenario 1: ImagePullBackOff (Faulty Container Image Tag)

### 1. Apply Faulty Manifest
```bash
kubectl apply -f troubleshooting/broken-image.yaml
```

### 2. Diagnose Failure
```bash
# Check pod status
kubectl get pods -n folio

# Inspect events
kubectl describe pod -l app=broken-image -n folio
```
**Expected Observation:**
Under `Events:`, Kubernetes reports `Failed to pull image "ghcr.io/jash2511/folio-backend:v999-does-not-exist": rpc error: code = NotFound`.

### 3. Remediate
```bash
kubectl set image deployment/broken-backend-image app=ghcr.io/jash2511/folio-backend:latest -n folio
kubectl rollout status deployment/broken-backend-image -n folio
```

---

## Scenario 2: Service Routing Failure (Mismatched Selector Labels)

### 1. Apply Faulty Service
```bash
kubectl apply -f troubleshooting/broken-service.yaml
```

### 2. Diagnose Failure
```bash
# Check service endpoints
kubectl get endpoints broken-backend-service -n folio
```
**Expected Observation:**
`ENDPOINTS` column is `<none>` because the service selector (`typo-backend-selector-no-endpoints`) does not match any running pods.

### 3. Inspect Pod Labels
```bash
kubectl get pods -n folio --show-labels
```

### 4. Remediate
Update the service selector in `troubleshooting/broken-service.yaml` to match `app: folio-backend` and re-apply:
```bash
kubectl patch svc broken-backend-service -n folio -p '{"spec":{"selector":{"app":"folio-backend"}}}'
kubectl get endpoints broken-backend-service -n folio
```
