import { Button } from "./ui/button";
import {motion} from "framer-motion";

export default function Footer() {
    return (
      <footer className="relative border-t bg-muted/50 flex flex-col items-center justify-center">
         <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-1/4 -left-1/4 w-1/2 h-1/2 bg-primary-light rounded-full"
          animate={{
            scale: [1, 1.1, 1],
            rotate: [0, 45, 0],
          }}
          transition={{
            duration: 15,
            repeat: Number.POSITIVE_INFINITY,
            ease: "linear",
          }}
        />
        <motion.div
          className="absolute -bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-secondary-light rounded-full"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, -45, 0],
          }}
          transition={{
            duration: 20,
            repeat: Number.POSITIVE_INFINITY,
            ease: "linear",
          }}
        />
      </div>
        <section className="border-t">
        <div className="container pt-24">
          <div className="mx-auto max-w-3xl space-y-8 text-center">
            <h2 className="text-3xl font-bold">Ready to Get Started?</h2>
            <p className="text-muted-foreground">
            Join thousands of content creators who are already using Moment AI to grow their audience.
            </p>
            <div className="space-x-4">
              <Button size="lg">Start Free Trial</Button>
              <Button size="lg" variant="outline">
                Contact Sales
              </Button>
            </div>
          </div>
        </div>
      </section>
      <div className="container py-16">
        <div className="mt-16 border-t pt-8 text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Moment AI Hub. All rights reserved.
        </div>
      </div>
    </footer>
    );
}