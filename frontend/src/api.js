const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
async function request(path, options = {}, token) {
  const response = await fetch(`${API_URL}${path}`, {headers: {"Content-Type": "application/json", ...(token ? {Authorization: `Token ${token}`} : {})}, ...options});
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Ошибка соединения с сервером");
  return data;
}
export const createQuestion = (role, vacancy_description, mode, token) => request("/questions/", {method:"POST", body:JSON.stringify({role,vacancy_description,mode})}, token);
export const evaluateAnswer = (id, answer, token) => request(`/sessions/${id}/answer/`, {method:"POST", body:JSON.stringify({answer})}, token);
export const getHistory = token => request("/history/", {}, token);
export const login = (username,password) => request("/auth/login/", {method:"POST",body:JSON.stringify({username,password})});
export const register = (username,password) => request("/auth/register/", {method:"POST",body:JSON.stringify({username,password})});
