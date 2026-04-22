export const brandPalette = {
  button: "#E5F223",
  text: "#3D3D3D",
  textLight: "#A3A29F",
  textMid: "#3B424B",
  background: "#DBDBDB",
} as const;

export const brandTypography = {
  primaryFont: "Roboto",
  fontStack: ["Roboto", "Helvetica Neue", "Arial", "sans-serif"].join(", "),
  fontSize: {
    caption: "0.85rem",
    body: "1rem",
    bodyLarge: "1.05rem",
    title: "clamp(2.5rem, 5vw, 4.5rem)",
  },
  lineHeight: {
    tight: "0.95",
    normal: "1.5",
    relaxed: "1.7",
  },
} as const;

export const brandSpacing = {
  pagePaddingY: "48px",
  pagePaddingX: "20px",
  pagePaddingYMobile: "24px",
  pagePaddingXMobile: "16px",
  sectionGap: "32px",
  contentGap: "20px",
  gridGap: "14px",
  labelGap: "8px",
  cardPadding: "40px",
  cardPaddingMobile: "24px",
  tokenPaddingY: "16px",
  tokenPaddingX: "18px",
  buttonPaddingY: "14px",
  buttonPaddingX: "22px",
} as const;

export const brandRadius = {
  card: "28px",
  cardMobile: "22px",
  token: "18px",
  pill: "999px",
} as const;

export const appConfig = {
  name: "SpendPilot",
  description: "Personal finance dashboard with clean, focused UX.",
} as const;

export const themeVariables = {
  "--color-button": brandPalette.button,
  "--color-text": brandPalette.text,
  "--color-text-light": brandPalette.textLight,
  "--color-text-mid": brandPalette.textMid,
  "--color-background": brandPalette.background,
  "--font-primary": brandTypography.fontStack,
  "--font-size-caption": brandTypography.fontSize.caption,
  "--font-size-body": brandTypography.fontSize.body,
  "--font-size-body-large": brandTypography.fontSize.bodyLarge,
  "--font-size-title": brandTypography.fontSize.title,
  "--line-height-tight": brandTypography.lineHeight.tight,
  "--line-height-normal": brandTypography.lineHeight.normal,
  "--line-height-relaxed": brandTypography.lineHeight.relaxed,
  "--spacing-page-y": brandSpacing.pagePaddingY,
  "--spacing-page-x": brandSpacing.pagePaddingX,
  "--spacing-page-y-mobile": brandSpacing.pagePaddingYMobile,
  "--spacing-page-x-mobile": brandSpacing.pagePaddingXMobile,
  "--spacing-section": brandSpacing.sectionGap,
  "--spacing-content": brandSpacing.contentGap,
  "--spacing-grid": brandSpacing.gridGap,
  "--spacing-label": brandSpacing.labelGap,
  "--spacing-card": brandSpacing.cardPadding,
  "--spacing-card-mobile": brandSpacing.cardPaddingMobile,
  "--spacing-token-y": brandSpacing.tokenPaddingY,
  "--spacing-token-x": brandSpacing.tokenPaddingX,
  "--spacing-button-y": brandSpacing.buttonPaddingY,
  "--spacing-button-x": brandSpacing.buttonPaddingX,
  "--radius-card": brandRadius.card,
  "--radius-card-mobile": brandRadius.cardMobile,
  "--radius-token": brandRadius.token,
  "--radius-pill": brandRadius.pill,
} as const;
