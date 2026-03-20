/**
 * Shared fetch wrapper with credentials, X-Tenant-ID header, and silent token refresh.
 */

export function getTenantId(): string {
  return localStorage.getItem('tenantId') || '';
}

export function setTenantId(tenantId: string): void {
  localStorage.setItem('tenantId', tenantId);
}

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function tryRefreshToken(): Promise<boolean> {
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const tenantId = getTenantId();
      const headers: Record<string, string> = {};
      if (tenantId) headers['X-Tenant-ID'] = tenantId;

      const resp = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        credentials: 'include',
        headers,
      });
      return resp.ok;
    } catch {
      return false;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function apiFetch(
  url: string,
  options: RequestInit = {},
): Promise<Response> {
  const tenantId = getTenantId();
  const headers = new Headers(options.headers || {});

  if (tenantId) {
    headers.set('X-Tenant-ID', tenantId);
  }

  let response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });

  // If 401 and not already an auth endpoint, try silent refresh
  if (response.status === 401 && !url.includes('/api/v1/auth/')) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      // Retry the original request with fresh token
      response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
      });
    } else {
      // Refresh failed — redirect to login
      const tenant = getTenantId();
      localStorage.removeItem('tenantId');
      window.location.href = tenant ? `/login?tenant=${tenant}` : '/login';
    }
  }

  return response;
}
