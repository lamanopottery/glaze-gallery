import type { ImageMetadata } from "astro";
import { GLAZE_GALLERY_STUDIO } from "astro:env/server";
import LMLogo from "@/assets/LM-logo.svg";
import MMLogo from "@/assets/MM-logo.svg";

/** A favicon `<link rel="icon">` definition. */
type Favicon = {
  /** Path or URL to the icon file. */
  href: string;
  /** MIME type, e.g. `"image/svg+xml"`. */
  type?: string;
  /** Icon dimensions, e.g. `"32x32"`. */
  sizes?: string;
};

/** Branding assets for a single studio. */
type Studio = {
  /** Studio logo shown in the header. */
  logo: ImageMetadata;
  /** Favicons for the document head. */
  favicons: Favicon[];
};

/** Branding assets keyed by the value of the GLAZE_GALLERY_STUDIO env var. */
const STUDIOS: Record<string, Studio | undefined> = {
  "La Mano Pottery": {
    logo: LMLogo,
    favicons: [
      { type: "image/svg+xml", href: "/LM-icon.svg" },
      { type: "image/x-icon", href: "/LM-icon.ico" },
    ],
  },
  "Mud Matters": {
    logo: MMLogo,
    favicons: [
      { sizes: "32x32", href: "/MM-icon-32.png" },
      { sizes: "192x192", href: "/MM-icon-192.png" },
    ],
  },
};

const selected = STUDIOS[GLAZE_GALLERY_STUDIO];
if (selected === undefined) {
  throw new Error(`Unknown GLAZE_GALLERY_STUDIO: ${JSON.stringify(GLAZE_GALLERY_STUDIO)}`);
}

/** Branding assets for the studio configured via the GLAZE_GALLERY_STUDIO env var. */
export const studio = selected;
