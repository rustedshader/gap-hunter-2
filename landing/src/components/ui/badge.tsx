import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-3 py-1 text-[0.72rem] font-semibold uppercase tracking-[0.2em]",
  {
    variants: {
      variant: {
        default:
          "border-[var(--color-border-strong)] bg-white/80 text-[var(--color-primary)]",
        subtle:
          "border-transparent bg-[var(--color-primary)]/8 text-[var(--color-primary)]",
        accent:
          "border-[var(--color-accent)]/20 bg-[var(--color-accent)]/12 text-[var(--color-accent)]"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
