import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SPLYZA Chatbot",
  description: "SPLYZA Support Chatbot",
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
