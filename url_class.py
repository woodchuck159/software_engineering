from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List


@dataclass
class Code:
    link: str
    namespace: str = ""


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


from typing import Tuple
from urllib.parse import urlparse

def parse_huggingface_url(url: str) -> Tuple[str, str, str]:
   
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError(f"Invalid Hugging Face URL: {url}")

    namespace = parts[0]
    repo = parts[1]
    rev = ""

    # If the URL has /tree/<rev>, capture it
    if len(parts) >= 4 and parts[2] == "tree":
        rev = parts[3]

    return namespace, repo, rev

def parse_hf_dataset_url_repo(url: str) -> str:
    """
    Extract only the repo (dataset name) from a Hugging Face dataset URL.
    Example: 
        https://huggingface.co/datasets/stanfordnlp/imdb -> "imdb"
        https://huggingface.co/datasets/glue -> "glue"
    """
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2 or parts[0] != "datasets":
        raise ValueError(f"Invalid Hugging Face dataset URL: {url}")

    return parts[-1]   # last segment is always the repo

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

    with path.open("r", encoding="ASCII") as f:
        for line in f:
            line = line.strip()
            if not line:  # skip empty lines
                continue

            parts = [p.strip() for p in line.split(",")]
            # Pad with None if fewer than 3 entries
            while len(parts) < 3:
                parts.append("")

            code_link, dataset_link, model_link = parts

            if model_link != None and model_link != '':
                ns, rp, rev = parse_huggingface_url(model_link) if model_link else ("", "", "")
            if dataset_link != None and dataset_link != '':
                data_repo = parse_hf_dataset_url_repo(dataset_link)

            group = ProjectGroup(
                code=Code(code_link) if code_link else None,
                dataset=Dataset(dataset_link, namespace="", repo=data_repo, rev="") if dataset_link else None,
                model=Model(model_link, ns, rp, rev) if model_link else None,
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
    url = "https://huggingface.co/openai-community/gpt2"
    ns, rp = parse_huggingface_url(url)
    print(f"Namespace: {ns}, Repo: {rp}")
    # Output: Namespace: openai-community, Repo: gpt2