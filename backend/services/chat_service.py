from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.config import get_settings
from backend.models.career import Career
from backend.models.prediction import EnsemblePrediction
from backend.models.skill import CareerSkill
from backend.models.chat_session import ChatMessage
from typing import AsyncGenerator
import asyncio


FABRICE_SYSTEM_PROMPT = """You are FabriceAI, a world-class career advisor specializing in how artificial intelligence impacts careers and professions. You have deep expertise in labor economics, AI/ML trends, and career planning.

Your personality:
- Warm, encouraging, and professional
- Data-driven — you back up advice with numbers and scores
- Honest about risks but always constructive
- You help people find AI-resilient career paths

Your knowledge base includes:
- AI automation risk scores (0-100) for 500+ careers
- Predicted disruption timelines (when AI could significantly impact each career)
- Salary data and projections factoring in AI impact
- Skills analysis showing which tasks in each career are automatable

Guidelines:
- When a user asks about a specific career, use the data provided in the context
- Always mention the automation risk score and disruption timeline
- Suggest AI-resilient alternatives for high-risk careers
- Recommend upskilling strategies (learning AI tools, developing human-edge skills)
- Keep responses focused on career and AI topics
- Use emojis sparingly for warmth
- Format responses with clear structure (bullet points, headers when appropriate)

If the user asks something unrelated to careers/AI, politely redirect them."""


