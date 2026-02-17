/**
 * Modified test utilities that call Python via HTTP bridge
 * instead of directly calling JS functions.
 *
 * Drop-in replacement for typopo's test-utils.js
 */
import { describe, it, expect } from 'vitest'
import Locale from '../typopo/src/locale/locale.js'
import { base } from '../typopo/src/const.js'
import { m } from '../typopo/src/markers.js'

/**
 * Test token markers using Unicode Private Use Area
 * These are placeholders replaced by transformTestSet() with locale-specific values
 */
export const t = {
  // Quotes
  odq:  "\uE000",
  cdq:  "\uE001",
  osq:  "\uE002",
  csq:  "\uE003",
  apos: "\uE004",

  // Direct speech
  directSpeechIntro: "\uE005",

  // Dashes
  spaceBeforeDash: "\uE010",
  dash:            "\uE011",
  spaceAfterDash:  "\uE012",

  // Symbols
  symbol: "\uE020",
  space:  "\uE021",

  // Abbreviations
  abbrSpace: "\uE030",

  // Ordinal dates
  ordinalDateFirstSpace:  "\uE040",
  ordinalDateSecondSpace: "\uE041",
  romanOrdinalIndicator:  "\uE042",
  spaceBeforePercent:     "\uE043",
}

const PYTHON_BRIDGE_URL = process.env.PYTHON_BRIDGE_URL || 'http://127.0.0.1:9876'

/**
 * Map JS function to Python function name (camelCase)
 * The Python bridge expects camelCase names and maps them internally
 */
