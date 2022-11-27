import AWS from "aws-sdk";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig(async () => {
  // Env
  const SecretsManager = new AWS.SecretsManager({
    apiVersion: "2017-10-17",
    region: process.env.AWS_REGION,
    credentials: { accessKeyId: process.env.AWS_ACCESS_KEY_ID, secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY },
  });
  // -- Set Public Vars
  await new Promise(async (resolve) =>
    SecretsManager.getSecretValue({ SecretId: process.env.TARGET_ENV }, (err, data) => {
      const secrets = JSON.parse(data.SecretString);
      process.env.VITE_TARGET_ENV = process.env.TARGET_ENV;
      process.env.VITE_GIDEON_API_URL = secrets.GIDEON_API_URL;
      resolve();
    })
  );
  // Config
  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: 1111,
    },
    preview: {
      port: 1111,
    },
  };
});
