module.exports = {
  apps: [
    {
      name: "migracion-impuestos-scheduler",
      script: ".\\.venv\\Scripts\\python.exe",
      args: "scheduler.py",
      cwd: __dirname,
      interpreter: "none",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      time: true,
      merge_logs: true,
      out_file: ".\\logs\\pm2-out.log",
      error_file: ".\\logs\\pm2-error.log",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
