"""Получение зависимостей из настоящего репозитория NuGet.

Файл скачивает ``.nupkg``, читает ``.nuspec`` внутри ZIP-архива и получает
список версий без менеджеров пакетов и сторонних библиотек.
"""

from __future__ import annotations

import json
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from .models import Dependency
from .versioning import VersionError, select_version


class NuGetError(Exception):
    """Ошибка обращения к репозиторию NuGet."""


class NuGetRepository:
    """Клиент NuGet V3 Flat Container без сторонних библиотек."""

    def __init__(self, base_url: str, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_direct_dependencies(
        self, package_name: str, package_version: str
    ) -> list[Dependency]:
        """Скачать пакет и прочитать зависимости из `.nuspec`."""
        url = self.package_url(package_name, package_version)
        data = self._download(url)
        return self.dependencies_from_package(data)

    def package_url(self, package_name: str, package_version: str) -> str:
        """Сформировать URL файла `.nupkg`."""
        name = quote(package_name.lower(), safe="._-")
        version = quote(package_version.lower(), safe="._-+")
        filename = f"{name}.{version}.nupkg"
        return f"{self.base_url}/{name}/{version}/{filename}"

    def versions_url(self, package_name: str) -> str:
        """Сформировать URL списка версий пакета."""
        name = quote(package_name.lower(), safe="._-")
        return f"{self.base_url}/{name}/index.json"

    def get_versions(self, package_name: str) -> list[str]:
        """Получить доступные версии пакета."""
        payload = self._download(self.versions_url(package_name))
        try:
            document = json.loads(payload.decode("utf-8"))
            versions = document["versions"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError) as error:
            raise NuGetError("некорректный список версий NuGet") from error
        if not isinstance(versions, list):
            raise NuGetError("поле versions должно быть списком")
        return [str(version) for version in versions]

    def resolve_version(self, package_name: str, version_spec: str) -> str:
        """Выбрать конкретную версию по ограничению из `.nuspec`."""
        versions = self.get_versions(package_name)
        try:
            return select_version(versions, version_spec)
        except VersionError as error:
            message = f"не удалось выбрать версию {package_name}: {error}"
            raise NuGetError(message) from error

    @staticmethod
    def dependencies_from_package(data: bytes) -> list[Dependency]:
        """Извлечь прямые зависимости из содержимого `.nupkg`."""
        try:
            with ZipFile(BytesIO(data)) as archive:
                names = [
                    name for name in archive.namelist()
                    if name.lower().endswith(".nuspec")
                ]
                if len(names) != 1:
                    raise NuGetError("пакет должен содержать один .nuspec")
                nuspec = archive.read(names[0])
        except (BadZipFile, KeyError) as error:
            raise NuGetError(f"некорректный пакет NuGet: {error}") from error
        return NuGetRepository._parse_nuspec(nuspec)

    @staticmethod
    def _parse_nuspec(data: bytes) -> list[Dependency]:
        try:
            root = ElementTree.fromstring(data)
        except ElementTree.ParseError as error:
            raise NuGetError(f"некорректный XML nuspec: {error}") from error
        dependencies: set[Dependency] = set()
        for element in root.iter():
            if _local_name(element.tag) != "dependency":
                continue
            name = (element.get("id") or "").strip()
            version = (element.get("version") or "").strip()
            if not name:
                raise NuGetError("у зависимости отсутствует id")
            dependencies.add(Dependency(name, version))
        return sorted(
            dependencies,
            key=lambda item: (item.name.lower(), item.version_spec),
        )

    def _download(self, url: str) -> bytes:
        request = Request(url, headers={"User-Agent": "dependency-tool/1.0"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return response.read()
        except HTTPError as error:
            message = f"NuGet вернул HTTP {error.code}: {url}"
            raise NuGetError(message) from error
        except URLError as error:
            message = f"не удалось обратиться к NuGet: {error.reason}"
            raise NuGetError(message) from error


def _local_name(tag: str) -> str:
    """Удалить XML-пространство имён из тега."""
    return tag.rsplit("}", maxsplit=1)[-1]

