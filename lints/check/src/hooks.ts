function useState<T>(initial: T): [T, (next: T) => void] {
  let value = initial;
  return [value, (next) => { value = next; }];
}

function useEffect(effect: () => void, deps: readonly unknown[]): void {
  setTimeout(effect, deps.length);
}

export function Conditional({ ok }: { ok: boolean }): string {
  if (ok) {
    // expect:react-hooks/rules-of-hooks
    const [count] = useState(0);
    return String(count);
  }
  return "off";
}

export function Deps({ id }: { id: string }): string {
  const [length, setLength] = useState(0);
  useEffect(() => {
    setLength(id.length);
    // expect:react-hooks/exhaustive-deps
  }, []);
  return String(length);
}
