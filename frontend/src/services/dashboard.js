import api from "./api";

export const getOverview = async () => (await api.get("/dashboard/overview")).data;
export const getTrend = async () => (await api.get("/dashboard/trend")).data;
export const getSeverity = async () => (await api.get("/dashboard/severity")).data;
export const getLogs = async (page = 1, pageSize = 10) =>
  (await api.get("/logs", { params: { page, page_size: pageSize } })).data;
export const getRules = async () => (await api.get("/rules")).data;
export const toggleRule = async (ruleId, enabled) =>
  (await api.patch(`/rules/${ruleId}`, { enabled })).data;
