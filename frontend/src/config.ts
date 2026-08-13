const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

if (!apiBaseUrl) {
  throw new Error(
    'Missing required env var VITE_API_BASE_URL. Copy .env.example to ' +
      '.env and set it.',
  )
}

export const config = {
  apiBaseUrl,
} as const
