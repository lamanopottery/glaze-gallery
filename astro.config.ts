import { defineConfig, envField } from "astro/config";
import cloudflare from "@astrojs/cloudflare";

import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  output: "server",
  adapter: cloudflare(),
  vite: { plugins: [tailwindcss()] },
  env: {
    schema: {
      GLAZE_GALLERY_STUDIO: envField.string({ context: "server", access: "public" }),
      GLAZE_GALLERY_STUDIO_EMAIL: envField.string({ context: "server", access: "public" }),
      GLAZE_GALLERY_IMAGES_URL: envField.string({ context: "server", access: "public" }),
      GLAZE_GALLERY_PASSWORD: envField.string({ context: "server", access: "secret" }),
      GLAZE_GALLERY_JWT_SECRET: envField.string({ context: "server", access: "secret" }),
    },
  },
});
