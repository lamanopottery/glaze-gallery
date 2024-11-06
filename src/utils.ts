import type { AstroGlobal, AstroCookieSetOptions } from "astro";
import jwt from "jsonwebtoken";

const cookieOptions = {
  httpOnly: true,
  sameSite: "strict",
  secure: true,
} satisfies AstroCookieSetOptions;

export function logIn(Astro: AstroGlobal, password: FormDataEntryValue | null) {
  if (typeof password !== "string") return;

  const { GLAZE_GALLERY_PASSWORD, GLAZE_GALLERY_JWT_SECRET } = Astro.locals.runtime.env;

  if (password === GLAZE_GALLERY_PASSWORD) {
    const loginToken = jwt.sign({ loggedIn: true }, GLAZE_GALLERY_JWT_SECRET, {
      expiresIn: "10s",
    });
    Astro.cookies.set("login-token", loginToken, cookieOptions);
  }
}

export function loginInfo(Astro: AstroGlobal) {
  const { GLAZE_GALLERY_JWT_SECRET } = Astro.locals.runtime.env;

  const loginToken = Astro.cookies.get("login-token")?.value;
  if (loginToken) {
    const loginInfo = jwt.verify(loginToken, GLAZE_GALLERY_JWT_SECRET);
    return loginInfo;
  }
  return "none";
}

export function isLoggedIn(Astro: AstroGlobal) {
  const { GLAZE_GALLERY_JWT_SECRET } = Astro.locals.runtime.env;

  const loginToken = Astro.cookies.get("login-token")?.value;
  if (loginToken) {
    try {
      const loginInfo = jwt.verify(loginToken, GLAZE_GALLERY_JWT_SECRET);
      return typeof loginInfo !== "string" && loginInfo.loggedIn == true;
    } catch {}
  }

  return false;
}
