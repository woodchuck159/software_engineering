from .api import Api
import typing
import requests
import os
import tempfile


class HuggingFaceApi(Api) :
    BASE_URL: str = "https://huggingface.co"
    ENDPOINT: typing.Dict[str, str] = {
        "model_info": "api/models/{model_id}",
        "model_file": "{model_id}/resolve/main/{filename}",
        # Add more endpoints as needed
    }


    def __init__(self):
        super().__init__(self.BASE_URL)


    def set_bearer_token_from_file(self, filepath: str, section: str = "huggingface", key: str = "bearer_token"):
        super().set_bearer_token_from_file(filepath, section=section, key=key)

    def get_model_info(self, model_id: str, endpoint: str = "model_info") -> dict[str, typing.Any] :
        endpoint_temp: str | None = self.ENDPOINT.get(endpoint)
        if not endpoint_temp:
            raise ValueError(f"Invalid Endpoint: '{endpoint_temp}' ")

        api_endpoint: str = endpoint_temp.format(model_id=model_id)
        return self.get(api_endpoint)
    

    def list_model_files(self, model_id: str) -> list[str]:
        info = self.get_model_info(model_id)
        return info.get("siblings", [])


    def download_file(self, model_id: str, filename: str, dest_dir: str | None = None) -> str:
        if dest_dir is None:
            dest_dir = tempfile.mkdtemp()
        url = f"{self.BASE_URL}/{model_id}/resolve/main/{filename}"
        resp = requests.get(url, stream=True)
        if resp.status_code != 200:
            raise Exception(f"Failed to download {filename}: {resp.text}")
        file_path = os.path.join(dest_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return file_path  


    def download_all_files(self, model_id: str, dest_dir: str | None = None) -> list[str]:
        files = self.list_model_files(model_id)
        paths: list[str] = []
        for file_info in files:
            filename: str | None = file_info.get("rfilename") or file_info.get("filename")
            if filename:
                paths.append(self.download_file(model_id, filename, dest_dir))
        return paths
