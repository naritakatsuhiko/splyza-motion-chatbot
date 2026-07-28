import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SPLYZA Motion Medical Chatbot",
  description: "SPLYZA Motion Medical Support Chatbot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
