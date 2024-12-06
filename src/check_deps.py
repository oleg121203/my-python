import pkg_resources
import sys


def check_requirements(requirements_file):
    # Читаем requirements.txt
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip()
                        and not line.startswith('#')]

    # Проверяем каждую зависимость
    missing = []
    installed = []

    for requirement in requirements:
        try:
            pkg_resources.require(requirement)
            installed.append(requirement)
        except (pkg_resources.DistributionNotFound,
                pkg_resources.VersionConflict):
            missing.append(requirement)

    return installed, missing


if __name__ == "__main__":
    installed, missing = check_requirements("requirements.txt")

    print("\nУстановленные пакеты:")
    for pkg in installed:
        print(f"✓ {pkg}")

    if missing:
        print("\nОтсутствующие пакеты:")
        for pkg in missing:
            print(f"✗ {pkg}")
    else:
        print("\nВсе зависимости установлены корректно!")
