import type { Metadata } from "next";
import type { CSSProperties, ReactNode } from "react";

import { appConfig, themeVariables } from "@/common/config/brand";

import "./globals.css";

export const metadata: Metadata = {
  title: appConfig.name,
  description: appConfig.description,
};

type RootLayoutProps = Readonly<{
  children: ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body style={themeVariables as CSSProperties}>
        {children}
      </body>
    </html>
  );
}
