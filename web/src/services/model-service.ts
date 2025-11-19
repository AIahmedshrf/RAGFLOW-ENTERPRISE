import axios from 'axios';

const api_host = '/v1';

export const modelApi = {
  getModels: `${api_host}/models/registry`,
  getModelDetails: (id: string) => `${api_host}/models/registry/${id}`,
  registerModel: `${api_host}/models/registry`,
  updateModel: (id: string) => `${api_host}/models/registry/${id}`,
  deleteModel: (id: string) => `${api_host}/models/registry/${id}`,
  runBenchmark: (id: string) => `${api_host}/models/benchmark/${id}/run`,
  getBenchmarks: `${api_host}/models/benchmark`,
  compareModels: `${api_host}/models/benchmark/compare`,
  getModelVersions: (id: string) => `${api_host}/models/versions/${id}`,
  createModelVersion: (id: string) => `${api_host}/models/versions/${id}`,
  activateVersion: (id: string, versionId: number) => 
    `${api_host}/models/versions/${id}/${versionId}/activate`,
  rollbackVersion: (id: string) => `${api_host}/models/versions/${id}/rollback`,
};

export const getModels = () => axios.get(modelApi.getModels);

export const getModelDetails = (id: string) => axios.get(modelApi.getModelDetails(id));

export const registerModel = (data: any) => axios.post(modelApi.registerModel, data);

export const updateModel = (id: string, data: any) => 
  axios.put(modelApi.updateModel(id), data);

export const deleteModel = (id: string) => axios.delete(modelApi.deleteModel(id));

export const runBenchmark = (id: string, testType: string) =>
  axios.post(modelApi.runBenchmark(id), { test_type: testType });

export const getBenchmarks = (modelId?: string) =>
  axios.get(modelApi.getBenchmarks, { params: { model_id: modelId } });

export const compareModels = (modelIds: string[]) =>
  axios.post(modelApi.compareModels, { model_ids: modelIds });

export const getModelVersions = (id: string) =>
  axios.get(modelApi.getModelVersions(id));

export const createModelVersion = (id: string, data: any) =>
  axios.post(modelApi.createModelVersion(id), data);

export const activateVersion = (id: string, versionId: number) =>
  axios.post(modelApi.activateVersion(id, versionId));

export const rollbackVersion = (id: string) =>
  axios.post(modelApi.rollbackVersion(id));

export default {
  getModels,
  getModelDetails,
  registerModel,
  updateModel,
  deleteModel,
  runBenchmark,
  getBenchmarks,
  compareModels,
  getModelVersions,
  createModelVersion,
  activateVersion,
  rollbackVersion,
};
