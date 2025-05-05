// components/ui/SignInButton.tsx
"use client";

import { useEffect } from "react";
import { initGoogleSignIn, signIn } from "@/lib/auth";

export const SignInButton = () => {
  useEffect(() => {
    initGoogleSignIn();
  }, []);

  const handleSignIn = async () => {
    try {
      const user = await signIn();
      console.log("User:", user.getBasicProfile().getName());
    } catch (error) {
      console.error("Sign-in failed", error);
    }
  };

  return (
    <button onClick={handleSignIn} className="px-4 py-2 bg-blue-500 text-white rounded">
      Sign in with Google
    </button>
  );
};
