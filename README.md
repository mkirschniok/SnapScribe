## SnapScribe - dodawanie stopki do zdjęć

### Opis
SnapScribe to prosty program komputerowy, który umożliwia dodanie stopki do zdjęć w sposób zautomatyzowany i masowy (dla całego katalogu).
Możliwe jest dostosowanie rozmiaru oraz koloru (półprzezroczysty biały lub czarny) tekstu stopki.

### Wymagania
Dla wersji do pobrania (.exe): system operacyjny Windows 10/11.
Dla wersji źródłowej: Python 3.8+ oraz biblioteki sys, os, threading, PIL, tkinter.

### Instrukcja
1. Pobierz plik SnapScribe.exe z zakładki Releases (lub samodzielnie skompiluj program z plików źródłowych). **UWAGA! Plik .exe może być błędnie wykrywany jako wirus przez niektóre programy antywirusowe.** Jest to tzw. _false-positive_, program nie zawiera wirusów. Można go dodać do wyjątków w ustawieniach antywirusa.
2. Uruchom program SnapScribe.exe.
3. Wybierz katalog, w którym znajdują się zdjęcia, do których chcesz dodać stopkę.
4. Wybierz kolor tekstu stopki (biały lub czarny).
5. Wprowadź rozmiar tekstu stopki (wartość z zakresu 1-1000).
6. Wpisz tekst, który ma znaleźć się w stopce.
7. Możesz sprawdzić podgląd zmian na wybranym zdjęciu, klikając przycisk "Aktualizuj podgląd".
8. Wybierz, czy chcesz nadpisać oryginalne zdjęcia, czy zapisać zmodyfikowane zdjęcia w nowym katalogu.
9. Kliknij przycisk "Dodaj napis do wszystkich zdjęć" i poczekaj na zakończenie procesu.
10. Gotowe! Zdjęcia zostaną nadpisane lub zapisane w nowym katalogu z dopiskiem "_opisane".

### Licencja
Program SnapScribe jest dostępny na licencji MIT. Więcej informacji w pliku LICENSE.

### Autor
Program SnapScribe został stworzony przez Michała Kirschniok w ramach projektu z przedmiotu "Praktyka Programowania w Języku Python" na Politechnice Śląskiej. 