# Aurora Advanced Orchestration System - Recovery Runbook

## Quick Reference

### Emergency Commands
```bash
# Stop everything immediately
./aurora_orchestrator.sh stop

# Full system restart
./aurora_orchestrator.sh restart

# Check what's running
./aurora_orchestrator.sh check

# View detailed status
./aurora_orchestrator.sh status

# Watch live logs
./aurora_orchestrator.sh logs
```

### Rollback to Manual Mode
If the orchestration system fails, fall back to manual commands:

```bash
# Stop supervisor
pkill -f aurora_supervisor

# Start services manually (from root dir)
source .venv/bin/activate
nohup uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001 > /tmp/manual_5001.log 2>&1 &
nohup python -m aurora_x.self_learn_server > /tmp/manual_5002.log 2>&1 &
npm run dev &  # Keep this terminal open
```

## Auto-Start on Container Boot

### Option 1: Add to .bashrc (Current Method)
```bash
# Add this line to ~/.bashrc
[ -f /workspaces/Aurora-x/aurora_autostart.sh ] && /workspaces/Aurora-x/aurora_autostart.sh &
```

### Option 2: systemd User Service (If Available)
```bash
# Create: ~/.config/systemd/user/aurora.service
[Unit]
Description=Aurora Service Orchestrator
After=network.target

[Service]
Type=forking
ExecStart=/workspaces/Aurora-x/aurora_orchestrator.sh start
ExecStop=/workspaces/Aurora-x/aurora_orchestrator.sh stop
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=default.target

# Enable:
systemctl --user enable aurora.service
systemctl --user start aurora.service
```

### Option 3: Cron @reboot
```bash
# Add to crontab:
@reboot sleep 10 && /workspaces/Aurora-x/aurora_orchestrator.sh start
```

## Common Issues & Solutions

### Issue: Service won't start
**Symptoms:** Port shows DOWN, supervisor logs show errors

**Fix:**
1. Check dependencies: `pip list | grep -E "uvicorn|fastapi|psutil"`
2. Verify virtual environment: `source .venv/bin/activate`
3. Check port conflicts: `lsof -i :<port>`
4. Review logs: `tail -50 /tmp/aurora_supervisor.log`

### Issue: Services crash immediately
**Symptoms:** Restart counter increases, status shows "crashed"

**Fix:**
1. Check individual service logs in `/tmp/`
2. Test service manually to see actual error
3. Verify config file: `cat aurora_supervisor_config.json`
4. Check disk space: `df -h`

### Issue: Dashboard won't load
**Symptoms:** Port 9090 not accessible

**Fix:**
1. Start dashboard manually: `python3 tools/aurora_health_dashboard.py`
2. Check if port is blocked: `lsof -i :9090`
3. Try different port in dashboard script

### Issue: High restart counts
**Symptoms:** Services constantly restarting

**Fix:**
1. Check health endpoints are responding correctly
2. Increase restart_delay in config
3. Check for resource exhaustion: `top`, `free -h`
4. Review exponential backoff settings

## Performance Tuning

### Adjust Restart Behavior
Edit `aurora_supervisor_config.json`:
```json
{
  "max_restarts": 10,  // Increase if needed
  "restart_delay": 5,   // Base delay in seconds
  "health_check_interval": 15  // How often to check health
}
```

### Resource Limits
Add to supervisor service configs:
```python
# In aurora_supervisor.py, add resource constraints
import resource
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))  # 2GB memory limit
```

## Monitoring Best Practices

1. **Daily Health Check**
   ```bash
   ./aurora_orchestrator.sh check
   ```

2. **Weekly Full Status Review**
   ```bash
   ./aurora_orchestrator.sh status | tee /tmp/weekly-check-$(date +%Y%m%d).txt
   ```

3. **Watch for Patterns**
   - High restart counts indicate instability
   - Increasing memory usage suggests leaks
   - Frequent health check failures need investigation

## Backup & Restore

### Save Current Configuration
```bash
cp aurora_supervisor_config.json aurora_supervisor_config.backup.json
cp .venv/pyvenv.cfg .venv/pyvenv.cfg.backup
```

### Restore from Backup
```bash
./aurora_orchestrator.sh stop
cp aurora_supervisor_config.backup.json aurora_supervisor_config.json
./aurora_orchestrator.sh start
```

## Testing Disaster Recovery

### Simulate Service Crash
```bash
# Kill a specific service
pkill -f "uvicorn aurora_x.serve"

# Watch auto-restart happen
watch -n 1 './aurora_orchestrator.sh check'
```

### Simulate Complete Failure
```bash
# Kill supervisor
pkill -f aurora_supervisor

# Services should stop gracefully
# Restart:
./aurora_orchestrator.sh start
```

## Contact & Escalation

If all recovery attempts fail:
1. Save logs: `tar -czf aurora-logs-$(date +%Y%m%d).tar.gz /tmp/aurora_*.log`
2. Document issue in `logs/aurora-ops-journal.md`
3. Fall back to manual service startup
4. Review with team before making config changes

---

**Last Updated:** 2025-11-01  
**Maintained By:** Aurora
