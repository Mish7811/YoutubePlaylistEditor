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
  const auth2 = gapi.auth2.getAuthInstance();
  if (auth2) {
    try {
      const user = await auth2.signIn();
      console.log("User signed in:", user);
      return user;
    } catch (error) {
      console.error("Error during Google Sign-In:", error);
      throw error;
    }
  } else {
    throw new Error("Google Sign-In is not initialized.");
  }
};
