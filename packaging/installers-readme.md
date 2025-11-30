Aurora Installers quick guide
- Linux native: installers/install-native-linux.sh USER TOKEN [systemd]
- macOS native: installers/install-macos.sh TOKEN
- Windows: run installers/install-windows.ps1 (Run as Admin for service)
- Docker: installers/install-universal.sh --mode docker
- Edge image: edge/build-edge-image.sh arm64
- Create .deb: packaging/fpm-deb.sh 1.0.0 amd64
- Sign update: signing/gpg-sign.sh path/to/update.tar.gz
- Verify update: signing/verify-sign.sh path/to/update.tar.gz
