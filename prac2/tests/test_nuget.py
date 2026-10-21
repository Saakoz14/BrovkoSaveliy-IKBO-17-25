"""Тесты чтения пакетов NuGet."""

import unittest
from io import BytesIO
from zipfile import ZipFile

from src.models import Dependency
from src.nuget import NuGetError, NuGetRepository


NUSPEC = b"""<?xml version="1.0"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>Example</id>
    <version>1.0.0</version>
    <dependencies>
      <group targetFramework="net8.0">
        <dependency id="Alpha" version="[1.0.0,2.0.0)" />
        <dependency id="Beta" version="3.0.0" />
      </group>
    </dependencies>
  </metadata>
</package>
"""


def make_package(nuspec: bytes = NUSPEC) -> bytes:
    """Создать тестовый `.nupkg` в памяти."""
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        archive.writestr("Example.nuspec", nuspec)
    return stream.getvalue()


class NuGetRepositoryTest(unittest.TestCase):
    """Проверка URL и извлечения прямых зависимостей."""

    def setUp(self) -> None:
        self.repository = NuGetRepository(
            "https://api.nuget.org/v3-flatcontainer/"
        )

    def test_builds_flat_container_url(self) -> None:
        url = self.repository.package_url("Example.Package", "1.2.3")
        expected = (
            "https://api.nuget.org/v3-flatcontainer/"
            "example.package/1.2.3/example.package.1.2.3.nupkg"
        )
        self.assertEqual(url, expected)

    def test_extracts_dependencies_from_nuspec(self) -> None:
        dependencies = self.repository.dependencies_from_package(
            make_package()
        )
        self.assertEqual(
            dependencies,
            [
                Dependency("Alpha", "[1.0.0,2.0.0)"),
                Dependency("Beta", "3.0.0"),
            ],
        )

    def test_rejects_invalid_archive(self) -> None:
        with self.assertRaisesRegex(NuGetError, "некорректный пакет"):
            self.repository.dependencies_from_package(b"not a zip")

    def test_rejects_invalid_nuspec(self) -> None:
        package = make_package(b"<package>")
        with self.assertRaisesRegex(NuGetError, "некорректный XML"):
            self.repository.dependencies_from_package(package)


if __name__ == "__main__":
    unittest.main()

