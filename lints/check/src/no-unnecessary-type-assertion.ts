let value = 1;
value = 2;

// expect:@typescript-eslint/no-unnecessary-type-assertion
export const one = value as number;
