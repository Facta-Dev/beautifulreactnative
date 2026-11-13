import type { Lead } from "./types";

// expect:@typescript-eslint/consistent-type-imports
import { Lead as LeadAgain } from "./types";

export const first: Lead = { id: "1", name: "First" };
export const second: LeadAgain = first;
