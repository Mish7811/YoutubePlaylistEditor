"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Music4 } from "lucide-react";
import Playlist from "@/components/Playlists";
import AddSong from "@/components/AddSong";
import ClearButton from "@/components/ClearButton";
import { initGoogleSignIn, signIn } from '@/lib/auth';

export default function Home() {
  const [key, setKey] = useState(0); // Key for forcing playlist refresh

  useEffect(() => {
    // Ensure Google Sign-In is initialized only in the client side
    if (typeof window !== "undefined") {
      initGoogleSignIn();
    }
  }, []);

  const refreshPlaylist = () => {
    setKey((prev) => prev + 1);
  };

  const handleSignIn = async () => {
    try {
      await signIn();
      console.log("User signed in successfully");
    } catch (error) {
      console.error("Error during sign-in", error);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-bl from-[#123458] to-[#030303] text-white pt-10 pb-8">
      <Card className="w-full max-w-2xl bg-black/40 rounded-4xl m-5 backdrop-blur-md border-gray-800">
        <CardHeader className="space-y-1">
          <CardTitle
            className="text-3xl font-light text-center flex items-center justify-center gap-2"
            style={{ fontFamily: "var(--font-pacifico)" }}
          >
            <Music4 className="h-8 w-8" />
            YouTube Playlist Manager
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Google Sign-In Button */}
          <button
            onClick={handleSignIn}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg mt-4"
          >
            Sign in with Google
          </button>

          {/* Add Song Section */}
          <div className="flex flex-col gap-4">
            <AddSong onAdd={refreshPlaylist} />
            <ClearButton onClear={refreshPlaylist} />
          </div>

          {/* Playlist Section */}
          <div className="border-t border-gray-800 pt-4">
            <Playlist key={key} />
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
