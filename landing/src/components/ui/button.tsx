import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-full text-sm font-semibold transition-[transform,box-shadow,background-color,color,border-color] duration-300 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg)] disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-[var(--color-accent)] px-6 py-3 text-[var(--color-cream)] shadow-[0_18px_40px_rgba(200,101,60,0.28)] hover:-translate-y-0.5 hover:bg-[color:color-mix(in_srgb,var(--color-accent),black_8%)]",
        secondary:
          "border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-6 py-3 text-[var(--color-text)] backdrop-blur hover:-translate-y-0.5 hover:border-[var(--color-primary)]/45 hover:bg-white/80",
        ghost:
          "px-4 py-2 text-[var(--color-text)] hover:bg-[var(--color-primary)]/8 hover:text-[var(--color-primary)]",
        quiet:
          "bg-transparent px-0 py-0 text-[var(--color-primary)] underline-offset-4 hover:text-[var(--color-accent)] hover:underline"
      },
      size: {
        default: "h-12",
        lg: "h-14 px-8 text-base",
        xl: "h-16 px-10 text-base"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
