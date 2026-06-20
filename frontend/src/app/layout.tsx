import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "Scientia AI — Research Assistant",
  description: "Advanced AI Research Assistant for Scientific Papers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-white antialiased min-h-screen bg-grid-pattern bg-[size:32px_32px]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
