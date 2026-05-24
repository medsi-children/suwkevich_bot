from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosticDomain:
    key: str
    title: str
    knowledge_tags: tuple[str, ...]
    primary_markers: tuple[str, ...]
    supporting_markers: tuple[str, ...]
    question_focus: tuple[str, ...]


DOMAINS: tuple[DiagnosticDomain, ...] = (
    DiagnosticDomain(
        key="suicide_self_harm",
        title="суицидальный риск / самоповреждение",
        knowledge_tags=("suicide", "self_harm", "crisis", "risk_assessment"),
        primary_markers=(
            "не хочу жить",
            "самоуб",
            "суицид",
            "свести счеты",
            "умереть",
            "убить себя",
            "выйти в окно",
            "порез",
            "самоповреж",
            "навредить себе",
            "передоз",
        ),
        supporting_markers=(
            "не справляюсь",
            "не вижу смысла",
            "прощаюсь",
            "раздал вещи",
            "один дома",
            "таблетки",
            "лезвие",
            "кровь",
            "наказал себя",
        ),
        question_focus=(
            "намерение умереть",
            "план и доступ к средствам",
            "недавние попытки",
            "один ли пользователь сейчас",
        ),
    ),
    DiagnosticDomain(
        key="psychosis_prodrome",
        title="психоз / продром / потеря критики",
        knowledge_tags=("psychosis", "prodrome", "reality_testing", "aps"),
        primary_markers=(
            "голоса",
            "слышу голос",
            "за мной следят",
            "мной управляют",
            "читают мысли",
            "вкладывают мысли",
            "забирают мысли",
            "особая миссия",
            "тайный смысл",
            "знаки обо мне",
            "инсценировка",
            "мир подстроен",
            "преследуют",
        ),
        supporting_markers=(
            "все намекают",
            "не могу сомневаться",
            "уверен на сто",
            "стал странно говорить",
            "мысли путаются",
            "резко замкнулся",
            "снизилась учеба",
            "плохо сплю",
        ),
        question_focus=(
            "сохранность критики",
            "галлюцинации и идеи воздействия",
            "опасное поведение на фоне убеждений",
            "динамика функционирования",
        ),
    ),
    DiagnosticDomain(
        key="bipolar_mania",
        title="биполярный спектр / гипомания / мания",
        knowledge_tags=("bipolar", "mania", "sleep", "risk_behavior"),
        primary_markers=(
            "сплю 3 часа",
            "сплю по 3 часа",
            "не сплю и не устаю",
            "много энергии",
            "скачка идей",
            "ускорились мысли",
            "грандиоз",
            "особая сила",
            "трачу деньги",
            "рискованные",
            "сексуальная расторможенность",
        ),
        supporting_markers=(
            "антидепрессант",
            "стал не похож",
            "много проектов",
            "раздражительность",
            "конфликтность",
            "эйфория",
            "агрессия",
            "психоз",
            "пав",
        ),
        question_focus=(
            "длительность подъема",
            "потребность во сне и усталость",
            "последствия рискованного поведения",
            "антидепрессанты, стимуляторы и ПАВ",
        ),
    ),
    DiagnosticDomain(
        key="depression_dysthymia",
        title="депрессия / дистимия / ангедония",
        knowledge_tags=("depression", "dysthymia", "anhedonia", "adolescent_depression"),
        primary_markers=(
            "ничего не радует",
            "ангедони",
            "нет сил",
            "апатия",
            "пустота",
            "вина",
            "никчем",
            "не могу встать",
            "не моюсь",
            "не ем",
            "нет смысла",
        ),
        supporting_markers=(
            "раздражительность",
            "снизилась учеба",
            "социально отдалился",
            "сплю весь день",
            "бессонница",
            "соматические жалобы",
            "усталость",
            "тоска",
        ),
        question_focus=(
            "длительность и динамика",
            "ангедония и биологические симптомы",
            "суицидальность",
            "периоды подъема для исключения биполярного спектра",
        ),
    ),
    DiagnosticDomain(
        key="anxiety_panic",
        title="тревога / паника / тревожно-фобические состояния",
        knowledge_tags=("anxiety", "gad", "panic", "phobia", "agoraphobia"),
        primary_markers=(
            "паническая атака",
            "панические атаки",
            "паника",
            "постоянная тревога",
            "тревога почти про все",
            "не могу остановить тревогу",
            "страх умереть",
            "страх сойти с ума",
            "нехватка воздуха",
            "боюсь выходить",
            "боюсь людных мест",
        ),
        supporting_markers=(
            "сердцебиение",
            "дрожь",
            "потею",
            "мышечное напряжение",
            "раздражительность",
            "бессонница",
            "избегаю мест",
            "ожидаю новый приступ",
            "кофеин",
            "стимуляторы",
        ),
        question_focus=(
            "длительность и охват тревоги",
            "внезапность и пик панических симптомов",
            "соматические красные флаги",
            "кофеин, стимуляторы, ПАВ и отмена",
        ),
    ),
    DiagnosticDomain(
        key="ocd",
        title="ОКР / навязчивости / ритуалы",
        knowledge_tags=("ocd", "obsessions", "compulsions", "rituals", "reassurance"),
        primary_markers=(
            "навязчивые мысли",
            "навязчивости",
            "ритуалы",
            "компульсии",
            "мою руки",
            "проверяю по сто раз",
            "перепроверяю",
            "боюсь загрязнения",
            "считаю про себя",
            "если не проверю",
        ),
        supporting_markers=(
            "мытье рук",
            "мысль лезет",
            "не могу перестать",
            "ритуал",
            "счет",
            "проверки",
            "плохая мысль",
            "нужно убедиться",
            "страшные мысли",
        ),
        question_focus=(
            "навязчивость или убежденность",
            "сопротивление и сохранность критики",
            "ритуалы, проверки и избегание",
            "дезадаптация, отказ от еды или воды, суицидальность",
        ),
    ),
    DiagnosticDomain(
        key="ptsd",
        title="ПТСР / травматический стресс",
        knowledge_tags=("ptsd", "trauma", "flashback", "nightmares", "dissociation"),
        primary_markers=(
            "флэшбэк",
            "флешбэк",
            "это происходит снова",
            "кошмары после",
            "после травмы",
            "после насилия",
            "после аварии",
            "после нападения",
            "птср",
            "сильная настороженность после",
        ),
        supporting_markers=(
            "избегаю",
            "кошмары",
            "вздрагиваю",
            "настороженность",
            "диссоциация",
            "стыд",
            "вина",
            "триггер",
            "не могу успокоиться после",
        ),
        question_focus=(
            "было ли травматическое событие",
            "флэшбэки, кошмары и избегание",
            "самоповреждение, алкоголь и ПАВ",
            "нужна ли сначала стабилизация и безопасность",
        ),
    ),
    DiagnosticDomain(
        key="eating_disorder",
        title="РПП / анорексия / булимия",
        knowledge_tags=("eating_disorder", "anorexia", "bulimia", "refeeding"),
        primary_markers=(
            "боюсь набрать вес",
            "страх набрать вес",
            "калории",
            "рвота после еды",
            "слабительные",
            "диуретики",
            "не ем",
            "отказ от еды",
            "безопасные продукты",
            "объедаюсь",
            "переедание",
        ),
        supporting_markers=(
            "похудел",
            "похудела",
            "обмороки",
            "аменорея",
            "холодно",
            "тренировки через силу",
            "стыд после еды",
            "ритуалы еды",
            "контроль",
            "тело",
        ),
        question_focus=(
            "скорость потери веса и медицинские симптомы",
            "страх набора веса и искаженный образ тела",
            "очистительное поведение",
            "риск рефидинг-синдрома при истощении",
        ),
    ),
    DiagnosticDomain(
        key="emotional_dysregulation",
        title="эмоциональная дисрегуляция / ПРЛ-гипотеза",
        knowledge_tags=("bpd", "emotional_dysregulation", "relationships", "dissociation"),
        primary_markers=(
            "страх отвержения",
            "меня бросят",
            "пустота",
            "идеализирую",
            "обесцениваю",
            "качели",
            "эмоциональный шторм",
            "не знаю кто я",
            "нестабильные отношения",
            "самоповреж",
        ),
        supporting_markers=(
            "зависит от сообщения",
            "резкие вспышки",
            "импульсивность",
            "диссоциация",
            "ревность",
            "аддиктив",
            "рискованное поведение",
            "стыд",
        ),
        question_focus=(
            "связь вспышек с отношениями",
            "длительность смены состояния",
            "самоповреждение и импульсивность",
            "отличие от биполярных эпизодов",
        ),
    ),
    DiagnosticDomain(
        key="delirium_cognitive",
        title="делирий / спутанность / когнитивное снижение",
        knowledge_tags=("delirium", "confusion", "disorientation", "cognition", "elderly"),
        primary_markers=(
            "спутанность",
            "дезориентация",
            "дезориентирован",
            "не узнает близких",
            "галлюцинации у пожилого",
            "резко стал странным",
            "не понимает где находится",
            "путает день и ночь",
            "делирий",
        ),
        supporting_markers=(
            "пожилой",
            "после операции",
            "после инфекции",
            "обезвоживание",
            "ухудшение памяти",
            "не может найти дорогу",
            "зрительные галлюцинации",
            "внезапно",
            "сон бодрствование",
        ),
        question_focus=(
            "острое или постепенное начало",
            "внимание, ориентация и нарушение сознания",
            "инфекция, операция, обезвоживание, лекарства",
            "нужна ли срочная медицинская помощь",
        ),
    ),
    DiagnosticDomain(
        key="somatic_substance",
        title="соматические причины / ПАВ / лекарства",
        knowledge_tags=("somatic", "substances", "medication", "intoxication"),
        primary_markers=(
            "алкоголь",
            "каннабис",
            "мефедрон",
            "амфетамин",
            "стимуляторы",
            "психоделик",
            "отмена препарата",
            "начал препарат",
            "энергетики",
            "боль в груди",
            "обморок",
            "судороги",
        ),
        supporting_markers=(
            "сердцебиение",
            "одышка",
            "кровь",
            "температура",
            "спутанность",
            "беременность",
            "послеродовой",
            "резкая потеря веса",
            "слабость",
            "отмена алкоголя",
            "запой",
            "тремор",
            "потливость",
        ),
        question_focus=(
            "ПАВ, лекарства и отмена",
            "острые соматические красные флаги",
            "неврология, эндокринология, кардиология",
            "временная связь симптомов с веществами или препаратами",
        ),
    ),
    DiagnosticDomain(
        key="addiction_withdrawal",
        title="зависимость / синдром отмены / интоксикация",
        knowledge_tags=("addiction", "withdrawal", "intoxication", "alcohol", "substances"),
        primary_markers=(
            "отмена алкоголя",
            "трясет после алкоголя",
            "тремор после запоя",
            "белочка",
            "ломка",
            "абстиненция",
            "галлюцинации после запоя",
            "не пью и трясет",
            "утром выпиваю",
            "запой",
        ),
        supporting_markers=(
            "потливость",
            "тахикардия",
            "бессонница",
            "судороги",
            "дезориентация",
            "спутанность",
            "алкоголь",
            "вчера прекратил",
            "зависимость",
            "передозировка",
        ),
        question_focus=(
            "когда было последнее употребление",
            "судороги, делирий и нарушение дыхания",
            "смешанное употребление и передозировка",
            "нужна ли срочная наркологическая или медицинская помощь",
        ),
    ),
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _marker_hits(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker in text]


def analyze_clinical_domains(text: str, *, limit: int = 3) -> list[dict[str, object]]:
    clean = _normalize(text)
    if not clean:
        return []

    candidates: list[dict[str, object]] = []
    for domain in DOMAINS:
        primary_hits = _marker_hits(clean, domain.primary_markers)
        supporting_hits = _marker_hits(clean, domain.supporting_markers)
        if not primary_hits and len(supporting_hits) < 2:
            continue

        score = len(primary_hits) * 3 + len(supporting_hits)
        if primary_hits and supporting_hits:
            score += 2
        if len(primary_hits) >= 2:
            score += 2

        candidates.append(
            {
                "key": domain.key,
                "title": domain.title,
                "score": score,
                "tags": domain.knowledge_tags,
                "primary_hits": primary_hits[:5],
                "supporting_hits": supporting_hits[:5],
                "question_focus": domain.question_focus,
            }
        )

    return sorted(candidates, key=lambda item: int(item["score"]), reverse=True)[:limit]


def format_domain_context(domains: list[dict[str, object]]) -> str:
    if not domains:
        return ""

    lines = [
        "Вероятные клинические домены для осторожной проверки. Это не диагнозы, "
        "а подсказки для выбора вопросов, оценки риска и дифференциальных гипотез:"
    ]
    for domain in domains:
        focus = "; ".join(str(item) for item in domain.get("question_focus", ()))
        lines.append(f"- {domain['title']}: уточнить {focus}.")
    return "\n".join(lines)
