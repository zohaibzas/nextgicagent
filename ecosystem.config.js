const path = require("path");
const ROOT = __dirname;

module.exports = {
  apps: [
    {
      name: "nextgic-backend",
      script: "python",
      args: "-m uvicorn main:app --host 0.0.0.0 --port 8000",
      cwd: ROOT,
      interpreter: "none",
      env_file: path.join(ROOT, ".env"),
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      watch: false,
      error_file: path.join(ROOT, "logs", "backend-error.log"),
      out_file:   path.join(ROOT, "logs", "backend-out.log"),
    },
    {
      name: "nextgic-whatsapp",
      script: path.join(ROOT, "whatsapp", "bot.js"),
      cwd: path.join(ROOT, "whatsapp"),
      interpreter: "node",
      env_file: path.join(ROOT, ".env"),
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      watch: false,
      error_file: path.join(ROOT, "logs", "whatsapp-error.log"),
      out_file:   path.join(ROOT, "logs", "whatsapp-out.log"),
    }
  ]
};
