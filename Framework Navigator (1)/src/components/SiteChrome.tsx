import { Link } from "@tanstack/react-router";
import { Leaf } from "lucide-react";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center overflow-hidden rounded-lg bg-emerald-900/10 p-1 border border-emerald-500/20">
            <img src="/logo.png" alt="FrameworkFit Logo" className="size-full object-contain" />
          </span>
          <span className="font-display text-[1.05rem] font-semibold tracking-tight text-navy">
            FrameworkFit
          </span>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link
            to="/frameworks"
            className="hidden text-muted-foreground transition-colors hover:text-navy sm:block"
            activeProps={{ className: "text-navy font-medium" }}
          >
            Framework library
          </Link>
          <Link
            to="/assess"
            className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            Start assessment
          </Link>
        </nav>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-border/70 py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-5 text-sm text-muted-foreground">
        <div className="flex items-center gap-2.5">
          <span className="flex size-7 items-center justify-center overflow-hidden rounded-md bg-emerald-900/10 p-0.5 border border-emerald-500/20">
            <img src="/logo.png" alt="FrameworkFit Logo" className="size-full object-contain" />
          </span>
          <p className="font-medium text-navy">FrameworkFit</p>
        </div>
        <p className="max-w-xl">
          Guidance only. Framework applicability depends on jurisdiction, listing status and
          value-chain obligations — confirm scope with your assurance provider.
        </p>
      </div>
    </footer>
  );
}
