// expect:no-new-func, @typescript-eslint/no-implied-eval
export const fn = new Function("return 1") as unknown;
