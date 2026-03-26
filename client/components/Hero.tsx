import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { createClient } from "@/utils/supabase/client"
import { LoginForm } from "@/components/login-form"
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog"
import { VisuallyHidden } from "@radix-ui/react-visually-hidden"

export default function Hero() {
  const router = useRouter()
  const supabase = createClient()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [showLoginDialog, setShowLoginDialog] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setIsLoggedIn(!!user)
      setIsLoading(false)
    }
    checkAuth()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setIsLoggedIn(!!session?.user)
      if (session?.user) setShowLoginDialog(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const handleGetStarted = () => {
    if (isLoggedIn) {
      router.push("/dashboard")
    } else {
      setShowLoginDialog(true)
    }
  }

  const handleLearnMore = () => {
    if (isLoggedIn) {
      router.push("/dashboard")
    } else {
      setShowLoginDialog(true)
    }
  }

  return (
    <>
    <div className="min-h-[80vh] bg-background py-20 md:py-32 overflow-hidden relative">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight">
            <motion.span
              className="text-primary block mb-2"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
            >
              Transform Your Podcasts into
            </motion.span>
            <motion.span
              className="text-foreground"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
            >
              Viral Clips
            </motion.span>
          </h1>
          <motion.p
            className="mt-6 text-xl text-muted-foreground max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            Automatically create engaging short-form content from your podcasts using AI. Save time, reach more
            people, and grow your audience.
          </motion.p>
          <motion.div
            className="mt-10 flex flex-col sm:flex-row gap-4 justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            {isLoading ? (
              <Button size="lg" className="w-full sm:w-auto" disabled>
                Loading...
              </Button>
            ) : isLoggedIn ? (
              <Button size="lg" className="w-full sm:w-auto" onClick={() => router.push("/dashboard")}>
                Go to Dashboard
              </Button>
            ) : (
              <>
                <Button size="lg" className="w-full sm:w-auto" onClick={handleGetStarted}>
                  Get started
                </Button>
                <Button variant="outline" size="lg" className="w-full sm:w-auto" onClick={handleLearnMore}>
                  Learn more
                </Button>
              </>
            )}
          </motion.div>
        </motion.div>
      </div>

      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-1/2 -left-1/2 w-full h-full bg-primary/10 dark:bg-primary/20 rounded-full"
          animate={{
            scale: [1, 1.1, 1],
            rotate: [0, 28, 0],
          }}
          transition={{
            duration: 20,
            repeat: Number.POSITIVE_INFINITY,
            ease: "linear",
          }}
        />
        <motion.div
          className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-secondary/10 dark:bg-secondary/20 rounded-full"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, -30, 0],
          }}
          transition={{
            duration: 25,
            repeat: Number.POSITIVE_INFINITY,
            ease: "linear",
          }}
        />
        <motion.div
          className="absolute top-1/4 left-1/4 w-12 h-12 bg-primary/20 dark:bg-primary/30 rounded-full"
          animate={{
            y: [0, -20, 0],
            x: [0, 20, 0],
          }}
          transition={{
            duration: 5,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-20 h-20 bg-secondary dark:bg-secondary/30 rounded-full"
          animate={{
            y: [0, -30, 0],
            x: [0, 30, 0],
          }}
          transition={{
            duration: 7,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
      </div>
    </div>

    <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
      <DialogContent className="sm:max-w-md p-0 border-none bg-transparent shadow-none">
        <VisuallyHidden>
          <DialogTitle>Login</DialogTitle>
        </VisuallyHidden>
        <LoginForm />
      </DialogContent>
    </Dialog>
    </>
  )
}

