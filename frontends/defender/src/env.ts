// environment
export const getTargetEnv = (): string => {
  return import.meta.env.VITE_TARGET_ENV;
};
export const isTargetTesting = (): boolean => {
  return getTargetEnv() === "testing" || getTargetEnv() === "test" || getTargetEnv() === "debug";
};
export const isTargetProduction = (): boolean => {
  return getTargetEnv() === "production" || getTargetEnv() === "prod";
};
export const isTargetDevelopment = (): boolean => {
  return getTargetEnv() === "development" || getTargetEnv() === "dev";
};
export const isTargetLocal = (): boolean => {
  return !isTargetProduction() && !isTargetDevelopment() && !isTargetTesting();
};
// vars
export const getGideonApiUrl = (): string => {
  return import.meta.env.VITE_GIDEON_API_URL;
};
