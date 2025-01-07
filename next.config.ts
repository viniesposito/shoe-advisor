import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.externals = [...(config.externals || []), {
      'shelljs': 'commonjs shelljs',
    }]
    return config
  },
}

export default nextConfig