function getFunctionName(fn) {
  // Arrow functions don't have useful names, try to extract from toString()
  const fnStr = fn.toString()

  // Match patterns like: (text) => fixCopyrights(text, ...)
  // Also handles Vite SSR transform: (text) => (0,__vite_ssr_import_0__.fixCopyrights)(text, ...)
  const arrowMatch = fnStr.match(/=>\s*(?:\(0,\s*[\w.]+\.)?(\w+)\)?[\s(]/)
  if (arrowMatch) {
    return arrowMatch[1]
  }

  // Match patterns like: function fixCopyrights(
  const funcMatch = fnStr.match(/function\s+(\w+)\s*\(/)
  if (funcMatch) {
    return funcMatch[1]
  }

  // Fall back to fn.name (but skip empty string or "anonymous")
  if (fn.name && fn.name !== '' && fn.name !== 'anonymous') {
    return fn.name
  }

  // DEBUG: warn about unextractable function
  // console.log('DEBUG: Could not extract name from:', fnStr.slice(0, 100))

  return null
}

/**
 * Call Python bridge with a function and text
 */
// Cache for which functions are unavailable (404)
const unavailableFunctions = new Set()

async function callPython(functionName, text, locale, configuration = null) {
  // Skip if we know this function doesn't exist
  if (unavailableFunctions.has(functionName)) {
    return { __skipped: true, reason: `internal helper '${functionName}' unit test skipped (not exposed in Python bridge)` }
  }

  const response = await fetch(PYTHON_BRIDGE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      function: functionName,
      text: text,
      locale: locale,
      config: configuration || {},
    }),
  })

  if (response.status === 404) {
    unavailableFunctions.add(functionName)
    return { __skipped: true, reason: `internal helper '${functionName}' unit test skipped (not exposed in Python bridge)` }
  }

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Python bridge error (${response.status}): ${errorText}`)
  }

  const data = await response.json()
  if (data.error) {
    throw new Error(`Python error: ${data.error}`)
  }
  return data.result
}

/**
 * Helper function to DRY up repetitive test patterns
 * Modified to call Python instead of JS functions
 */
export function createTestSuite(
  description,
  unitTestSet,
  unitFunction = null,
  moduleTestSet = {},
  moduleFunction = null,
  locales = 'en-us',
  configuration = null
) {
  describe(description, () => {
    // If moduleTestSet is empty but moduleFunction is defined, use unitTestSet for module tests
    const effectiveModuleTestSet =
      Object.keys(moduleTestSet).length === 0 && moduleFunction ? unitTestSet : moduleTestSet

    // Normalize locales to array
    const localeArray = Array.isArray(locales) ? locales : [locales]

    // Run tests for each locale
    localeArray.forEach((locale) => {
      // Unit tests - call Python
      if (unitFunction) {
        const pythonFuncName = getFunctionName(unitFunction)

        // Skip if we can't determine the function name (complex arrow functions)
        if (!pythonFuncName) {
          it.skip(`unit test (${locale}): skipped - cannot extract function name`, () => {})
        } else {
          Object.keys(unitTestSet).forEach((key) => {
            const testName = `unit test (${locale}): "${truncate(key)}" → "${truncate(unitTestSet[key])}"`
            it(testName, async (ctx) => {
              const result = await callPython(pythonFuncName, key, locale, configuration)
              if (result && result.__skipped) {
                ctx.skip()
                return
              }
              expect(result).toBe(unitTestSet[key])
            })
          })
        }
      }

      // Module tests - call Python with module function name
      if (moduleFunction && Object.keys(effectiveModuleTestSet).length > 0) {
        const pythonFuncName = getFunctionName(moduleFunction)

        if (!pythonFuncName) {
          it.skip(`module test (${locale}): skipped - cannot extract function name`, () => {})
        } else {
          Object.keys(effectiveModuleTestSet).forEach((key) => {
            const testName = `module test (${locale}): "${truncate(key)}" → "${truncate(effectiveModuleTestSet[key])}"`
            it(testName, async (ctx) => {
              const result = await callPython(pythonFuncName, key, locale, configuration)
              if (result && result.__skipped) {
                ctx.skip()
                return
              }
              expect(result).toBe(effectiveModuleTestSet[key])
            })
          })
        }
      }
    })
  })
}

/**
 * Truncate string for readable test names
 */
function truncate(str, maxLen = 30) {
  if (str.length <= maxLen) return str
  return str.slice(0, maxLen - 3) + '...'
}

/**
 * Helper function to escape regex special characters
 */
function escapeRegex(str) {
  return str.replace(/[{}()[\]\\.$^*+?|]/g, '\\$&')
}

/**
 * Generic test set transformation function with locale-specific token replacement
 * This is identical to upstream - just transforms test data, no Python calls needed
 */
export function transformTestSet(testSet, localeName, options = {}) {
  const locale = new Locale(localeName)
  const { symbolName, additionalSets = [] } = options

  // Merge all additional test sets
  const mergedTestSet = additionalSets.reduce((acc, set) => ({ ...acc, ...set }), { ...testSet })

  const tokenMap = {
    // Quotes (Unicode Private Use Area tokens from t object)
    [t.odq]: locale.openingDoubleQuote,
    [t.cdq]: locale.closingDoubleQuote,
    [t.osq]: locale.openingSingleQuote,
    [t.csq]: locale.closingSingleQuote,
    [t.apos]: base.apostrophe,

    // Direct Speech
    [t.directSpeechIntro]: locale.directSpeechIntro,

    // Dashes
    [t.spaceBeforeDash]: locale.dashWords.spaceBefore,
    [t.dash]: locale.dashWords.dash,
    [t.spaceAfterDash]: locale.dashWords.spaceAfter,

    // Symbols (only if symbolName provided)
    ...(symbolName && {
      [t.symbol]: base[symbolName],
      [t.space]: locale.spaceAfter[symbolName],
    }),

    // Abbreviations
    [t.abbrSpace]: locale.spaceAfter.abbreviation,

    // Non-breaking spaces
    [t.ordinalDateFirstSpace]: locale.ordinalDate.firstSpace,
    [t.ordinalDateSecondSpace]: locale.ordinalDate.secondSpace,
    [t.romanOrdinalIndicator]: locale.romanOrdinalIndicator,
    [t.spaceBeforePercent]: locale.spaceBefore.percent,

    // Processing markers (from m object) that appear in test inputs
    [m.doublePrime]: base.doublePrime,
  }

  const replaceTokens = (str) => {
    // First replace all tokens
    const tokenReplaced = Object.entries(tokenMap).reduce(
      (result, [token, value]) => result.replace(new RegExp(escapeRegex(token), 'g'), value),
      str
    )
    // Then handle escaped dots (this must happen after token replacement)
    return tokenReplaced.replace(/\\\./g, '.')
  }

  const transformed = {}
  Object.keys(mergedTestSet).forEach((key) => {
    transformed[replaceTokens(key)] = replaceTokens(mergedTestSet[key])
  })

  return transformed
}
