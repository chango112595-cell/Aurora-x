# AuroraOS Packaging Guide

## Step-by-step guide and checklist

### Linux Native Install
```bash
# From repo root
bash installers/install-universal.sh --mode native --service systemd --token "your-secret-token"
# Start orchestration
./aurora.sh start
# Check status
./aurora.sh status
# View logs
tail -F aurora_logs/*.out.log
```

### Docker Install
```bash
bash installers/install-universal.sh --mode docker
bash docker/run.sh auroraos:latest
docker logs -f aurora
```

### Building Packages

#### Debian (.deb)
```bash
bash installers/linux/create-deb.sh 1.0.0 amd64
```

#### RPM
```bash
bash installers/linux/create-rpm.sh 1.0.0 x86_64
```

#### AppImage
```bash
bash installers/linux/create-appimage.sh
```

#### macOS Package
```bash
bash installers/macos/create-pkg.sh
```

#### Windows MSI
Requires WiX Toolset installed:
```powershell
candle.exe Product.wxs
light.exe Product.wixobj -o AuroraOS.msi
```

### Kubernetes / Helm
```bash
helm install aurora ./k8s/helm-chart
```
