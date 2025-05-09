import type { Metadata } from "next";
import Script from "next/script"; // 👈 import Script
import { Geist, Geist_Mono, Pacifico, Permanent_Marker } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });
const permanentMarker = Permanent_Marker({
  weight: '400',
  variable: "--font-permanent-marker",
  display: 'swap',
  subsets: ["latin"],
});
const pacifico = Pacifico({
  weight: '400',
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-pacifico',
});

export const metadata: Metadata = {
  title: "YouTube Playlist Manager",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${pacifico.variable} ${permanentMarker.variable} antialiased`}
      >
        {/* 👇 Load the Google API script before your app uses gapi */}
        <Script
          src="https://apis.google.com/js/api.js"
          strategy="beforeInteractive"
        />
        {children}
      </body>
    </html>
  );
}
