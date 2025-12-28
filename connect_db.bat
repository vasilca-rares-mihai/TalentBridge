@echo off
echo Se conecteaza la containerul talent-bridge-db...

:: Comanda de mai jos intra in container si ruleaza direct mariadb pe baza de date specificata
docker exec -it talent-bridge-db mariadb -u root -p db_talentbridge

:: Aceasta linie tine fereastra deschisa in caz de eroare, dupa ce iesi din DB
pause