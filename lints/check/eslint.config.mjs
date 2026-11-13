// Beautiful React Native drop-in lints
//
// Paste this into your repo root (read the overrides below first, then add
// your project-specific ignores on the first entry). It makes eslint enforce
// the rules from the reactnative-best-practices skill that a linter can check:
// the View/ViewModel/SDK walls, hooks discipline, the no-remote-code rule and
// the silencing requirements. Silence a rule locally with a reason, which the
// config requires.
//
// Everything beyond the pinned rules rides the typescript-eslint
// strictTypeChecked + stylisticTypeChecked presets. Make CI strict with:
//
//     npx eslint .
//
// The lints/check project proves every pinned rule fires: see
// scripts/check-lints.sh and tests/contracts/test_lints_contract.py.

import js from "@eslint/js";
import tseslint from "typescript-eslint";
import eslintComments from "@eslint-community/eslint-plugin-eslint-comments";
import reactHooks from "eslint-plugin-react-hooks";

const VIEW_MESSAGE =
  "The View never imports the SDK: call a ViewModel command and render its state — see the 'Architecture contract' in reactnative-best-practices.";

const VIEWMODEL_MESSAGE =
  "The ViewModel is platform-free: react-native, react-dom and views enter through ports — see the 'Architecture contract' in reactnative-best-practices.";

const SDK_MESSAGE =
  "The SDK is a plain TypeScript client: it never imports React, React Native or the session — see the 'Architecture contract' in reactnative-best-practices.";

export default tseslint.config(
  { ignores: ["dist/", "node_modules/", "coverage/", "src/gen/", ".expo/"] },
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
  {
    plugins: {
      "@eslint-community/eslint-comments": eslintComments,
      "react-hooks": reactHooks,
    },
    rules: {
      // One logger, not console.* sprinkled through screens.
      "no-console": "error",
      // No remote code, no eval, no Function constructor.
      "no-eval": "error",
      "no-new-func": "error",
      "@typescript-eslint/no-implied-eval": "error",
      // Silencing must be narrow, explained, and rare: @ts-expect-error with a
      // reason on the narrowest line; ts-ignore and ts-nocheck are flat out.
      "@typescript-eslint/ban-ts-comment": [
        "error",
        {
          "ts-expect-error": "allow-with-description",
          "ts-ignore": true,
          "ts-nocheck": true,
          minimumDescriptionLength: 10,
        },
      ],
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/no-misused-promises": [
        "error",
        { checksConditionals: true, checksVoidReturn: true },
      ],
      "@typescript-eslint/switch-exhaustiveness-check": "error",
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports" },
      ],
      "@typescript-eslint/explicit-module-boundary-types": "error",
      "@typescript-eslint/no-unnecessary-type-assertion": "error",
      // Muting attempts are themselves findings.
      "@eslint-community/eslint-comments/no-unlimited-disable": "error",
      "@eslint-community/eslint-comments/require-description": ["error", { ignore: [] }],
      // Hooks rules are correctness rules, not style.
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "error",
    },
  },
  {
    // The View never talks to the SDK.
    files: ["src/**/views/**/*.{ts,tsx}", "src/screens/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        { patterns: [{ group: ["@/sdk", "@/sdk/*", "**/sdk/*"], message: VIEW_MESSAGE }] },
      ],
    },
  },
  {
    // The ViewModel stays platform-free.
    files: ["src/**/viewmodels/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["react-native", "react-native/*", "react-dom", "react-dom/*", "@/views", "@/views/*", "**/views/*"],
              message: VIEWMODEL_MESSAGE,
            },
          ],
        },
      ],
    },
  },
  {
    // The SDK stays React-free and platform-free.
    files: ["src/sdk/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          paths: [
            { name: "react", message: SDK_MESSAGE },
            { name: "react-native", message: SDK_MESSAGE },
          ],
          patterns: [{ group: ["@/session", "@/session/*"], message: SDK_MESSAGE }],
        },
      ],
    },
  },
);
