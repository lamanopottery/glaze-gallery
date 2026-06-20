import glazeNames from "@/data/glaze-names.json";
import glazeComboInfo from "@/data/glaze-combo-info.json";
import imagesLow from "@/data/images-low.json";
import imagesHigh from "@/data/images-high.json";
import { studio } from "@/utils/studio";

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
  return `${studio.imagesUrl}/${imagePrefix}/${imageName}-${resolution}.webp`;
}
