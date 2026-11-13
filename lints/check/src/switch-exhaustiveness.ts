type Kind = "a" | "b";

export function label(kind: Kind): string {
  // expect:@typescript-eslint/switch-exhaustiveness-check
  switch (kind) {
    case "a":
      return "A";
  }
  return "unknown";
}
