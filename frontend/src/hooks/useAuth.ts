import { useMutation } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import type { UserPublic } from "@/client"

// Always return true as authentication is disabled
const isLoggedIn = () => {
  return true
}

const useAuth = () => {
  const navigate = useNavigate()

  // Mock user object
  const user: UserPublic = {
    email: "guest@example.com",
    is_active: true,
    is_superuser: false,
    full_name: "Guest User",
    id: "guest-id",
  }

  // No-op mutations since there's no real auth
  const signUpMutation = useMutation({
    mutationFn: async () => {},
    onSuccess: () => {
      navigate({ to: "/dashboard" })
    },
  })

  const loginMutation = useMutation({
    mutationFn: async () => {},
    onSuccess: () => {
      navigate({ to: "/dashboard" })
    },
  })

  const logout = () => {
    navigate({ to: "/" })
  }

  return {
    signUpMutation,
    loginMutation,
    logout,
    user,
  }
}

export { isLoggedIn }
export default useAuth
