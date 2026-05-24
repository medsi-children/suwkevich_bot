from app.services.clinical_knowledge import get_clinical_knowledge_context
from app.services.diagnostic_domains import analyze_clinical_domains, format_domain_context


def test_detects_bipolar_mania_domain_from_marker_combination() -> None:
    domains = analyze_clinical_domains(
        "Три дня сплю по 3 часа и не устаю, много энергии, трачу деньги и "
        "начал слишком много проектов."
    )

    assert domains
    assert domains[0]["key"] == "bipolar_mania"
    assert "потребность во сне" in format_domain_context(domains)


def test_detects_psychosis_domain_without_calling_it_diagnosis() -> None:
    domains = analyze_clinical_domains(
        "Иногда кажется, что за мной следят, а песни дают знаки обо мне."
    )

    assert domains
    assert domains[0]["key"] == "psychosis_prodrome"
    assert "психоз" in str(domains[0]["title"])


def test_detects_ocd_domain_from_obsessions_and_rituals() -> None:
    domains = analyze_clinical_domains(
        "Меня мучают навязчивые мысли, я перепроверяю дверь по сто раз и мою руки, "
        "иначе тревога становится невыносимой."
    )

    assert domains
    assert domains[0]["key"] == "ocd"
    assert "ритуалы" in format_domain_context(domains)


def test_knowledge_context_prefers_relevant_disorder_file() -> None:
    context = get_clinical_knowledge_context(
        "Я слышу голоса, кажется, за мной следят, и я не уверен, могу ли сомневаться."
    )

    assert "disorders/psychosis_prodrome.md" in context
    assert "сохранность критики" in context


def test_knowledge_context_uses_guidelines_for_panic_and_somatic_red_flags() -> None:
    context = get_clinical_knowledge_context(
        "У меня паническая атака с сердцебиением и страхом смерти, но еще боль в груди "
        "и это вообще первый такой эпизод."
    )

    assert "disorders/anxiety_panic.md" in context or "clinical_guidelines_minzdrav.md" in context
    assert "боль в груди" in context
