export const sdk = {
  orders: {
    list: (): Promise<{ id: string }[]> => Promise.resolve([{ id: "1" }]),
  },
};
