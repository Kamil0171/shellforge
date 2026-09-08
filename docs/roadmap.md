# Roadmapa projektu ShellForge

ShellForge jest polskojęzyczną platformą do praktycznej nauki Linuxa, administracji systemami, sieci i bezpieczeństwa, wdrażania aplikacji oraz podstaw DevOps.

Roadmapa opisuje aktualny stan i kierunek rozwoju projektu. Sekcja przyszłych pomysłów nie jest zobowiązaniem do wdrożenia wszystkich wymienionych elementów i nie określa terminów realizacji.

## Zrealizowane

### Fundament platformy

- aplikacja FastAPI z widokami Jinja2;
- konfiguracja SQLite i modele SQLModel;
- synchronizacja treści edukacyjnych podczas startu aplikacji;
- responsywny interfejs oparty na Bootstrapie, CSS i JavaScript;
- publiczne wdrożenie pod domeną `shellforge.pl` z HTTPS.

### Nauka i utrwalanie

- lekcje z teorią, komendami, zadaniami i podsumowaniem;
- quizy sprawdzające praktyczne zrozumienie materiału;
- fiszki do szybkiej powtórki;
- panel z podsumowaniem zawartości;
- ścieżka nauki;
- wyszukiwanie i filtrowanie lekcji;
- podział listy lekcji na moduły tematyczne;
- nawigacja do poprzedniej i następnej lekcji;
- materiały z podstaw terminala, administracji systemem, sieci i bezpieczeństwa oraz wdrażania aplikacji.

### Praktyka

- Symulator „Dyżur administratora”;
- Dynamic Incident: poziomy łatwy i średni oraz pięć kategorii awarii zależności;
- data-driven Modern NOC, kamera i stopniowe odkrywanie świata;
- wielohostowy Virtual Rocky z izolowanym stanem hostów, kontrolowanym `ssh`, edytorem plików, DNF/YUM, siecią i systemd;
- interaktywne środowisko scenariusza wykorzystujące Phaser 3;
- symulowany terminal i działania administracyjne;
- cele incydentu, postęp i punktacja;
- stopniowane podpowiedzi, runbooki i walidowane rozwiązania referencyjne;
- limity wejścia, wygasanie sesji oraz kontrola liczby aktywnych sesji;
- typowany graf zależności, propagacja symptomów i stanowe cele Validatora V3;
- data-only fundament przyszłego generatora AI, bez podłączonego modelu lub zewnętrznego API;
- raport po ukończeniu incydentu z przyczyną, działaniami naprawczymi i końcowym stanem.

### Jakość i utrzymanie repozytorium

- testy automatyczne w pytest;
- kontrola jakości kodu przez Ruff;
- GitHub Actions uruchamiający testy i kontrolę jakości kodu;
- Dependabot sprawdzający aktualizacje zależności Pythona i akcji GitHub.

## Aktualny kierunek

- dalszy rozwój treści z obszaru DevOps i automatyzacji;
- rozwijanie materiałów opartych na praktycznych problemach administracyjnych;
- doskonalenie spójności między lekcjami, utrwalaniem wiedzy i Symulatorem;
- utrzymanie jakości, czytelności i aktualności dokumentacji projektu.

## Pomysły na przyszłość

Poniższe kierunki są pomysłami do rozważenia, a nie deklaracją terminów lub kompletnego zakresu wdrożenia:

- kolejne scenariusze incydentów administracyjnych;
- dalsze materiały o automatyzacji testów i wdrożeń;
- praktyczne podstawy konteneryzacji;
- monitorowanie aplikacji i usług;
- metryki, alerty i analiza logów;
- procedury utrzymaniowe, kopie zapasowe i odtwarzanie;
- rozwijanie narzędzi do praktycznego sprawdzania wiedzy.

## Zasady rozwoju

- najpierw prostota i wartość edukacyjna;
- małe, logiczne zmiany łatwe do sprawdzenia;
- funkcje oparte na rzeczywistych potrzebach użytkownika;
- brak fikcyjnych terminów i obietnic dotyczących pomysłów przyszłych;
- dokumentacja aktualizowana razem z rzeczywistym stanem projektu.
