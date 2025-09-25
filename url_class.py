from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List


@dataclass
class Code:
    link: str


@dataclass
class Dataset:
    link: str
    namespace: str = ""
    repo: str = ""
    rev: str = ""

@dataclass
class Model:
    # www.huggingface.co\namespace\repo\rev
    link: str 
    namespace: str = ""
    repo: str = ""
    rev: str = ""


@dataclass
class ProjectGroup:
    code: Optional[Code] = None
    dataset: Optional[Dataset] = None
    model: Optional[Model] = None


def parse_project_file(filepath: str | Path) -> List[ProjectGroup]:
    """
    Parse a text file where each line has format:
        code_link,dataset_link,model_link

    Each line corresponds to a grouped set of links.
    Empty fields are allowed (e.g., ',,http://model.com').

    Args:
        filepath: Path to the input file.

    Returns:
        A list of ProjectGroup objects containing Code, Dataset, and/or Model.
    """
    project_groups: List[ProjectGroup] = []
    path = Path(filepath)

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:  # skip empty lines
                continue

            parts = [p.strip() for p in line.split(",")]
            # Pad with None if fewer than 3 entries
            while len(parts) < 3:
                parts.append("")

            code_link, dataset_link, model_link = parts

            group = ProjectGroup(
                code=Code(code_link) if code_link else None,
                dataset=Dataset(dataset_link) if dataset_link else None,
                model=Model(model_link) if model_link else None,
            )
            project_groups.append(group)

    return project_groups


def main():
    # Point to your test file
    filepath = Path("tests/test.txt")

    # Parse file
    groups = parse_project_file(filepath)

    # Print results
    print("Parsed project groups:\n")
    for i, group in enumerate(groups, start=1):
        print(f"Group {i}: {group}")


if __name__ == "__main__":
    main()