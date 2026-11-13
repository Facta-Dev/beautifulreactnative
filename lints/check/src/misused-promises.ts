// expect:@typescript-eslint/no-misused-promises
[1, 2].forEach(async (value) => {
  await Promise.resolve(value);
});
