import os

print("DXG present:", os.path.exists("/dev/dxg"))
print(
    "WSL libcuda present:",
    all(
        os.path.exists(p)
        for p in [
            "/usr/lib/wsl/lib/libcuda.so",
            "/usr/lib/wsl/lib/libcuda.so.1",
        ]
    ),
)
try:
    import torch

    print("Torch:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("Device:", torch.cuda.get_device_name(0))
        print("CUDA build:", torch.version.cuda)
except Exception as e:  # pragma: no cover - environment check only
    print("Torch check error:", repr(e))
