export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch('/api/' + path, {
    ...options,
    headers: options.body ? { 'Content-Type': 'application/json' } : undefined,
  });
  if (!response.headers.get('content-type')?.includes('application/json')) {
    throw new Error('Chưa kết nối được máy chủ tài khoản.');
  }
  if (!response.ok) {
    if (response.status === 401 && (path.startsWith("progress") || path.startsWith("admin"))) window.dispatchEvent(new Event("hci-session-expired"));
    const { message } = await response.json();
    throw new ApiError(response.status, message);
  }
  return response.json();
}

export function writeApi<T>(path: string, method: 'POST' | 'PUT', data?: object) {
  return api<T>(path, { method, body: data && JSON.stringify(data) });
}
