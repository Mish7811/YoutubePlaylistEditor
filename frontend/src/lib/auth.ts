// lib/signin.ts
import { gapi } from 'gapi-script';

export const initGoogleAuth = () => {
  return new Promise<void>((resolve, reject) => {
    gapi.load('client:auth2', () => {
      gapi.client
        .init({
          clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
          scope: 'https://www.googleapis.com/auth/youtube.readonly',
        })
        .then(() => resolve())
        .catch((error) => reject(error));
    });
  });
};

export const signInWithGoogle = async () => {
  try {
    const auth2 = gapi.auth2.getAuthInstance();
    const user = await auth2.signIn();
    const accessToken = user.getAuthResponse().access_token;
    localStorage.setItem('access_token', accessToken); // ✅ Store access token
  } catch (error) {
    console.error("Google Sign-in failed", error);
  }
};
