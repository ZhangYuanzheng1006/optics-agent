# Degiron 2009 Fig. 3 V2 Magnus Submit Log

- Blueprint: `Optics_COMSOL_Runtime_zyz`
- Image: `docker://magnus-local/comsol-runtime:latest`
- Remote case dir: `/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2`
- GPU: not used (`gpu_type=cpu`, `gpu_count=0`).
- Method: `scalar_tm_hx_pde` plus isolated `wave_optics_mode_analysis_probe`; neither is full physical Fig. 3 reproduction unless validated separately.

## Staging

```json
{
  "dry_run": false,
  "remote_case_dir": "/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2",
  "files": [
    "Degiron2009Fig3V2ScalarPdeLadderSmoke.java",
    "Degiron2009Fig3V2ScalarPdeCoupledSweep.java",
    "Degiron2009Fig3V2ModeAnalysisSu8Smoke.java",
    "run_config_ladder_smoke.json",
    "run_config_coupled_sweep.json",
    "run_config_mode_su8_smoke.json",
    "postprocess_degiron_fig3_v2.py"
  ]
}
```

## Jobs

| Case | Job ID | Status | Action | Output |
|---|---|---|---|---|
| `ladder_smoke` | `f886f496f107e1b7` | `Success` | `reused_success` | `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-ladder-smoke-v6` |
| `mode_su8_smoke` | `0e64e432914254d7` | `Success` | `reused_success` | `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-mode-su8-smoke-v2` |
| `coupled_sweep` | `f6c6748bf850a69f` | `Success` | `reused_success` | `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-coupled-sweep-v1` |

## Raw Records

