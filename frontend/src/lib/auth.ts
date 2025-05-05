// lib/signin.ts or components/ui/SignInButton.tsx
import { gapi } from 'gapi-script';

const CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!;

export const initGoogleSignIn = () => {
  if (typeof window !== "undefined") { // Ensure it's running on the client
    gapi.load('auth2', () => {
      gapi.auth2.init({
        client_id: CLIENT_ID,
      });
    });
  }
};

export const signIn = async () => {
  if (typeof window !== "undefined") { // Ensure it's running on the client
    const auth2 = gapi.auth2.getAuthInstance();
    const googleUser = await auth2.signIn();
    const id_token = googleUser.getAuthResponse().id_token;
    localStorage.setItem('id_token', id_token);
  }
};
