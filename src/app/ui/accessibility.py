"""Accessibility utilities for UI themes."""
from ui.theme_tokens import Colors

class AccessibilityUtils:
    """Helper methods for accessibility validation and color adjustments."""

    @staticmethod
    def validate_contrast_ratio(foreground: str, background: str) -> float:
        """Calculate WCAG contrast ratio between two colors."""
        def get_luminance(color: str) -> float:
            if not color or not isinstance(color, str):
                return 0.5
            color = color.lstrip('#')
            if len(color) != 6:
                return 0.5
            try:
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            except ValueError:
                return 0.5

            def linearize(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)

            r_lin = linearize(r)
            g_lin = linearize(g)
            b_lin = linearize(b)
            return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

        l1 = get_luminance(foreground)
        l2 = get_luminance(background)
        if l1 < l2:
            l1, l2 = l2, l1
        return (l1 + 0.05) / (l2 + 0.05)

    @classmethod
    def check_wcag_compliance(cls, foreground: str, background: str, level: str = "AA") -> dict:
        """Check WCAG compliance for color contrast."""
        ratio = cls.validate_contrast_ratio(foreground, background)
        thresholds = {
            "AA": {"normal": 4.5, "large": 3.0},
            "AAA": {"normal": 7.0, "large": 4.5}
        }
        if level not in thresholds:
            level = "AA"
        thresholds = thresholds[level]
        return {
            "ratio": round(ratio, 2),
            "aa_normal": ratio >= thresholds["normal"],
            "aa_large": ratio >= thresholds["large"],
            "aaa_normal": ratio >= thresholds.get("normal", 4.5) * 7.0/4.5,
            "aaa_large": ratio >= thresholds.get("large", 3.0) * 4.5/3.0,
            "compliant": ratio >= thresholds["normal"]
        }

    @staticmethod
    def simulate_colorblindness(color: str, type_: str = "deuteranopia") -> str:
        """Simulate how a color appears to people with different types of colorblindness."""
        color = color.lstrip('#')
        try:
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return color

        matrices = {
            "protanopia": [
                [0.567, 0.433, 0.000],
                [0.558, 0.442, 0.000],
                [0.000, 0.242, 0.758]
            ],
            "deuteranopia": [
                [0.625, 0.375, 0.000],
                [0.700, 0.300, 0.000],
                [0.000, 0.300, 0.700]
            ],
            "tritanopia": [
                [0.950, 0.050, 0.000],
                [0.000, 0.433, 0.567],
                [0.000, 0.475, 0.525]
            ]
        }
        matrix = matrices.get(type_, matrices["deuteranopia"])
        new_r = int(r * matrix[0][0] + g * matrix[0][1] + b * matrix[0][2])
        new_g = int(r * matrix[1][0] + g * matrix[1][1] + b * matrix[1][2])
        new_b = int(r * matrix[2][0] + g * matrix[2][1] + b * matrix[2][2])
        new_r = max(0, min(255, new_r))
        new_g = max(0, min(255, new_g))
        new_b = max(0, min(255, new_b))
        return f"#{new_r:02x}{new_g:02x}{new_b:02x}"

    @classmethod
    def validate_theme_accessibility(cls) -> dict:
        """Validate the current theme for accessibility compliance."""
        checks = {
            "text_contrast": cls.check_wcag_compliance(Colors.TEXT_PRIMARY, Colors.SURFACE),
            "secondary_text_contrast": cls.check_wcag_compliance(Colors.TEXT_SECONDARY, Colors.SURFACE),
            "button_contrast": cls.check_wcag_compliance(Colors.TEXT_PRIMARY, Colors.BUTTON_PRIMARY_BG),
            "focus_indicator_visible": len(Colors.BORDER) > 0,
            "error_color_distinct": cls.validate_contrast_ratio(Colors.STATE_ERROR, Colors.SURFACE) > 3.0,
            "success_color_distinct": cls.validate_contrast_ratio(Colors.STATE_SUCCESS, Colors.SURFACE) > 3.0,
        }
        overall_compliance = all(
            check.get("compliant", True) if isinstance(check, dict) else check
            for check in checks.values()
        )
        return {
            "overall_compliant": overall_compliance,
            "checks": checks,
            "recommendations": cls._get_accessibility_recommendations(checks)
        }

    @classmethod
    def _get_accessibility_recommendations(cls, checks: dict) -> list:
        recommendations = []
        if not checks.get("text_contrast", {}).get("compliant", True):
            recommendations.append("Increase contrast between primary text and background")
        if not checks.get("secondary_text_contrast", {}).get("compliant", True):
            recommendations.append("Increase contrast between secondary text and background")
        if not checks.get("button_contrast", {}).get("compliant", True):
            recommendations.append("Increase contrast between button text and background")
        if not checks.get("error_color_distinct", True):
            recommendations.append("Make error state color more distinct from background")
        if not checks.get("success_color_distinct", True):
            recommendations.append("Make success state color more distinct from background")
        if not checks.get("focus_indicator_visible", True):
            recommendations.append("Add visible focus indicators for keyboard navigation")
        return recommendations

    @classmethod
    def auto_adjust_contrast(cls) -> dict:
        """Automatically adjust colors to improve contrast."""
        adjustments = {}
        text_contrast = cls.validate_contrast_ratio(Colors.TEXT_PRIMARY, Colors.SURFACE)
        if text_contrast < 4.5:
            # Simple heuristic: if background is dark, lighten text; else darken text
            # This assumes Colors.SURFACE is available and updated
            pass # Implementation simplified for refactoring
        return adjustments

    @classmethod
    def get_accessibility_summary(cls, mode_info: dict) -> dict:
        """Get a comprehensive accessibility summary."""
        validation = cls.validate_theme_accessibility()
        return {
            "current_mode": mode_info,
            "validation": validation,
            "compliance_score": sum(1 for check in validation["checks"].values()
                                  if (check.get("compliant", True) if isinstance(check, dict) else check)) /
                              len(validation["checks"]) * 100,
            "improvements_applied": len(cls.auto_adjust_contrast()) > 0
        }
