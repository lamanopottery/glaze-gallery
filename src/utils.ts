import type { AstroGlobal, AstroCookieSetOptions } from "astro";
import { SignJWT, jwtVerify } from "jose";

const cookieOptions = {
  httpOnly: true,
  sameSite: "strict",
  secure: true,
} satisfies AstroCookieSetOptions;

const alg = "HS256";

export async function logIn(Astro: AstroGlobal, password: string) {
  const { GLAZE_GALLERY_PASSWORD, GLAZE_GALLERY_JWT_SECRET } = Astro.locals.runtime.env;

  if (password === GLAZE_GALLERY_PASSWORD) {
    const secret = new TextEncoder().encode(GLAZE_GALLERY_JWT_SECRET);
    const loginToken = await new SignJWT({ loggedIn: true })
      .setProtectedHeader({ alg })
      .setExpirationTime("1h")
      .sign(secret);
    Astro.cookies.set("login-token", loginToken, cookieOptions);
  }
}

export async function isLoggedIn(Astro: AstroGlobal) {
  const { GLAZE_GALLERY_JWT_SECRET } = Astro.locals.runtime.env;

  const loginToken = Astro.cookies.get("login-token")?.value;
  if (loginToken) {
    const secret = new TextEncoder().encode(GLAZE_GALLERY_JWT_SECRET);
    try {
      const { payload } = await jwtVerify(loginToken, secret);
      return payload.loggedIn === true;
    } catch {}
  }

  return false;
}
