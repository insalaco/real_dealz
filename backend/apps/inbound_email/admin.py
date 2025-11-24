from django.contrib import admin
from django.utils.safestring import mark_safe
import bleach
import re
from .models import InboundEmail

@admin.register(InboundEmail)
class InboundEmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "recipient", "received_at", "is_processed")
    readonly_fields = ("preview", "body_plain", "metadata", "raw_mime")  # mark preview as readonly

    fieldsets = (
        (None, {
            "fields": (
                "message_id",
                "sender",
                "recipient",
                "subject",
                "received_at",
                "is_processed",
            )
        }),
        ("Preview", {
            "fields": ("preview",),  # this will render read-only HTML
        }),
        ("Raw Data", {
            "fields": ("body_plain", "body_html", "raw_mime", "metadata"),
        }),
    )

    def preview(self, obj):
        if obj.body_html:
            html = obj.body_html

            # remove tracking pixels
            html = re.sub(
                r'<img[^>]+(width=["\']?1["\']?|height=["\']?1["\']?|style=["\']?[^"\']*(display:\s*none|visibility:\s*hidden)[^"\']*)[^>]*>',
                '',
                html,
                flags=re.IGNORECASE
            )

            # sanitize HTML
            allowed_tags = ["a", "p", "div", "span", "br", "strong", "em",
                            "ul", "ol", "li", "table", "thead", "tbody", "tr",
                            "th", "td", "img"]
            allowed_attrs = {
                "a": ["href", "title"],
                "img": ["src", "alt", "width", "height", "style"],
                "*": ["style"]
            }

            cleaned_html = bleach.clean(
                html,
                tags=allowed_tags,
                attributes=allowed_attrs,
                protocols=["http", "https", "mailto"],
                strip=True
            )

            # force links to open in new tab
            cleaned_html = cleaned_html.replace(
                "<a ",
                "<a target=\"_blank\" rel=\"noopener noreferrer\" "
            )

            return mark_safe(cleaned_html)

        # fallback for plain text
        if obj.body_plain:
            return mark_safe(f"<pre>{bleach.linkify(obj.body_plain)}</pre>")

        return "(No content)"

    preview.short_description = "Email Preview"
