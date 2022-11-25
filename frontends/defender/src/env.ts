/* eslint-disable prettier/prettier */

function get(global: string, which: string, isOptional = false) {
  // @ts-ignore
  if (!isOptional && !global && !process.env[which]) {
    throw new Error(`${which} is a required environment variable`);
  }
  // @ts-ignore
  return global || process.env[which]!;
}

// environment context
// @ts-ignore
export const getNodeEnv = () => get(NODE_ENV, "NODE_ENV");
export const isNodeTesting = () => {
  return getNodeEnv() === "testing" || getNodeEnv() === "test" || getNodeEnv() === "debug";
};
export const isNodeProduction = () => {
  return getNodeEnv() === "production" || getNodeEnv() === "prod";
};
export const isNodeDevelopment = () => {
  return getNodeEnv() === "development" || getNodeEnv() === "dev";
};
export const isNodeLocal = () => {
  return !isNodeProduction() && !isNodeDevelopment() && !isNodeTesting();
};

// TODO: GIDEON
// export const getGideonApiUrl = () => get(GIDEON_API_URL, "GIDEON_API_URL");
export const getGideonApiUrl = () => "http://localhost:3000";
