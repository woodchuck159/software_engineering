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

    if len(parts) < 1:
        raise ValueError(f"Invalid Hugging Face URL: {url}")
    
    if len(parts) == 1:
        repo = parts[0]
        namespace = url.strip("/").split("-")[0]
        rev = "main"
        return namespace, repo, rev

    namespace = parts[0]
    repo = parts[1]
    rev = "main"

    # If the URL has /tree/<rev>, capture it
    if len(parts) >= 4 and parts[2] == "tree":
        rev = parts[3]

    return namespace, repo, rev

from urllib.parse import urlparse

from urllib.parse import urlparse

def parse_dataset_url(url: str) -> str:
    """
    Parse a dataset URL and return the appropriate identifier for loading.
    
    - Hugging Face datasets: returns only the repo name
        Example: 
            https://huggingface.co/datasets/stanfordnlp/imdb -> "imdb"
            https://huggingface.co/datasets/glue -> "glue"
    
    - GitHub repos: returns the full URL (used directly for git clone)
        Example:
            https://github.com/zalandoresearch/fashion-mnist -> "https://github.com/zalandoresearch/fashion-mnist"
    
    Raises:
        ValueError: if the URL is not recognized.
    """
    parsed = urlparse(url)

    # Hugging Face case
    if "huggingface.co" in parsed.netloc:
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2 or parts[0] != "datasets":
            raise ValueError(f"Invalid Hugging Face dataset URL: {url}")
        return parts[-1]  # only the repo name, e.g. "imdb"

    # GitHub case
    if "github.com" in parsed.netloc:
        return url  # keep full URL for git clone

    raise ValueError(f"Unsupported dataset URL: {url}")
    

def parse_project_file(filepath: str) -> List[ProjectGroup]:
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
                ns, rp, rev = parse_huggingface_url(model_link) if model_link else ("", "", "main")
            if dataset_link != None and dataset_link != '':
                data_repo = parse_dataset_url(dataset_link)

            group = ProjectGroup(
                code=Code(code_link),
                dataset=Dataset(dataset_link, namespace="", repo=data_repo, rev=""),
                model=Model(model_link, ns, rp, rev),
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
