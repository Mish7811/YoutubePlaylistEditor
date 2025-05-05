// lib/auth.ts
const CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!;

export const initGoogleSignIn = () => {
  if (typeof window !== 'undefined' && window.gapi) {
    window.gapi.load('auth2', () => {
      window.gapi.auth2.init({
        client_id: CLIENT_ID,
      }).then(() => {
        console.log("Google Auth initialized");
      }).catch((error: unknown) => {
        if (error instanceof Error) {
          console.error("Init error:", error.message);
        } else {
          console.error("Init unknown error:", error);
        }
      });
    });
  } else {
    console.error("gapi not available on window");
  }
};

export const signIn = async () => {
  const auth2 = window.gapi.auth2.getAuthInstance();
  if (!auth2) throw new Error("Google Sign-In is not initialized.");

  try {
    const user = await auth2.signIn();
    console.log("Signed in user:", user);
    return user;
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error("Sign-in error:", error.message);
    } else {
      console.error("Unknown sign-in error:", error);
    }
    throw error;
  }
};
