import { PHASE_DEVELOPMENT_SERVER } from "next/constants.js";

/** @type {import('next').NextConfig} */
const nextConfig = (phase) => ({
  // Keep `next dev` and `next build` from sharing the same generated files.
  // A production build can otherwise invalidate chunks held by a live dev
  // server, producing intermittent "Cannot find module './<chunk>.js'" errors.
  // Browser-test servers can supply their own directory, so they never share
  // generated files with an interactive developer session either.
  distDir:
    phase === PHASE_DEVELOPMENT_SERVER
      ? process.env.NEXT_DEV_DIST_DIR || ".next-dev"
      : process.env.NEXT_BUILD_DIST_DIR || ".next",
  // Permit loopback aliases during local development without opening the dev
  // server to arbitrary origins.
  allowedDevOrigins: ["localhost", "127.0.0.1"],
});

export default nextConfig;
