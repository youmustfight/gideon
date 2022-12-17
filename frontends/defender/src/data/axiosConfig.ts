/* eslint-env browser */
import axios from "axios";
import * as Env from "../env";
import { LOCAL_STORAGE_KEY_API_TOKEN } from "./localStorageKeys";

axios.defaults.baseURL = Env.getGideonApiUrl();

axios.interceptors.request.use((config) => {
  const apiToken = localStorage.getItem(LOCAL_STORAGE_KEY_API_TOKEN);
  if (apiToken) {
    // @ts-ignore
    config.headers.Authorization = apiToken;
  }
  return config;
});
