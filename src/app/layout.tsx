import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/theme/theme-provider";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "OmniScope AI - Multi-Omics Data Analysis Platform",
  description: "Advanced multi-omics data analysis platform powered by AI. Analyze genomics, proteomics, and metabolomics data with cutting-edge machine learning.",
  keywords: ["OmniScope", "Multi-omics", "Genomics", "Proteomics", "Metabolomics", "AI", "Machine Learning", "Data Analysis"],
  authors: [{ name: "OmniScope AI Team" }],
  icons: {
    icon: "/favicon.ico",
  },
  openGraph: {
    title: "OmniScope AI - Multi-Omics Analysis",
    description: "Advanced multi-omics data analysis platform powered by AI",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "OmniScope AI - Multi-Omics Analysis",
    description: "Advanced multi-omics data analysis platform powered by AI",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} font-sans antialiased bg-background text-foreground`}
      >
        <ThemeProvider>
          {children}
          <Toaster 
            position="top-right"
            toastOptions={{
              style: {
                background: 'hsl(var(--background))',
                color: 'hsl(var(--foreground))',
                border: '1px solid hsl(var(--border))',
              },
            }}
          />
        </ThemeProvider>
      </body>
    </html>
  );
}
