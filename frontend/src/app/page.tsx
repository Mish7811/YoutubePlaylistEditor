"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Music4 } from "lucide-react";
import Playlist from "@/components/Playlists";
import AddSong from "@/components/AddSong";
import ClearButton from "@/components/ClearButton";
import { fetchPlaylist, clearPlaylist } from "@/lib/api";

export default function Home() {
  const [key, setKey] = useState(0); // Key for forcing playlist refresh
  const [gapiLoaded, setGapiLoaded] = useState(false);
  const [playlist, setPlaylist] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      import('@/lib/auth').then((auth) => {
        auth.initGoogleSignIn();
        setGapiLoaded(true);
      }).catch((error) => {
        console.error("Failed to load gapi", error);
      });
    }
  }, []);

  const refreshPlaylist = async () => {
    setLoading(true);
    try {
      const data = await fetchPlaylist();
      setPlaylist(data);
    } catch (error) {
      console.error("Error fetching playlist", error);
    } finally {
      setLoading(false);
    }
    setKey((prev) => prev + 1);
  };

  const handleSignIn = async () => {
    if (gapiLoaded) {
      try {
        const { signIn } = await import('@/lib/auth');
        const user = await signIn();
        if (user) {
          console.log("User signed in successfully");
        } else {
          console.log("User closed the sign-in popup.");
          // Optional: Provide feedback to the user
          alert("Sign-in popup was closed. Please try again.");
        }
      } catch (error: unknown) {
        if (
          typeof error === "object" &&
          error !== null &&
          "error" in error &&
          (error as { error: string }).error === "popup_closed_by_user"
        ) {
          console.log("The sign-in popup was closed by the user.");
          alert("Sign-in process was interrupted. Please try again.");
        } else {
          console.error("Error during sign-in", error);
        }
      }
    }
  };
  

  const handleClearPlaylist = async () => {
    try {
      await clearPlaylist();
      refreshPlaylist();
    } catch (error) {
      console.error("Error clearing playlist", error);
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
          <button
            onClick={handleSignIn}
            className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg mt-4"
          >
            Sign in with Google
          </button>

          <div className="flex flex-col gap-4">
            <AddSong onAdd={refreshPlaylist} />
            <ClearButton onClear={handleClearPlaylist} />
          </div>

          <div className="border-t border-gray-800 pt-4">
            {loading ? (
              <div className="text-center text-white">Loading Playlist...</div>
            ) : (
              <Playlist key={key} playlist={playlist} />
            )}
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
