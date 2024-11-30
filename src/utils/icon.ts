import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { icon } from "@fortawesome/fontawesome-svg-core";

export function iconData(iconDefinition: IconDefinition) {
  const [abstract] = icon(iconDefinition).abstract;

  return {
    viewBox: abstract.attributes.viewBox as string,
    svgPath: abstract.children![0].attributes.d as string,
  };
}