class FabriceAIService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self._has_api_key = bool(self.settings.anthropic_api_key and
                                  self.settings.anthropic_api_key != "sk-ant-your-key-here" and
                                  len(self.settings.anthropic_api_key) > 10)
        if self._has_api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
            except Exception:
                self._has_api_key = False
                self.client = None
        else:
            self.client = None

    def _find_careers(self, message: str) -> list[Career]:
        words = [w.lower() for w in message.split() if len(w) > 3]
        careers = self.db.query(Career).join(EnsemblePrediction).all()

        matched = []
        for career in careers:
            title_lower = career.title.lower()
            if any(word in title_lower for word in words):
                matched.append(career)
        return matched[:5]

    def _format_career_data(self, career: Career) -> str:
        ep = career.ensemble_prediction
        if not ep:
            return f"**{career.title}**: No prediction data available."

        risk_emoji = {
            "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"
        }.get(ep.risk_level, "⚪")

        lines = [
            f"**{career.title}** {risk_emoji}",
            f"",
            f"- **AI Automation Risk:** {ep.automation_risk_score:.0f}/100 ({ep.risk_level})",
            f"- **Predicted AI Disruption:** ~{ep.disruption_year}",
            f"- **Job Stability Score:** {ep.job_stability_score:.0f}/100",
            f"- **Median Salary:** ${career.median_salary:,.0f}",
            f"- **5-Year Salary Projection:** ${ep.salary_5yr_projection:,.0f}",
            f"- **10-Year Salary Projection:** ${ep.salary_10yr_projection:,.0f}",
            f"- **Education Required:** {career.education_level}",
            f"- **Employment Growth:** {career.growth_rate_pct:+.1f}%",
            f"- **People Employed:** {career.employment_count:,}",
        ]
        return "\n".join(lines)

    def _find_career_context(self, message: str) -> str:
        matched = self._find_careers(message)
        if matched:
            parts = [self._format_career_data(c) for c in matched]
            return "\n\nRelevant career data from our database:\n" + "\n\n".join(parts)
        return ""

    def _get_chat_history(self, session_id: str) -> list[dict]:
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(20)
            .all()
        )
        return [{"role": m.role, "content": m.content} for m in messages]

    def _generate_fallback_response(self, message: str) -> str:
        msg_lower = message.lower()
        matched = self._find_careers(message)

        # If they asked about specific careers, show the data
        if matched:
            parts = ["Hi! I'm FabriceAI, your career advisor. Here's what I found:\n"]
            for career in matched:
                parts.append(self._format_career_data(career))
                ep = career.ensemble_prediction
                if ep:
                    if ep.risk_level in ("critical", "high"):
                        parts.append(
                            f"\n⚠️ **Advisory:** {career.title} has a {ep.risk_level} AI automation risk. "
                            f"Consider developing skills in areas that AI struggles with — creativity, "
                            f"emotional intelligence, complex problem-solving, and leadership. "
                            f"Learning to work alongside AI tools can also make you more valuable."
                        )
                    elif ep.risk_level == "low":
                        parts.append(
                            f"\n✅ **Good news!** {career.title} has a low AI automation risk. "
                            f"This career relies heavily on human skills that are difficult for AI to replicate. "
                            f"It's a strong choice for long-term career stability."
                        )
                    else:
                        parts.append(
                            f"\n💡 **Tip:** {career.title} has moderate AI risk. Stay competitive by "
                            f"embracing AI tools in your workflow and developing your uniquely human skills."
                        )
            parts.append("\n---\n*Explore the Dashboard for more careers, or try the Career DNA quiz to find your best match!*")
            return "\n\n".join(parts)

        # Generic queries
        if any(kw in msg_lower for kw in ["safest", "safe career", "safe job", "low risk", "best career"]):
            safest = (
                self.db.query(Career)
                .join(EnsemblePrediction)
                .filter(EnsemblePrediction.risk_level == "low")
                .order_by(Career.median_salary.desc())
                .limit(5)
                .all()
            )
            if safest:
                response = "Great question! Here are the **safest careers from AI automation** (with the best salaries):\n\n"
                for i, c in enumerate(safest, 1):
                    ep = c.ensemble_prediction
                    response += (
                        f"**{i}. {c.title}** 🟢\n"
                        f"   - Risk: {ep.automation_risk_score:.0f}% | Salary: ${c.median_salary:,.0f} | "
                        f"Disruption: ~{ep.disruption_year}\n\n"
                    )
                response += (
                    "These careers rely heavily on human creativity, empathy, physical presence, "
                    "or complex decision-making — areas where AI has significant limitations.\n\n"
                    "*Tip: Use the Career DNA feature to find the safest career that matches YOUR skills!*"
                )
                return response

        if any(kw in msg_lower for kw in ["risky", "danger", "at risk", "replaced", "most risk"]):
            riskiest = (
                self.db.query(Career)
                .join(EnsemblePrediction)
                .filter(EnsemblePrediction.risk_level == "critical")
                .order_by(EnsemblePrediction.automation_risk_score.desc())
                .limit(5)
                .all()
            )
            if riskiest:
                response = "Here are the **careers most at risk** of AI automation:\n\n"
                for i, c in enumerate(riskiest, 1):
                    ep = c.ensemble_prediction
                    response += (
                        f"**{i}. {c.title}** 🔴\n"
                        f"   - Risk: {ep.automation_risk_score:.0f}% | Salary: ${c.median_salary:,.0f} | "
                        f"Disruption: ~{ep.disruption_year}\n\n"
                    )
                response += (
                    "These careers involve highly routine, data-heavy, or repetitive tasks that AI "
                    "can increasingly handle. If you're in one of these fields, consider:\n\n"
                    "1. **Upskilling** — Learn AI/ML tools to augment your work\n"
                    "2. **Pivoting** — Transition to a related but more AI-resilient role\n"
                    "3. **Specializing** — Focus on the parts of your job that require human judgment"
                )
                return response

        if any(kw in msg_lower for kw in ["study", "college", "major", "degree", "school", "university"]):
            response = (
                "Great question about education! Here's my advice:\n\n"
                "**AI-Resilient Fields to Study:**\n\n"
                "1. **Healthcare** (Nursing, Medicine, Therapy) — Low automation risk, high demand\n"
                "2. **Computer Science / AI** — If you can't beat AI, build it! High salaries, strong growth\n"
                "3. **Engineering** (Mechanical, Civil, Biomedical) — Complex physical-world problems\n"
                "4. **Psychology / Counseling** — Human connection can't be automated\n"
                "5. **Education** — Teaching requires empathy and adaptability\n\n"
                "**Fields to Approach with Caution:**\n"
                "- Pure data entry / administrative roles\n"
                "- Basic accounting / bookkeeping\n"
                "- Routine manufacturing\n\n"
                "💡 **Pro tip:** Whatever you study, learn to work WITH AI tools. "
                "The future belongs to people who can leverage AI, not compete against it.\n\n"
                "*Try the Career DNA quiz to get personalized recommendations based on your skills and interests!*"
            )
            return response

        if any(kw in msg_lower for kw in ["compare", "vs", "versus", "or", "better"]):
            return (
                "I can help you compare careers! Here are some ways to do it:\n\n"
                "1. **Ask me about specific careers** — e.g., 'Tell me about nursing' or 'software developer'\n"
                "2. **Use the Compare feature** — Visit the Dashboard, find careers you're interested in, "
                "and compare them side-by-side\n"
                "3. **Try Career DNA** — Take the quiz to find careers that match your unique skills\n\n"
                "What careers would you like to know about?"
            )

        if any(kw in msg_lower for kw in ["hello", "hi", "hey", "help", "what can you"]):
            total = self.db.query(func.count(Career.id)).scalar()
            return (
                f"Hi there! I'm **FabriceAI**, your personal career advisor! 👋\n\n"
                f"I have data on **{total} careers** with AI automation risk scores, salary projections, "
                f"and disruption timelines. Here's what I can help with:\n\n"
                f"- 🔍 **Career analysis** — Ask about any career (e.g., 'Tell me about nursing')\n"
                f"- 🛡️ **Safest careers** — 'What careers are safest from AI?'\n"
                f"- ⚠️ **At-risk careers** — 'Which jobs are most at risk?'\n"
                f"- 🎓 **Education advice** — 'What should I study in college?'\n"
                f"- 📊 **Comparisons** — 'Compare nursing vs teaching'\n\n"
                f"What would you like to know?"
            )

        # Default response
        total = self.db.query(func.count(Career.id)).scalar()
        return (
            f"Thanks for your question! I'm FabriceAI, and I specialize in how AI impacts careers.\n\n"
            f"I have data on **{total} careers** in my database. Try asking me:\n\n"
            f"- About a specific career (e.g., 'software developer', 'nurse', 'accountant')\n"
            f"- 'What careers are safest from AI?'\n"
            f"- 'Which jobs are most at risk?'\n"
            f"- 'What should I study in college?'\n\n"
            f"I'll give you data-backed insights with risk scores, salary projections, and practical advice!"
        )

    async def stream_response(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        # If we have an API key, use Claude
        if self._has_api_key and self.client:
            history = self._get_chat_history(session_id)
            career_context = self._find_career_context(user_message)

            messages = history.copy()
            enriched_message = user_message
            if career_context:
                enriched_message += career_context

            messages.append({"role": "user", "content": enriched_message})

            try:
                with self.client.messages.stream(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    system=FABRICE_SYSTEM_PROMPT,
                    messages=messages,
                ) as stream:
                    for text in stream.text_stream:
                        yield text
                return
            except Exception:
                pass  # Fall through to fallback

        # Fallback: use database-driven responses
        response = self._generate_fallback_response(user_message)

        # Stream it word by word for a natural feel
        words = response.split(' ')
        for i, word in enumerate(words):
            if i > 0:
                yield ' '
            yield word
            if word.endswith('\n') or word.endswith('.') or word.endswith('!') or word.endswith('?'):
                await asyncio.sleep(0.02)
            elif i % 5 == 0:
                await asyncio.sleep(0.01)
