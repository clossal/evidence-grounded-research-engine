import "./globals.css";

export const metadata = {
  title: "Document Intelligence & Automation",
  description: "Local PDF extraction, evidence-grounded Q&A, and structured exports.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // LanguageTool adds data-lt-installed to <html> before React hydrates.
    // This is deliberately limited to the externally mutated root element so
    // real mismatches inside the application still surface in development.
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-white text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
