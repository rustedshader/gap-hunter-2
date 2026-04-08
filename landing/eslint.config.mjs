import nextCoreVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

export default [
  {
    ignores: ["eslint.config.mjs"]
  },
  ...nextCoreVitals,
  ...nextTypescript
];
