# Degiron 2009 Fig. 3 Magnus Submit Log

- Blueprint: `Optics_COMSOL_Runtime_zyz`
- Image: `docker://magnus-local/comsol-runtime:latest`
- Remote case dir: `/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3`
- GPU: not used (`gpu_type=cpu`, `gpu_count=0`).

## Staging

```json
{
  "dry_run": false,
  "remote_case_dir": "/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3",
  "files": [
    "Degiron2009Fig3ModeSweep.java",
    "run_config_smoke.json",
    "run_config_sweep.json",
    "postprocess_degiron_fig3.py"
  ]
}
```

## Jobs

| Case | Job ID | Status | Action | Output |
|---|---|---|---|---|
| `sweep` | `127fde3b1d9bcb34` | `Success` | `reused_success` | `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-sweep-v4` |

## Raw Records

```json
[
  {
    "case": "sweep",
    "run_id": "degiron-2009-fig3-sweep-v4",
    "job_id": "127fde3b1d9bcb34",
    "status": "Success",
    "dedupe_action": "reused_success",
    "input_file": "/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3/Degiron2009Fig3ModeSweep.java",
    "output_dir": "/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-sweep-v4",
    "cpu_count": 8,
    "memory_demand": "32G",
    "ephemeral_storage": "100G",
    "gpu_type": "cpu",
    "gpu_count": 0,
    "resource_check": null,
    "download": {
      "local_dir": "C:\\Users\\27370\\Desktop\\project\\optics_agent\\reproduction_test\\private\\Degiron_2009_NJP_Fig3\\magnus\\raw_logs\\degiron-2009-fig3-sweep-v4",
      "returncode": 0,
      "stderr_tail": ""
    },
    "postprocess": {
      "returncode": 0,
      "stdout": "{\n  \"run_dir\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-sweep-v4\",\n  \"raw_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-sweep-v4\\\\raw\\\\neff_sweep_raw_from_stdout.csv\",\n  \"final_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3\\\\results\\\\neff_sweep.csv\",\n  \"figure\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3\\\\results\\\\fig3_reproduction.png\",\n  \"row_count\": 62,\n  \"method\": \"surrogate_fallback\",\n  \"physical_reproduction_complete\": false,\n  \"branches\": [\n    \"antisymmetric\",\n    \"symmetric\"\n  ]\n}\n",
      "stderr": ""
    }
  }
]
```
