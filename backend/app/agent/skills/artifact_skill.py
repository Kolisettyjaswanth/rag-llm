import re
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.services.rag_service import RAGService
    from app.llm.provider import LLMProvider


class ArtifactSkill:
    name = "artifact"

    def __init__(
        self,
        rag_service: "RAGService | None" = None,
        llm: "LLMProvider | None" = None,
    ) -> None:
        if rag_service is None:
            from app.services.rag_service import RAGService

            rag_service = RAGService()

        if llm is None:
            from app.llm.factory import get_llm_provider

            llm = get_llm_provider()

        self.rag_service = rag_service
        self.llm = llm

    def execute(
        self,
        db: Session,
        request: str,
    ) -> dict:
        retrieval = self.rag_service.retrieve(
            db=db,
            question=request,
            top_k=5,
        )

        context = retrieval["context"]

        system_prompt = """You are the Artifact Generation skill for Lenny Growth Assistant.

Generate a complete self-contained HTML document containing HTML and CSS.

Requirements:
- Use semantic HTML.
- Put CSS inside a <style> element.
- Do not use JavaScript.
- Do not use external resources.
- Do not use external images, fonts, scripts, iframes, forms, or network requests.
- Keep the artifact self-contained.
- Ground factual product/growth content in the supplied transcript context.
- Do not invent transcript claims.
- Make the result visually polished and responsive.
"""

        prompt = f"""User artifact request:
{request}

Relevant Lenny's Podcast transcript context:
{context}

Return ONLY the complete HTML document.
"""

        html = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        html = self._sanitize(self.normalize_html_artifact(html))

        return {
            "answer": "Artifact generated successfully.",
            "sources": retrieval["sources"],
            "artifact": {
                "type": "html",
                "content": html,
            },
        }

    @staticmethod
    def normalize_html_artifact(content: str) -> str:
        content = content.strip()
        fenced_match = re.fullmatch(
            r"```(?:html)?\s*(.*?)\s*```",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if fenced_match:
            return fenced_match.group(1).strip()

        return content

    @staticmethod
    def _sanitize(html: str) -> str:
        html = re.sub(
            r"<(?:script|iframe|object|embed|link|form)\b[^>]*>.*?</(?:script|iframe|object|embed|link|form)>",
            "",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        html = re.sub(
            r"<(?:script|iframe|object|embed|link|form)\b[^>]*/?>",
            "",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        html = re.sub(
            r"\s+on[a-z0-9_-]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
            "",
            html,
            flags=re.IGNORECASE,
        )

        html = re.sub(
            r"\s+(?:href|src|action|formaction|poster|cite)\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
            "",
            html,
            flags=re.IGNORECASE,
        )

        html = re.sub(r"@import[^;]+;", "", html, flags=re.IGNORECASE)
        html = re.sub(r"url\s*\([^)]*\)", "", html, flags=re.IGNORECASE)

        return html.strip()
