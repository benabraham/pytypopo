import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    // Include upstream tests
    include: ['../typopo/tests/**/*.test.js'],

    // Exclude tests that require jsdom or are debug/not relevant for Python
    exclude: [
      '../typopo/tests/idempotency.test.js',
      '../typopo/tests/integration/typopo.test.js',
      '../typopo/tests/performance.test.js',
      '../typopo/tests/debug/**',
    ],

    // Increase timeout for HTTP calls
    testTimeout: 30000,

    // Resolve upstream imports
    alias: {
      // Redirect test-utils to our Python bridge version
      '../test-utils.js': resolve(import.meta.dirname, 'test-utils-python.js'),
      './test-utils.js': resolve(import.meta.dirname, 'test-utils-python.js'),

      // Keep locale imports pointing to upstream
      '../../src/locale/locale.js': resolve(import.meta.dirname, '../typopo/src/locale/locale.js'),
      '../src/locale/locale.js': resolve(import.meta.dirname, '../typopo/src/locale/locale.js'),

      // Keep const imports pointing to upstream
      '../../src/const.js': resolve(import.meta.dirname, '../typopo/src/const.js'),
      '../src/const.js': resolve(import.meta.dirname, '../typopo/src/const.js'),
    },
  },
})
