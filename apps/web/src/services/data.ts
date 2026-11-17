import type { SignMetadata } from '../types/sign';

export async function loadSigns(signal?: AbortSignal): Promise<SignMetadata[]> {
  const response = await fetch('/data/signs.json', { signal });
  if (!response.ok) {
    throw new Error(`Không thể tải sign metadata: HTTP ${response.status}`);
  }
  return response.json() as Promise<SignMetadata[]>;
}
