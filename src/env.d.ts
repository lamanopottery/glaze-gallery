/// <reference types="astro/client" />
/// <reference path="../.astro/types.d.ts" />
/// <reference types="@cloudflare/workers-types" />

namespace App {
  interface Locals {
    runtime: {
      env: Env;
    };
  }
}
