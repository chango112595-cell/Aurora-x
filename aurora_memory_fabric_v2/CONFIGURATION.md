# Memory Fabric Configuration Guide

## Overview

The Aurora Memory Fabric v2 service now supports configurable host binding through environment variables, making it easy to deploy in different network configurations.

## Configuration

### Environment Variable

**`MEMORY_FABRIC_HOST`** - Sets the network interface to bind the Memory Fabric service to.

- **Default**: `127.0.0.1` (loopback interface, local access only)
- **Common values**:
  - `127.0.0.1` - Bind to localhost only (secure, local access)
  - `0.0.0.0` - Bind to all interfaces (allows remote access)
  - Specific IP address - Bind to a specific network interface

### Setting the Configuration

#### Via Environment Variable

```bash
# In .env file
MEMORY_FABRIC_HOST=127.0.0.1

# Or export directly
export MEMORY_FABRIC_HOST=0.0.0.0
```

#### Via Command Line

```bash
# Start service with custom host
python3 aurora_memory_fabric_v2/service.py 5004 0.0.0.0
```

#### Via Docker/Compose

```yaml
# docker-compose.yml
services:
  memory_fabric:
    environment:
      - MEMORY_FABRIC_HOST=0.0.0.0
```

## Usage Examples

### Local Development (Default)

```bash
# Uses 127.0.0.1 by default
python3 aurora_memory_fabric_v2/service.py
```

Output: `[MEMORY FABRIC V2] Running on http://127.0.0.1:5004`

### Docker Container

```bash
# Bind to all interfaces to accept connections from other containers
export MEMORY_FABRIC_HOST=0.0.0.0
python3 aurora_memory_fabric_v2/service.py
```

Output: `[MEMORY FABRIC V2] Running on http://0.0.0.0:5004`

### Specific Network Interface

```bash
# Bind to specific IP
export MEMORY_FABRIC_HOST=192.168.1.100
python3 aurora_memory_fabric_v2/service.py
```

Output: `[MEMORY FABRIC V2] Running on http://192.168.1.100:5004`

## Testing Configuration

Run the configuration test suite to verify your setup:

```bash
# Test default configuration
python3 -m pytest tests/test_memory_fabric_config.py -v

# Test with custom host
MEMORY_FABRIC_HOST=0.0.0.0 python3 -m pytest tests/test_memory_fabric_config.py -v
```

## Security Considerations

- **Production**: Use `127.0.0.1` for local-only access
- **Docker/Kubernetes**: Use `0.0.0.0` to allow inter-container communication
- **Development**: Either `127.0.0.1` or `0.0.0.0` depending on your needs
- Always use proper network security measures (firewall, VPN) when binding to `0.0.0.0`

## API Functions

All core functions now accept an optional `host` parameter:

```python
from aurora_memory_fabric_v2.service import (
    start_memory_fabric_service,
    check_existing_service,
    is_port_in_use
)

# Start with custom host
start_memory_fabric_service(port=5004, host='0.0.0.0')

# Check if service is running on specific host
is_running = check_existing_service(5004, '127.0.0.1')

# Check if port is available on specific host
port_available = not is_port_in_use(5004, '0.0.0.0')
```

## Troubleshooting

### Service won't start

- Check if the port is already in use: `lsof -i :5004`
- Verify the host binding is correct for your network setup
- Ensure firewall allows the binding (especially for `0.0.0.0`)

### Can't connect from remote

- Verify `MEMORY_FABRIC_HOST=0.0.0.0` is set
- Check firewall rules: `sudo ufw status`
- Ensure the service is actually bound to the expected interface: `netstat -tlnp | grep 5004`

### Permission denied

- Binding to privileged ports (<1024) requires root/sudo
- Use ports >1024 for non-privileged operation
- Check SELinux/AppArmor policies if applicable

## Migration from Hardcoded Values

Previous hardcoded references to `localhost` and `127.0.0.1` have been replaced with configurable options. If you were relying on these hardcoded values:

1. No action needed for default behavior (still uses `127.0.0.1`)
2. Set `MEMORY_FABRIC_HOST` environment variable for custom configurations
3. Update any service startup scripts to pass the `host` parameter if needed

## Related Files

- `aurora_memory_fabric_v2/service.py` - Main service implementation
- `tests/test_memory_fabric_config.py` - Configuration test suite
- `.env.example` - Example environment configuration
- `.env.template` - Template for environment setup
