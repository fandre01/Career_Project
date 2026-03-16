from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.config import get_settings
from backend.models.career import Career
from backend.models.prediction import EnsemblePrediction
from backend.models.skill import CareerSkill
from backend.models.chat_session import ChatMessage
from typing import AsyncGenerator
import asyncio


FABRICE_SYSTEM_PROMPT = """You are FabriceAI, an intelligent career advisor built by Fabrice Andre, a Data Science student at Brigham Young University-Idaho (BYU-Idaho). You specialize in how artificial intelligence impacts careers and professions, powered by real labor market data and machine learning predictions.

Your personality:
- Warm, encouraging, and professional
- Data-driven — you back up advice with numbers and scores from the CareerShield AI database
- Honest about risks but always constructive and empowering
- You help people find AI-resilient career paths and make informed decisions
- You speak with confidence and authority on career topics

Your knowledge base includes:
- AI automation risk scores (0-100) for hundreds of careers
- Predicted disruption timelines (when AI could significantly impact each career)
- Salary data and 5-year/10-year projections factoring in AI impact
- Skills analysis showing which tasks in each career are automatable
- Job stability scores, employment counts, and growth rates
- Education requirements for each career

Guidelines:
- When a user asks about a specific career, use the data provided in the context
- Always mention the automation risk score and disruption timeline when discussing a career
- Suggest AI-resilient alternatives for high-risk careers
- Recommend upskilling strategies (learning AI tools, developing human-edge skills)
- You can answer questions about career planning, job market trends, education choices, salary expectations, interview tips, resume advice, skill development, and career transitions
- For topics outside your expertise, give a helpful general answer and gently redirect to career topics
- Use emojis sparingly for warmth
- Format responses with clear structure (bullet points, headers when appropriate)
- Keep responses concise but thorough — aim for 150-300 words
- End responses with a follow-up question or suggestion to keep the conversation going
- When greeting users, mention that you were built by Fabrice Andre, a Data Science student at BYU-Idaho"""


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
            desc_lower = (career.description or "").lower()
            if any(word in title_lower or word in desc_lower for word in words):
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
            parts = ["Great question! Here's what our data shows:\n"]
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
            parts.append("\n---\n*Want to explore more? Try the Dashboard for all careers, or take the Career DNA quiz to find your best match!*")
            return "\n\n".join(parts)

        # Safest careers
        if any(kw in msg_lower for kw in ["safest", "safe career", "safe job", "low risk", "best career", "secure", "future proof", "stable"]):
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
                    "Would you like to know more about any of these careers? Or try the **Career DNA** feature to find the safest career that matches YOUR skills!"
                )
                return response

        # Riskiest careers
        if any(kw in msg_lower for kw in ["risky", "danger", "at risk", "replaced", "most risk", "eliminate", "automat", "disappear", "obsolete", "threatened"]):
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
                    "3. **Specializing** — Focus on the parts of your job that require human judgment\n\n"
                    "Would you like specific advice for transitioning out of a high-risk career?"
                )
                return response

        # Education & study advice
        if any(kw in msg_lower for kw in ["study", "college", "major", "degree", "school", "university", "education", "learn", "course", "certification", "training", "bootcamp"]):
            return (
                "Great question about education! Here's my data-driven advice:\n\n"
                "**AI-Resilient Fields to Study:**\n\n"
                "1. **Healthcare** (Nursing, Medicine, Therapy) — Low automation risk, high demand\n"
                "2. **Computer Science / AI / Data Science** — If you can't beat AI, build it! High salaries, strong growth\n"
                "3. **Engineering** (Mechanical, Civil, Biomedical) — Complex physical-world problems\n"
                "4. **Psychology / Counseling** — Human connection can't be automated\n"
                "5. **Education** — Teaching requires empathy and adaptability\n\n"
                "**Fields to Approach with Caution:**\n"
                "- Pure data entry / administrative roles\n"
                "- Basic accounting / bookkeeping\n"
                "- Routine manufacturing\n\n"
                "💡 **Pro tip:** Whatever you study, learn to work WITH AI tools. "
                "The future belongs to people who can leverage AI, not compete against it.\n\n"
                "Would you like me to analyze a specific career you're considering? Or try the **Career DNA** quiz to get personalized recommendations!"
            )

        # Salary questions
        if any(kw in msg_lower for kw in ["salary", "pay", "earn", "income", "money", "compensation", "wage", "highest paid", "best paying"]):
            top_salary = (
                self.db.query(Career)
                .join(EnsemblePrediction)
                .order_by(Career.median_salary.desc())
                .limit(5)
                .all()
            )
            if top_salary:
                response = "Here are the **highest-paying careers** in our database:\n\n"
                for i, c in enumerate(top_salary, 1):
                    ep = c.ensemble_prediction
                    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(ep.risk_level, "⚪")
                    response += (
                        f"**{i}. {c.title}** {risk_emoji}\n"
                        f"   - Salary: ${c.median_salary:,.0f} | AI Risk: {ep.automation_risk_score:.0f}% ({ep.risk_level})\n\n"
                    )
                response += (
                    "💡 **Key insight:** High salary doesn't always mean safe from AI. "
                    "Check the risk scores above — some high-paying jobs are also high-risk.\n\n"
                    "Want me to find careers that are both high-paying AND low-risk?"
                )
                return response

        # Compare careers
        if any(kw in msg_lower for kw in ["compare", "vs", "versus", "better", "difference", "choose between"]):
            return (
                "I can help you compare careers! Here are your options:\n\n"
                "1. **Ask me directly** — e.g., 'Tell me about nursing' or 'What about software engineering?'\n"
                "2. **Use the Compare page** — Select up to 4 careers and see them side-by-side with radar charts\n"
                "3. **Try Career DNA** — Take the quiz to find careers that match your unique skills\n\n"
                "What careers are you deciding between? I'll pull up the data for you!"
            )

        # Skills & upskilling
        if any(kw in msg_lower for kw in ["skill", "upskill", "improve", "prepare", "future", "ready", "adapt", "transition", "switch career", "change career", "pivot"]):
            return (
                "Great thinking! Here are the **top skills to develop** for an AI-powered future:\n\n"
                "**Technical Skills (High Value):**\n"
                "- 🤖 AI/ML literacy — Understanding how AI tools work\n"
                "- 📊 Data analysis & visualization\n"
                "- 💻 Programming (Python, JavaScript)\n"
                "- ☁️ Cloud computing & DevOps\n\n"
                "**Human-Edge Skills (AI Can't Replace):**\n"
                "- 🎨 Creative thinking & innovation\n"
                "- 🤝 Emotional intelligence & empathy\n"
                "- 🗣️ Complex communication & negotiation\n"
                "- 🧠 Critical thinking & strategic planning\n"
                "- 👥 Leadership & team management\n\n"
                "💡 **The winning formula:** Combine domain expertise + AI tool proficiency. "
                "A nurse who can use AI diagnostics, or a marketer who leverages AI analytics, "
                "becomes irreplaceable.\n\n"
                "What's your current career? I can give you specific upskilling recommendations!"
            )

        # Interview & resume
        if any(kw in msg_lower for kw in ["interview", "resume", "cv", "cover letter", "apply", "job search", "hired", "hiring"]):
            return (
                "Here are my top tips for standing out in today's AI-influenced job market:\n\n"
                "**Resume Tips:**\n"
                "- Highlight your experience with AI/tech tools\n"
                "- Quantify your achievements with data\n"
                "- Show adaptability and continuous learning\n"
                "- Tailor your resume for each application\n\n"
                "**Interview Tips:**\n"
                "- Demonstrate how you've used technology to improve your work\n"
                "- Show awareness of AI trends in your industry\n"
                "- Emphasize your uniquely human skills (creativity, empathy, leadership)\n"
                "- Ask thoughtful questions about the company's AI strategy\n\n"
                "💡 **Pro tip:** Companies increasingly value candidates who can work alongside AI, "
                "not just those with traditional skills.\n\n"
                "What career are you applying for? I can give you industry-specific advice!"
            )

        # About FabriceAI / who built this
        if any(kw in msg_lower for kw in ["who built", "who made", "who created", "about you", "your creator", "fabrice", "byu"]):
            total = self.db.query(func.count(Career.id)).scalar()
            return (
                f"I'm **FabriceAI**, an intelligent career advisor powered by machine learning and real labor market data! 🤖\n\n"
                f"I was built by **Fabrice Andre**, a Data Science student at **Brigham Young University-Idaho (BYU-Idaho)**. "
                f"Fabrice created CareerShield AI as a platform to help people worldwide understand how artificial intelligence "
                f"will impact their careers and make smarter, data-driven career decisions.\n\n"
                f"**What powers me:**\n"
                f"- Machine learning models trained on O*NET and Bureau of Labor Statistics data\n"
                f"- AI automation risk analysis for **{total} careers**\n"
                f"- Salary projections, job stability scores, and skills analysis\n\n"
                f"What would you like to know about your career's future?"
            )

        # Greeting
        if any(kw in msg_lower for kw in ["hello", "hi", "hey", "help", "what can you", "good morning", "good afternoon", "good evening", "sup", "yo", "greetings"]):
            total = self.db.query(func.count(Career.id)).scalar()
            return (
                f"Hello! I'm **FabriceAI**, your personal AI career advisor! 👋\n\n"
                f"I was built by **Fabrice Andre**, a Data Science student at **BYU-Idaho**, "
                f"to help you navigate the future of work with confidence.\n\n"
                f"Ask me anything about how AI will impact your career, what to study, or which jobs are safest. "
                f"I have data-driven insights on **{total} careers** including:\n\n"
                f"- 🔍 **Career analysis** — 'Tell me about software engineering'\n"
                f"- 🛡️ **Safest careers** — 'What careers are safest from AI?'\n"
                f"- ⚠️ **At-risk careers** — 'Which jobs will AI replace?'\n"
                f"- 💰 **Salary insights** — 'What are the highest-paying safe careers?'\n"
                f"- 🎓 **Education advice** — 'What should I study in college?'\n"
                f"- 🚀 **Upskilling tips** — 'How do I prepare for an AI future?'\n"
                f"- 📊 **Career comparisons** — 'Compare nursing vs teaching'\n\n"
                f"What would you like to explore?"
            )

        # Thank you
        if any(kw in msg_lower for kw in ["thank", "thanks", "appreciate", "helpful", "awesome", "great"]):
            return (
                "You're welcome! I'm glad I could help! 😊\n\n"
                "Remember, the key to thriving in an AI-powered world is to stay adaptable, "
                "keep learning, and focus on developing skills that complement AI rather than compete with it.\n\n"
                "Feel free to ask me anything else about careers, education, or AI trends. "
                "And don't forget to explore the **Dashboard** and **Career DNA** features for even more insights!\n\n"
                "Good luck on your career journey! 🚀"
            )

        # Default — catch-all for any other question
        total = self.db.query(func.count(Career.id)).scalar()
        return (
            f"That's a great question! I'm **FabriceAI**, your personal career advisor, "
            f"built by Fabrice Andre, a Data Science student at BYU-Idaho.\n\n"
            f"I specialize in how AI impacts careers, and I have data on **{total} careers** "
            f"in my database. Here are some things I can help you with:\n\n"
            f"- 🔍 **Ask about any career** — e.g., 'software developer', 'nurse', 'accountant'\n"
            f"- 🛡️ **Safest careers** — 'What careers are safest from AI?'\n"
            f"- ⚠️ **At-risk careers** — 'Which jobs will AI replace?'\n"
            f"- 💰 **Salary insights** — 'What are the highest-paying careers?'\n"
            f"- 🎓 **Education advice** — 'What should I study?'\n"
            f"- 🚀 **Upskilling** — 'How do I prepare for an AI future?'\n"
            f"- 📝 **Job search** — 'Resume and interview tips'\n\n"
            f"Try asking one of these, or tell me about your current career and I'll give you personalized insights!"
        )

    async def stream_response(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        # If we have an API key, try Claude first
        if self._has_api_key and self.client:
            try:
                history = self._get_chat_history(session_id)
                career_context = self._find_career_context(user_message)

                messages = history.copy()
                enriched_message = user_message
                if career_context:
                    enriched_message += career_context

                messages.append({"role": "user", "content": enriched_message})

                # Collect Claude's response chunks
                chunks: list[str] = []
                with self.client.messages.stream(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    system=FABRICE_SYSTEM_PROMPT,
                    messages=messages,
                ) as stream:
                    for text in stream.text_stream:
                        chunks.append(text)

                # If we got chunks, yield them all
                if chunks:
                    for chunk in chunks:
                        yield chunk
                    return
            except Exception:
                pass  # Fall through to fallback

        # Fallback: use database-driven responses
        try:
            response = self._generate_fallback_response(user_message)
        except Exception:
            response = (
                "Hello! I'm **FabriceAI**, your personal AI career advisor! 👋\n\n"
                "I was built by **Fabrice Andre**, a Data Science student at **BYU-Idaho**, "
                "to help you navigate the future of work.\n\n"
                "Ask me anything about how AI will impact your career, what to study, "
                "or which jobs are safest. I'm here to help!\n\n"
                "Try asking: 'What careers are safest from AI?' or 'Tell me about nursing'"
            )

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
