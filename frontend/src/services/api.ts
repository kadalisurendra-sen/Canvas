/**
 * Shared fetch wrapper that always includes credentials (cookies).
 * All API calls go through Vite proxy (relative URLs) so cookies work same-origin.
 */
export async function apiFetch(
  url: string,
  options: RequestInit = {},
): Promise<Response> {
  return fetch(url, {
    ...options,
    credentials: 'include',
  });
}
