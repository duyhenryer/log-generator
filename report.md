# Report: VictoriaLogs warning `missing _msg field`

## Bối cảnh
- **Mục tiêu**: sinh log để test hệ thống logging trên EKS, ingest vào VictoriaLogs bằng Vector.
- **Triệu chứng**: trong log của VictoriaLogs/vlinsert xuất hiện warning:
  - `missing _msg field; see https://docs.victoriametrics.com/victorialogs/keyconcepts/#message-field`

## Kết luận nhanh
- Ứng dụng `log-generator` đã in JSON có `_msg`, nhưng **Vector transform mặc định của chart** đã **nhét JSON vào field `.log`**, khiến `_msg` trở thành **`log._msg`** thay vì top-level `_msg`.
- Đồng thời transform lại **xóa `.message`**, làm mất fallback `message`.
- Vì thế VictoriaLogs không tìm được message theo `VL-Msg-Field` ⇒ báo “missing _msg field”.

## Pipeline hiện tại
```text
log-generator (stdout json) -> Vector kubernetes_logs (.message) -> VRL remap -> Vector sink elasticsearch -> /insert/elasticsearch -> VictoriaLogs
```

## Root cause chi tiết (Vector default chart)
Trong config default (và bản bạn deploy ban đầu):

- Transform:
  - `.log = parse_json(.message) ?? .message`
  - `del(.message)`

Khi `.message` là JSON (ví dụ `{ "_msg": "...", ... }`) thì:
- `.log` trở thành object `{ "_msg": "...", ... }`
- `_msg` lúc này nằm ở **`log._msg`**
- `.message` bị xoá

Trong khi header:
- `VL-Msg-Field: message,msg,_msg,log.msg,log.message,log`

Không có `log._msg` ⇒ VictoriaLogs không lấy được `_msg` ⇒ warning.

## Fix đã áp dụng

### 1) Fix ở log-generator: thêm `_time` (recommended)
Repo: `/home/duydo/Working/duy/Github/log-generator`

- `loggen/main.py`: thêm `_time` RFC3339/ISO8601 UTC vào output JSON.
- `tests/test_log_generator.py`: cập nhật test để assert `_time` hợp lệ.
- `README.md`: cập nhật example JSON để có `_msg` + `_time`.

Verify local (uv):
```bash
cd /home/duydo/Working/duy/Github/log-generator
uv run log-generator --format json --count 5
uv sync --extra test
uv run pytest -v
```

### 2) Fix ở Vector: Option A (Recommended) — flatten JSON ra root
Repo deploy: `/home/duydo/Working/Opswat/Bitbucket/fusion-kubernetes`

File: `infrastructure/staging/controllers/victoria-logs-cluster.yaml`

#### 2.1 Transform (VRL remap)
Mục tiêu: nếu `.message` là JSON object thì merge vào root để `_msg` giữ top-level.

```yaml
transforms:
  parser:
    type: remap
    inputs: [k8s]
    source: |
      # Option A: Flatten JSON into root so _msg stays at top-level
      parsed, err = parse_json(.message)
      if err == null && is_object(parsed) {
        . = merge(., parsed)
        del(.message)
      }
      # If parse failed, .message is kept as-is (VL-Msg-Field will use it)
```

#### 2.2 Headers (VictoriaLogs field mapping)
Sau khi flatten, `_msg` và `_time` nằm ở top-level nên mapping đơn giản:

```yaml
request:
  headers:
    VL-Msg-Field: _msg,message
    VL-Time-Field: _time,timestamp
```

## Checklist kiểm tra sau deploy trên EKS

### 1) Kiểm tra log-generator stdout có `_msg` + `_time`
```bash
kubectl -n logging logs deploy/log-generator --tail=50
```

### 2) Kiểm tra Vector agent có lỗi parse/remap không
```bash
kubectl -n logging logs -l app.kubernetes.io/name=vector --tail=200
```

### 3) Kiểm tra vlinsert không còn warning “missing _msg field”
```bash
kubectl -n logging logs -l app=vlinsert --tail=200 | grep -i "missing _msg" || true
```

## LogsQL query mẫu (dùng trên UI của VictoriaLogs / vlselect)

### Notes
- Trong UI, thường bạn chọn time range ở góc trên, nên không nhất thiết phải tự thêm `_time:...`.
- Nhưng thêm `_time:...` trong query giúp rõ ràng và copy/paste dễ.

### Query cơ bản
- **Log mới nhất 5 phút**:
  - `_time:5m`
- **Log mới nhất 1 giờ**:
  - `_time:1h`

### Filter theo Kubernetes metadata (thường Vector kubernetes_logs sẽ attach)
- **Theo namespace**:
  - `_time:1h kubernetes.pod_namespace:"logging"`
- **Theo container**:
  - `_time:1h kubernetes.container_name:"log-generator"`
- **Theo pod name (ví dụ)**:
  - `_time:1h kubernetes.pod_name:"log-generator-65c85dbbd7-2pq4c"`

### Xem nhanh các field chính
- **Lấy 50 log gần nhất của log-generator, chỉ show vài field**:
  - `_time:1h kubernetes.container_name:"log-generator" | sort by (_time) desc | limit 50 | fields _time, kubernetes.pod_name, kubernetes.container_name, _msg`

### Tìm lỗi / từ khoá
- **Tìm word `error` trong message 1 giờ gần nhất**:
  - `_time:1h error`
- **Bỏ qua các log có word `kubernetes`**:
  - `_time:1h error -kubernetes`

### Thống kê nhanh
- **Đếm log theo container trong 5 phút**:
  - `_time:5m | stats by (kubernetes.container_name) count() as logs | sort by (logs desc)`
- **Top stream có nhiều log nhất 5 phút** (nếu stream fields được set):
  - `_time:5m | top 10 by (_stream)`

## Kỳ vọng sau khi fix
- VictoriaLogs/vlinsert **không còn** warning `missing _msg field`.
- Log được ingest có `_msg` top-level và `_time` chuẩn, query theo thời gian/field ổn định hơn.

