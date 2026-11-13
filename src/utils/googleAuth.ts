/**
 * Google Identity Services & Google Cloud Console OAuth 2.0 Integration
 */

export interface GoogleUserProfile {
  sub: string;
  name: string;
  email: string;
  picture?: string;
  email_verified?: boolean;
}

// Production Google Cloud Console Client ID provided by user
export const OFFICIAL_GOOGLE_CLIENT_ID = '1036683970798-2l4s35qal14te730n4ftarfsdj5ualc5.apps.googleusercontent.com';

/**
 * Get active Google Cloud Console Client ID
 */
export function getActiveGoogleClientId(): string {
  try {
    const saved = localStorage.getItem('floorguard_google_client_id');
    if (saved && saved.trim()) return saved.trim();
  } catch {}

  const envId = (import.meta as any).env?.VITE_GOOGLE_CLIENT_ID;
  if (envId && typeof envId === 'string' && envId.trim()) {
    return envId.trim();
  }

  return OFFICIAL_GOOGLE_CLIENT_ID;
}

/**
 * Save Google Cloud Console Client ID to localStorage
 */
export function saveGoogleClientId(clientId: string): void {
  try {
    if (clientId && clientId.trim()) {
      localStorage.setItem('floorguard_google_client_id', clientId.trim());
    } else {
      localStorage.removeItem('floorguard_google_client_id');
    }
  } catch {}
}

/**
 * Safely parse Google ID Token (JWT)
 */
export function decodeGoogleJwt(token: string): GoogleUserProfile | null {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (err) {
    console.error('Error decoding Google JWT credential:', err);
    return null;
  }
}

/**
 * Initialize Google Identity Services (GIS) One-Tap / Button
 */
export function renderOfficialGoogleButton(
  container: HTMLElement,
  clientId: string,
  onSuccess: (profile: GoogleUserProfile, rawCredential?: string) => void,
  onError?: (err: any) => void
): boolean {
  if (typeof window === 'undefined' || !(window as any).google?.accounts?.id) {
    return false;
  }

  try {
    (window as any).google.accounts.id.initialize({
      client_id: clientId,
      callback: (response: { credential: string }) => {
        if (response && response.credential) {
          const profile = decodeGoogleJwt(response.credential);
          if (profile && profile.email) {
            onSuccess(profile, response.credential);
          } else if (onError) {
            onError(new Error('Failed to decode user profile from Google ID Token.'));
          }
        }
      },
      auto_select: false,
      cancel_on_tap_outside: true,
    });

    container.innerHTML = '';

    (window as any).google.accounts.id.renderButton(container, {
      type: 'standard',
      theme: 'outline',
      size: 'large',
      text: 'continue_with',
      shape: 'pill',
      logo_alignment: 'left',
      width: '280',
    });

    return true;
  } catch (err) {
    console.error('Error rendering official Google Sign-In button:', err);
    if (onError) onError(err);
    return false;
  }
}

/**
 * Request Google OAuth 2.0 Access Token via Google Cloud Popup
 */
export async function launchGoogleOAuthPopup(
  clientId: string,
  onSuccess: (profile: GoogleUserProfile, accessToken: string) => void,
  onError: (error: any) => void
): Promise<void> {
  if (typeof window === 'undefined' || !(window as any).google?.accounts?.oauth2) {
    onError(new Error('Google OAuth 2.0 SDK not ready. Please check internet connection.'));
    return;
  }

  try {
    const tokenClient = (window as any).google.accounts.oauth2.initTokenClient({
      client_id: clientId,
      scope: 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
      callback: async (tokenResponse: { access_token?: string; error?: string }) => {
        if (tokenResponse.error) {
          onError(new Error(tokenResponse.error));
          return;
        }

        if (tokenResponse.access_token) {
          try {
            const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
              headers: {
                Authorization: `Bearer ${tokenResponse.access_token}`,
              },
            });
            const profile = await res.json();
            if (profile && profile.email) {
              onSuccess(profile, tokenResponse.access_token);
            } else {
              onError(new Error('Invalid response from Google UserInfo API.'));
            }
          } catch (fetchErr) {
            onError(fetchErr);
          }
        }
      },
    });

    tokenClient.requestAccessToken({ prompt: 'select_account' });
  } catch (err) {
    onError(err);
  }
}
