import type { ImageMetadata } from "astro";
import { GLAZE_GALLERY_STUDIO } from "astro:env/server";
import LMLogo from "@/assets/LM-logo.svg";
import MMLogo from "@/assets/MM-logo.svg";
import kraftPaperTile from "@/assets/kraft-paper-tile.jpg";
import kraftPaperBlueTile from "@/assets/kraft-paper-blue-tile.jpg";

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
  /** Short slug stamped onto `<html data-studio>` to drive per-studio CSS. */
  key: string;
  /** Studio logo shown in the header. */
  logo: ImageMetadata;
  /** Favicons for the document head. */
  favicons: Favicon[];
  /** Solid page background color shown behind (and around) the texture tile. */
  backgroundColor: string;
  /** Repeating kraft-paper texture painted over the background color. */
  backgroundTile: ImageMetadata;
};

/** Branding assets keyed by the value of the GLAZE_GALLERY_STUDIO env var. */
const STUDIOS: Record<string, Studio | undefined> = {
  "La Mano Pottery": {
    key: "la-mano",
    logo: LMLogo,
    favicons: [
      { type: "image/svg+xml", href: "/LM-icon.svg" },
      { type: "image/x-icon", href: "/LM-icon.ico" },
    ],
    backgroundColor: "#a5855e",
    backgroundTile: kraftPaperTile,
  },
  "Mud Matters": {
    key: "mud-matters",
    logo: MMLogo,
    favicons: [
      { type: "image/svg+xml", href: "/MM-icon.svg" },
      { type: "image/x-icon", href: "/MM-icon.ico" },
    ],
    backgroundColor: "#778378",
    backgroundTile: kraftPaperBlueTile,
  },
};

const selected = STUDIOS[GLAZE_GALLERY_STUDIO];
if (selected === undefined) {
  throw new Error(`Unknown GLAZE_GALLERY_STUDIO: ${JSON.stringify(GLAZE_GALLERY_STUDIO)}`);
}

/** Branding assets for the studio configured via the GLAZE_GALLERY_STUDIO env var. */
export const studio = selected;
