import { GLAZE_GALLERY_IMAGES_URL } from "astro:env/server";
import glazeNames from "@/data/glaze-names.json";
import glazeComboInfo from "@/data/glaze-combo-info.json";
import imagesLow from "@/data/images-low.json";
import imagesHigh from "@/data/images-high.json";

export function validGlaze(glaze: string | undefined): glaze is keyof typeof glazeNames {
  return !!glaze && glaze in glazeNames;
}

export function validGlazeCombo(
  glazeCombo: string | undefined,
): glazeCombo is keyof typeof glazeComboInfo {
  return !!glazeCombo && glazeCombo in glazeComboInfo;
}

export function validImageName(imageName: string): imageName is keyof typeof imagesLow {
  return imageName in imagesLow;
}

export function imageURL(
  glazeCombo: string | undefined,
  side: "front" | "back",
  resolution: "low" | "high",
) {
  const imageName = `${glazeCombo}-${side}`;
  if (!glazeCombo || !validImageName(imageName)) {
    return null;
  }
  const imagePrefix = (resolution === "low" ? imagesLow : imagesHigh)[imageName];
  return `${GLAZE_GALLERY_IMAGES_URL}/${imagePrefix}/${imageName}-${resolution}.webp`;
}
