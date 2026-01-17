/**
 * Kumon worksheet utilities.
 */

/**
 * Kumon Maths level descriptions.
 * Levels progress through mathematical concepts.
 */
const LEVEL_NAMES: Record<string, string> = {
  '7A': 'Counting',
  '6A': 'Numbers to 30',
  '5A': 'Line Drawing',
  '4A': 'Numbers to 50',
  '3A': 'Adding to 5',
  '2A': 'Adding to 10',
  'A': 'Adding',
  'B': 'Subtracting',
  'C': 'Multiplication',
  'D': 'Division',
  'E': 'Fractions',
  'F': 'Fractions',
  'G': 'Pos/Neg Numbers',
  'H': 'Algebra',
  'I': 'Factorisation',
  'J': 'Functions',
  'K': 'Quadratics',
  'L': 'Logarithms',
  'M': 'Trigonometry',
  'N': 'Differentiation',
  'O': 'Integration',
};

/**
 * Format a sheet ID (e.g. "C26a") into a meaningful display name.
 * Returns: "C26a · Multiplication"
 */
export function formatSheetName(sheetId: string | null): string {
  if (!sheetId) return 'Unknown';

  // Extract level letter (e.g. "C" from "C26a")
  const match = sheetId.match(/^(\d*[A-Z])/);
  if (!match) return sheetId;

  const level = match[1];
  const topic = LEVEL_NAMES[level];

  if (topic) {
    return `${sheetId} · ${topic}`;
  }

  return sheetId;
}

/**
 * Get just the topic name for a level.
 */
export function getLevelTopic(sheetId: string | null): string | null {
  if (!sheetId) return null;

  const match = sheetId.match(/^(\d*[A-Z])/);
  if (!match) return null;

  return LEVEL_NAMES[match[1]] || null;
}

/**
 * Extract the starting sheet from a sheet range.
 * "C26a-C28b" → "C26a"
 * "C26a" → "C26a"
 */
export function getStartingSheet(sheetId: string | null): string | null {
  if (!sheetId) return null;
  // If it's a range (contains '-'), extract the first part
  const dashIndex = sheetId.indexOf('-');
  if (dashIndex > 0) {
    return sheetId.substring(0, dashIndex);
  }
  return sheetId;
}

/**
 * Format a sheet ID showing only the starting sheet for consistency.
 * "C26a-C28b" → "C26 · Multiplication"
 */
export function formatSheetNameConsistent(sheetId: string | null): string {
  const startSheet = getStartingSheet(sheetId);
  return formatSheetName(startSheet);
}
