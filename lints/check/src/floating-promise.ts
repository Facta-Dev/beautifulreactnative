async function save(): Promise<void> {
  await Promise.resolve();
}

// expect:@typescript-eslint/no-floating-promises
save();