```json
[
  {
    "case": "ladder_smoke",
    "run_id": "degiron-2009-fig3-v2-ladder-smoke-v6",
    "job_id": "f886f496f107e1b7",
    "status": "Success",
    "dedupe_action": "reused_success",
    "input_file": "/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2/Degiron2009Fig3V2ScalarPdeLadderSmoke.java",
    "output_dir": "/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-ladder-smoke-v6",
    "cpu_count": 8,
    "memory_demand": "32G",
    "ephemeral_storage": "100G",
    "gpu_type": "cpu",
    "gpu_count": 0,
    "resource_check": null,
    "download": {
      "local_dir": "C:\\Users\\27370\\Desktop\\project\\optics_agent\\reproduction_test\\private\\Degiron_2009_NJP_Fig3_v2\\magnus\\raw_logs\\degiron-2009-fig3-v2-ladder-smoke-v6",
      "returncode": 0,
      "stderr_tail": ""
    },
    "postprocess": {
      "returncode": 0,
      "stdout": "{\n  \"run_dir\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-v2-ladder-smoke-v6\",\n  \"raw_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-v2-ladder-smoke-v6\\\\raw\\\\neff_v2_raw_from_stdout.csv\",\n  \"final_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\results\\\\ladder_smoke_neff.csv\",\n  \"figure\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\results\\\\ladder_smoke_neff.png\",\n  \"row_count\": 56,\n  \"error_count\": 0,\n  \"errors\": [],\n  \"methods\": [\n    \"scalar_tm_hx_pde\"\n  ],\n  \"cases\": [\n    \"coupled\",\n    \"isolated_au\",\n    \"isolated_su8\"\n  ],\n  \"coupled_row_count\": 24,\n  \"plausible_row_count\": 56,\n  \"physical_reproduction_complete\": false,\n  \"physical_status\": \"scalar_tm_hx_pde_candidate\"\n}\n",
      "stderr": ""
    }
  },
  {
    "case": "mode_su8_smoke",
    "run_id": "degiron-2009-fig3-v2-mode-su8-smoke-v2",
    "job_id": "0e64e432914254d7",
    "status": "Success",
    "dedupe_action": "reused_success",
    "input_file": "/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2/Degiron2009Fig3V2ModeAnalysisSu8Smoke.java",
    "output_dir": "/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-mode-su8-smoke-v2",
    "cpu_count": 8,
    "memory_demand": "32G",
    "ephemeral_storage": "100G",
    "gpu_type": "cpu",
    "gpu_count": 0,
    "resource_check": null,
    "download": {
      "local_dir": "C:\\Users\\27370\\Desktop\\project\\optics_agent\\reproduction_test\\private\\Degiron_2009_NJP_Fig3_v2\\magnus\\raw_logs\\degiron-2009-fig3-v2-mode-su8-smoke-v2",
      "returncode": 0,
      "stderr_tail": ""
    },
    "postprocess": {
      "returncode": 0,
      "stdout": "{\n  \"run_dir\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-v2-mode-su8-smoke-v2\",\n  \"raw_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-v2-mode-su8-smoke-v2\\\\raw\\\\neff_v2_raw_from_stdout.csv\",\n  \"final_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\results\\\\degiron-2009-fig3-v2-mode-su8-smoke-v2_neff.csv\",\n  \"figure\": \"\",\n  \"row_count\": 0,\n  \"error_count\": 2,\n  \"errors\": [\n    \"isolated_su8_mode,5.6000,shift_kind=neff: Exception: \\tcom.comsol.nativejni.FlNativeException: COMSOL ����ʧ�ܡ� \\t(rethrown as com.comsol.util.exceptions.FlException) Messages: \\tThe following feature has encountered a problem \\t- Feature: ����ֵ����� 1 (sol1/e1)  \\tFailed to compute the matrix factorization in the eigensolver  \\tTry to search for eigenvalues around a different shift value  \\tCOMSOL assertion failure ; shift_kind=beta: Exception: \\tcom.comsol.nativejni.FlNativeException: COMSOL ����ʧ�ܡ� \\t(rethrown as com.comsol.util.exceptions.FlException) Messages: \\tThe following feature has encountered a problem \\t- Feature: ����ֵ����� 1 (sol1/e1)  \\tFailed to compute the matrix factorization in the eigensolver  \\tTry to search for eigenvalues around a different shift value  \\tCOMSOL assertion failure ; shift_kind=plain: Exception: \\tcom.comsol.nativejni.FlNativeException: COMSOL ����ʧ�ܡ� \\t(rethrown as com.comsol.util.exceptions.FlException) Messages: \\tThe following feature has encountered a problem \\t- Feature: ����ֵ����� 1 (sol1/e1)  \\tFailed to compute the matrix factorization in the eigensolver  \\tTry to search for eigenvalues around a different shift value  \\tCOMSOL assertion failure ;\",\n    \"isolated_su8_mode,6.6000,shift_kind=neff: Exception: \\tcom.comsol.nativejni.FlNativeException: COMSOL ����ʧ�ܡ� \\t(rethrown as com.comsol.util.exceptions.FlException) Messages: \\tThe following feature has encountered a problem \\t- Feature: ����ֵ����� 1 (sol1/e1)  \\tFailed to compute the matrix factorization in the eigensolver  \\tTry to search for eigenvalues around a different shift value  \\tCOMSOL assertion failure ; shift_kind=beta: Exception: \\tcom.comsol.nativejni.FlNativeException: COMSOL ����ʧ�ܡ� \\t(rethrown as com.comsol.util.exceptions.FlException) Messages: \\tThe following feature has encountered a problem \\t- Feature: ����ֵ����� 1 (sol1/e1)  \\tFailed to compute the matrix factorization in the eigensolver  \\tTry to search for eigenvalues around a different shift value  \\tCOMSOL assertion failure ; shift_kind=plain: Exception: \\tcom.comsol.nativejni.FlNativeException: COMSOL ����ʧ�ܡ� \\t(rethrown as com.comsol.util.exceptions.FlException) Messages: \\tThe following feature has encountered a problem \\t- Feature: ����ֵ����� 1 (sol1/e1)  \\tFailed to compute the matrix factorization in the eigensolver  \\tTry to search for eigenvalues around a different shift value  \\tCOMSOL assertion failure ;\"\n  ],\n  \"methods\": [],\n  \"cases\": [],\n  \"coupled_row_count\": 0,\n  \"plausible_row_count\": 0,\n  \"physical_reproduction_complete\": false,\n  \"physical_status\": \"no_physical_rows\"\n}\n",
      "stderr": ""
    }
  },
  {
    "case": "coupled_sweep",
    "run_id": "degiron-2009-fig3-v2-coupled-sweep-v1",
    "job_id": "f6c6748bf850a69f",
    "status": "Success",
    "dedupe_action": "reused_success",
    "input_file": "/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2/Degiron2009Fig3V2ScalarPdeCoupledSweep.java",
    "output_dir": "/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-coupled-sweep-v1",
    "cpu_count": 8,
    "memory_demand": "32G",
    "ephemeral_storage": "100G",
    "gpu_type": "cpu",
    "gpu_count": 0,
    "resource_check": null,
    "download": {
      "local_dir": "C:\\Users\\27370\\Desktop\\project\\optics_agent\\reproduction_test\\private\\Degiron_2009_NJP_Fig3_v2\\magnus\\raw_logs\\degiron-2009-fig3-v2-coupled-sweep-v1",
      "returncode": 0,
      "stderr_tail": ""
    },
    "postprocess": {
      "returncode": 0,
      "stdout": "{\n  \"run_dir\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-v2-coupled-sweep-v1\",\n  \"raw_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\magnus\\\\raw_logs\\\\degiron-2009-fig3-v2-coupled-sweep-v1\\\\raw\\\\neff_v2_raw_from_stdout.csv\",\n  \"final_csv\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\results\\\\coupled_neff_sweep.csv\",\n  \"figure\": \"C:\\\\Users\\\\27370\\\\Desktop\\\\project\\\\optics_agent\\\\reproduction_test\\\\private\\\\Degiron_2009_NJP_Fig3_v2\\\\results\\\\fig3_reproduction_v2.png\",\n  \"row_count\": 248,\n  \"error_count\": 0,\n  \"errors\": [],\n  \"methods\": [\n    \"scalar_tm_hx_pde\"\n  ],\n  \"cases\": [\n    \"coupled\"\n  ],\n  \"coupled_row_count\": 248,\n  \"plausible_row_count\": 248,\n  \"physical_reproduction_complete\": false,\n  \"physical_status\": \"scalar_tm_hx_pde_candidate\"\n}\n",
      "stderr": ""
    }
  }
]
```
