"""지식 베이스 로더 및 파서"""
import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class QAItem:
    number: int
    question: str
    answer: str
    section: str
    images: list[str] = field(default_factory=list)


def load_knowledge_base(file_path: Path) -> str:
    """마크다운 파일을 읽어서 전체 텍스트를 반환합니다."""
    return file_path.read_text(encoding="utf-8")


def parse_qa_items(text: str) -> list[QAItem]:
    """마크다운에서 Q&A 항목을 파싱합니다."""
    items = []
    current_section = ""

    # 섹션 헤더 추출
    section_pattern = re.compile(r"^### ([A-Z])\.\s+(.+)$", re.MULTILINE)
    sections = {m.start(): m.group(1) for m in section_pattern.finditer(text)}
    section_positions = sorted(sections.keys())

    # Q&A 파싱
    q_pattern = re.compile(
        r"\*\*Q(\d+)\.\s*(.+?)\*\*.*?답변[:：]\s*(.+?)(?=\*\*Q\d+\.|\n## |\n### |---\n|\Z)",
        re.DOTALL,
    )

    for match in q_pattern.finditer(text):
        q_pos = match.start()
        # 현재 섹션 결정
        for sp in section_positions:
            if sp < q_pos:
                current_section = sections[sp]

        number = int(match.group(1))
        question = match.group(2).strip()
        answer = match.group(3).strip()

        # 이미지 참조 추출
        images = re.findall(r"!\[.*?\]\((image[^)]*\.png)\)", answer)

        items.append(
            QAItem(
                number=number,
                question=question,
                answer=answer,
                section=current_section,
                images=images,
            )
        )

    return items


def extract_image_refs(text: str) -> list[str]:
    """텍스트에서 [IMAGE:파일명] 패턴의 이미지 참조를 추출합니다."""
    return re.findall(r"\[IMAGE:(image[^\]]*\.png)\]", text)
