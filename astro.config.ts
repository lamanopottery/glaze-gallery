import { defineConfig } from "astro/config";
import cloudflare from "@astrojs/cloudflare";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  output: "server",
  trailingSlash: "never",
  adapter: cloudflare(),
  integrations: [tailwind()],
});
