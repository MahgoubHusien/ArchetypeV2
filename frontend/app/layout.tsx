import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Archetype - AI UX Testing Platform",
  description: "AI-powered UX testing platform that simulates diverse user personas to evaluate and improve your website's user experience",
  keywords: "UX testing, AI testing, user experience, persona simulation, usability testing",
  authors: [{ name: "Archetype Team" }],
  openGraph: {
    title: "Archetype - AI UX Testing Platform",
    description: "Transform your UX with AI-powered persona testing",
    type: "website",
  },
};

import { Toaster } from "sonner";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <Toaster 
          position="top-right"
          toastOptions={{
            style: {
              background: 'white',
              border: '1px solid #e5e7eb',
            },
          }}
        />
      </body>
    </html>
  );
}
