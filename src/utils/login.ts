import type { AstroGlobal } from "astro";
import type { JWTPayload } from "jose";
import { SignJWT, jwtVerify } from "jose";
import { GLAZE_GALLERY_PASSWORD, GLAZE_GALLERY_JWT_SECRET } from "astro:env/server";

const LOGIN_TOKEN_EXPIRATION_SECONDS = 60 * 30; // 30 minutes
const REFRESH_TOKEN_EXPIRATION_SECONDS = 60 * 60 * 24 * 7; // 7 days

function getSecret() {
  return new TextEncoder().encode(GLAZE_GALLERY_JWT_SECRET);
}

async function saveToken(
  Astro: AstroGlobal,
  name: string,
  payload: JWTPayload,
  expirationSeconds: number,
) {
  const expirationDate = new Date();
  expirationDate.setTime(expirationDate.getTime() + expirationSeconds * 1000);

  const token = await new SignJWT(payload)
    .setProtectedHeader({ alg: "HS256" })
    .setExpirationTime(expirationDate)
    .sign(getSecret());

  Astro.cookies.set(name, token, {
    expires: expirationDate,
    httpOnly: true,
    sameSite: "lax",
    secure: true,
  });
}

async function refreshTokens(Astro: AstroGlobal) {
  await saveToken(Astro, "login-token", { loggedIn: true }, LOGIN_TOKEN_EXPIRATION_SECONDS);
  await saveToken(Astro, "refresh-token", { refresh: true }, REFRESH_TOKEN_EXPIRATION_SECONDS);
}

async function getPayload(Astro: AstroGlobal, name: string) {
  const loginToken = Astro.cookies.get(name)?.value;
  console.log(loginToken);
  if (loginToken) {
    try {
      const { payload } = await jwtVerify(loginToken, getSecret());
      return payload;
    } catch {}
  }

  return null;
}

export async function logIn(Astro: AstroGlobal, password: string) {
  if (password === GLAZE_GALLERY_PASSWORD) {
    await refreshTokens(Astro);
  }
}

export async function isLoggedIn(Astro: AstroGlobal) {
  const loginPayload = await getPayload(Astro, "login-token");
  if (loginPayload !== null && loginPayload.loggedIn === true) {
    return true;
  }

  const refreshPayload = await getPayload(Astro, "refresh-token");
  if (refreshPayload !== null && refreshPayload.refresh === true) {
    await refreshTokens(Astro);
    const loginPayload = await getPayload(Astro, "login-token");
    return loginPayload !== null && loginPayload.loggedIn === true;
  }
}

export function redirectToLogin(Astro: AstroGlobal) {
  const { pathname, search } = Astro.url;
  const dest = encodeURIComponent(pathname.slice(1) + search);
  const queryParams = dest ? `?dest=${dest}` : "";
  return Astro.redirect(`/login${queryParams}`);
}
