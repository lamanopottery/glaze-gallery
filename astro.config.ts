import { defineConfig } from "astro/config";
import cloudflare from "@astrojs/cloudflare";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  output: "server",
  adapter: cloudflare(),
  integrations: [tailwind()],
  vite: {
    define: {
      "import.meta.env.GLAZE_GALLERY_STUDIO": JSON.stringify(
        import.meta.env.GLAZE_GALLERY_STUDIO,
      ),
      "import.meta.env.GLAZE_GALLERY_STUDIO_EMAIL": JSON.stringify(
        import.meta.env.GLAZE_GALLERY_STUDIO_EMAIL,
      ),
    },
  },
});
