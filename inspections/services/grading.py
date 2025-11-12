import logging
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from django.conf import settings

from inspections.models import Inspection, Restaurant

logger = logging.getLogger(__name__)

ALLOWED_YEARS: Sequence[int] = (2021, 2022, 2023, 2024, 2025)


@dataclass
class ForbiddenHit:
    year: int
    term: str
    context: str

    def to_dict(self) -> Dict[str, object]:
        return {"year": self.year, "term": self.term, "context": self.context}


@dataclass
class NegatedHit:
    year: int
    term: str
    negation: str
    context: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "year": self.year,
            "term": self.term,
            "negation": self.negation,
            "context": self.context,
        }


@dataclass
class GradeResult:
    regraded_letter: str
    star_rating: int
    forbidden_years: Dict[str, Optional[bool]]
    explanations: Dict[str, object] = field(default_factory=dict)

    def as_update_kwargs(self) -> Dict[str, object]:
        return {
            "regraded_letter": self.regraded_letter,
            "star_rating": self.star_rating,
            "forbidden_years": self.forbidden_years,
            "grading_explanations": self.explanations,
        }


class GradingService:
    def __init__(
        self,
        forbidden_terms: Optional[Sequence[str]] = None,
        negation_terms: Optional[Sequence[str]] = None,
        lowest_grade: Optional[str] = None,
    ):
        self.forbidden_terms = tuple(forbidden_terms or getattr(settings, "FORBIDDEN_TERMS", ()))
        self.negation_terms = tuple(negation_terms or getattr(settings, "NEGATION_TERMS", ()))
        self.lowest_grade = lowest_grade or getattr(settings, "LOWEST_GRADE", "C")

        if not self.forbidden_terms:
            raise ValueError("FORBIDDEN_TERMS configuration cannot be empty.")

        self._forbidden_patterns: Tuple[re.Pattern[str], ...] = tuple(
            re.compile(rf"\b({re.escape(term)})\b", re.IGNORECASE) for term in self.forbidden_terms
        )
        self._negation_sequences: Tuple[Tuple[str, ...], ...] = tuple(
            tuple(term.lower().split()) for term in self.negation_terms
        )

    def grade_restaurant(self, restaurant: Restaurant) -> GradeResult:
        prefetched_cache = getattr(restaurant, "_prefetched_objects_cache", {})
        prefetched = prefetched_cache.get("inspections") if isinstance(prefetched_cache, dict) else None
        if prefetched is not None:
            inspections = [
                inspection
                for inspection in prefetched
                if inspection.date and inspection.date.year in ALLOWED_YEARS
            ]
            inspections.sort(key=lambda inspection: inspection.date, reverse=True)
        else:
            inspections = restaurant.inspections.filter(date__year__in=ALLOWED_YEARS).order_by("-date")
        result = self.grade_from_inspections(inspections)
        logger.info(
            "Restaurant graded",
            extra={
                "restaurant_id": restaurant.pk,
                "restaurant_camis": restaurant.camis,
                "restaurant_name": restaurant.name,
                "rules_applied": result.explanations.get("rules_applied"),
                "forbidden_years": result.forbidden_years,
            },
        )
        return result

    def grade_from_inspections(self, inspections: Iterable[Inspection]) -> GradeResult:
        by_year: Dict[int, Dict[str, object]] = {
            year: {"has_data": False, "forbidden": False} for year in ALLOWED_YEARS
        }
        forbidden_hits: List[ForbiddenHit] = []
        negated_hits: List[NegatedHit] = []

        total_inspections = 0

        for inspection in inspections:
            if not inspection.date:
                continue
            year = inspection.date.year
            if year not in by_year:
                continue
            total_inspections += 1
            by_year[year]["has_data"] = True
            text = self._compose_inspection_text(inspection)
            if not text:
                continue
            hits, negations = self._analyze_text(text, year)

            if hits:
                by_year[year]["forbidden"] = True
                forbidden_hits.extend(hits)
            if negations:
                negated_hits.extend(negations)

        if total_inspections == 0:
            explanations = {
                "rules_applied": ["RULE_UNKNOWN_NO_DATA", "STARS_2_DEFAULT"],
                "forbidden_hits": [hit.to_dict() for hit in forbidden_hits],
                "negations": [neg.to_dict() for neg in negated_hits],
                "forbidden_years": self._format_forbidden_years(by_year, include_none=True),
            }
            logger.info("No inspection data available for grading.")
            return GradeResult(
                regraded_letter="Unknown",
                star_rating=2,
                forbidden_years=self._format_forbidden_years(by_year, include_none=True),
                explanations=explanations,
            )

        letter_rule, regraded_letter = self._determine_letter_grade(by_year)
        star_rule, star_rating = self._determine_star_rating(by_year)

        explanations = {
            "rules_applied": [letter_rule, star_rule],
            "forbidden_hits": [hit.to_dict() for hit in forbidden_hits],
            "negations": [neg.to_dict() for neg in negated_hits],
            "forbidden_years": self._format_forbidden_years(by_year, include_none=True),
        }

        logger.info(
            "Grading result",
            extra={
                "letter_rule": letter_rule,
                "star_rule": star_rule,
                "regraded_letter": regraded_letter,
                "star_rating": star_rating,
                "forbidden_years": explanations["forbidden_years"],
            },
        )

        return GradeResult(
            regraded_letter=regraded_letter,
            star_rating=star_rating,
            forbidden_years=self._format_forbidden_years(by_year, include_none=True),
            explanations=explanations,
        )

    def _compose_inspection_text(self, inspection: Inspection) -> str:
        parts = [inspection.summary or "", inspection.action or ""]
        return " ".join(part for part in parts if part).strip()

    def _analyze_text(self, text: str, year: int) -> Tuple[List[ForbiddenHit], List[NegatedHit]]:
        if not text:
            return [], []

        lowered = text.lower()
        tokens_with_pos = list(re.finditer(r"\b\w+\b", lowered))
        tokens = [match.group(0) for match in tokens_with_pos]
        token_positions = [match.start() for match in tokens_with_pos]

        forbidden_matches: List[ForbiddenHit] = []
        negated_matches: List[NegatedHit] = []
        for pattern in self._forbidden_patterns:
            for match in pattern.finditer(lowered):
                token_index = self._find_token_index(token_positions, match.start(), match.end())
                if token_index is None:
                    continue
                negation = self._find_negation(tokens, token_index)
                original_term = text[match.start() : match.end()]
                context = self._extract_context(text, match.start(), match.end())
                if negation:
                    negated_matches.append(
                        NegatedHit(year=year, term=original_term, negation=negation, context=context)
                    )
                else:
                    forbidden_matches.append(
                        ForbiddenHit(year=year, term=original_term, context=context)
                    )
        return forbidden_matches, negated_matches

    def _find_token_index(self, positions: List[int], start: int, end: int) -> Optional[int]:
        for idx, pos in enumerate(positions):
            if pos >= start and pos < end:
                return idx
            if pos > end:
                break
        return None

    def _find_negation(self, tokens: List[str], token_index: int) -> Optional[str]:
        window = 3
        for negation_sequence in self._negation_sequences:
            length = len(negation_sequence)
            if length == 0:
                continue
            start_limit = max(0, token_index - window)
            last_start = token_index - length
            for start_idx in range(last_start, start_limit - 1, -1):
                if start_idx < 0:
                    continue
                end_idx = start_idx + length
                if end_idx > token_index:
                    continue
                segment = tokens[start_idx:end_idx]
                if tuple(segment) == negation_sequence:
                    return " ".join(segment)
        return None

    def _extract_context(self, text: str, start: int, end: int, radius: int = 40) -> str:
        begin = max(start - radius, 0)
        finish = min(end + radius, len(text))
        snippet = text[begin:finish]
        return snippet.strip()

    def _determine_letter_grade(self, by_year: Dict[int, Dict[str, object]]) -> Tuple[str, str]:
        flag = lambda year: bool(by_year[year]["forbidden"])
        if flag(2025) or flag(2024):
            return "RULE_1_LOWEST_RECENT", self.lowest_grade
        if flag(2023) and not flag(2024) and not flag(2025):
            return "RULE_2_B_2023_ONLY", "B"
        if (flag(2022) or flag(2021)) and not (flag(2023) or flag(2024) or flag(2025)):
            return "RULE_3_A_OLD_ONLY", "A"
        if not any(flag(year) for year in ALLOWED_YEARS):
            return "RULE_4_A_ALL_CLEAN", "A"
        # Fallback: conservatively return lowest grade
        return "RULE_FALLBACK_LOWEST", self.lowest_grade

    def _determine_star_rating(self, by_year: Dict[int, Dict[str, object]]) -> Tuple[str, int]:
        def has_data(year: int) -> bool:
            return bool(by_year[year]["has_data"])

        def flag(year: int) -> bool:
            return bool(by_year[year]["forbidden"])

        def window_clean(years: Sequence[int]) -> bool:
            if not all(has_data(year) for year in years):
                return False
            return all(not flag(year) for year in years)

        if flag(2025):
            return "STARS_1_RECENT_FORBIDDEN", 1

        if window_clean(ALLOWED_YEARS):
            return "STARS_4_CLEAN_SINCE_2021", 4

        if window_clean((2022, 2023, 2024, 2025)):
            return "STARS_3_CLEAN_SINCE_2022", 3

        if window_clean((2023, 2024, 2025)):
            return "STARS_2_CLEAN_SINCE_2023", 2

        if window_clean((2024, 2025)):
            return "STARS_2_CLEAN_SINCE_2024", 2

        return "STARS_2_DEFAULT", 2

    def _format_forbidden_years(
        self, by_year: Dict[int, Dict[str, object]], include_none: bool = False
    ) -> Dict[str, Optional[bool]]:
        formatted: Dict[str, Optional[bool]] = {}
        for year in ALLOWED_YEARS:
            has_data = bool(by_year[year]["has_data"])
            if not has_data and not include_none:
                continue
            formatted[str(year)] = bool(by_year[year]["forbidden"]) if has_data else None
        return formatted


def grade_restaurants(restaurants: Iterable[Restaurant], service: Optional[GradingService] = None) -> None:
    service = service or GradingService()
    for restaurant in restaurants:
        result = service.grade_restaurant(restaurant)
        Restaurant.objects.filter(pk=restaurant.pk).update(**result.as_update_kwargs())

