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
  /** Studio name shown in page metadata and site chrome. */
  name: string;
  /** Public contact email shown on the login page. */
  email: string;
  /** Public studio website linked from the header logo. */
  url: string;
  /** Canonical URL for this studio's glaze gallery deployment. */
  galleryUrl: string;
  /** Static host containing this studio's published images and JSON manifests. */
  imagesUrl: string;
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
const STUDIOS = {
  lamanopottery: {
    name: "La Mano Pottery",
    email: "info@lamanopottery.com",
    url: "https://www.lamanopottery.com",
    galleryUrl: "https://glazegallery.lamanopottery.com",
    imagesUrl: "https://glazegalleryimages.lamanopottery.com",
    logo: LMLogo,
    favicons: [
      { type: "image/svg+xml", href: "/LM-icon.svg" },
      { type: "image/x-icon", href: "/LM-icon.ico" },
    ],
    backgroundColor: "#a5855e",
    backgroundTile: kraftPaperTile,
  },
  mudmatters: {
    name: "Mud Matters",
    email: "info@mudmatters.com",
    url: "https://www.mudmatters.com",
    galleryUrl: "https://glazegallery.mudmatters.com",
    imagesUrl: "https://glazegalleryimages.mudmatters.com",
    logo: MMLogo,
    favicons: [
      { type: "image/svg+xml", href: "/MM-icon.svg" },
      { type: "image/x-icon", href: "/MM-icon.ico" },
    ],
    backgroundColor: "#778378",
    backgroundTile: kraftPaperBlueTile,
  },
} satisfies Record<string, Studio>;

type StudioKey = keyof typeof STUDIOS;

function isStudioKey(value: string): value is StudioKey {
  return Object.hasOwn(STUDIOS, value);
}

if (!isStudioKey(GLAZE_GALLERY_STUDIO)) {
  throw new Error(`Unknown GLAZE_GALLERY_STUDIO: ${JSON.stringify(GLAZE_GALLERY_STUDIO)}`);
}

const selected: Studio = STUDIOS[GLAZE_GALLERY_STUDIO];

/** Branding assets for the studio configured via the GLAZE_GALLERY_STUDIO env var. */
export const studio = {
  key: GLAZE_GALLERY_STUDIO,
  ...selected,
};
