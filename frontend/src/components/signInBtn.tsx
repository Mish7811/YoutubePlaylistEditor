import { useEffect } from 'react';
import { initGoogleSignIn, signIn } from '@/lib/auth';

const SignInButton = () => {
  // Initialize Google Sign-In when the component mounts
  useEffect(() => {
    initGoogleSignIn();
  }, []);

  const handleSignIn = async () => {
    try {
      await signIn();
      console.log('User signed in successfully');
    } catch (error) {
      console.error('Error during sign-in', error);
    }
  };

  return (
    <button
      onClick={handleSignIn}
      className="px-4 py-2 bg-blue-500 text-white rounded-lg"
    >
      Sign in with Google
    </button>
  );
};

export default SignInButton;
