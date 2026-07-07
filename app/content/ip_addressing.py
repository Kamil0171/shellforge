IP_ADDRESSING = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Podstawy adresacji IP",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Poznasz podstawy adresów IPv4, masek, sieci, hostów, prywatnych zakresów adresów "
            "oraz pierwsze komendy do sprawdzania konfiguracji sieci w Linuxie."
        ),
        "theory": (
            "Adres IP identyfikuje urządzenie w sieci. W codziennej administracji najczęściej spotkasz "
            "adresy IPv4 zapisane jako cztery liczby oddzielone kropkami, na przykład "
            "<code>192.168.1.20</code>. Sam adres nie wystarcza do zrozumienia sieci, bo potrzebna jest "
            "maska albo zapis CIDR, na przykład <code>/24</code>. Maska określa, która część adresu "
            "opisuje sieć, a która konkretny host. Dla <code>192.168.1.20/24</code> siecią jest zwykle "
            "<code>192.168.1.0</code>, a hostem jedno urządzenie w tym zakresie. Brama domyślna to router, "
            "przez który system wysyła ruch poza lokalną sieć. W praktyce początkujący administrator "
            "powinien umieć odpowiedzieć na trzy pytania: jaki adres ma interfejs, jaka jest trasa "
            "domyślna i czy adres należy do sieci prywatnej. Prywatne zakresy IPv4 to "
            "<code>10.0.0.0/8</code>, <code>172.16.0.0/12</code> oraz <code>192.168.0.0/16</code>. "
            "Są używane w sieciach domowych, firmowych i laboratoryjnych, a do Internetu zwykle wychodzą "
            "przez NAT. Komenda <code>ip addr</code> pokazuje adresy przypisane do interfejsów, a "
            "<code>ip route</code> pokazuje trasy, w tym trasę domyślną oznaczoną słowem "
            "<code>default</code>."
        ),
        "commands": [
            {
                "command": "ip addr",
                "description": "Pokazuje interfejsy sieciowe i przypisane do nich adresy IP.",
                "example": "$ ip addr",
            },
            {
                "command": "ip -4 addr",
                "description": "Pokazuje tylko adresy IPv4 skonfigurowane w systemie.",
                "example": "$ ip -4 addr",
            },
            {
                "command": "ip addr show dev eth0",
                "description": "Wyświetla adresy konkretnego interfejsu, jeśli taki interfejs istnieje.",
                "example": "$ ip addr show dev eth0",
            },
            {
                "command": "ip route",
                "description": "Pokazuje tablicę routingu, czyli decyzje systemu o wysyłaniu pakietów.",
                "example": "$ ip route",
            },
            {
                "command": "ip route show default",
                "description": "Pokazuje trasę domyślną używaną do ruchu poza lokalną sieć.",
                "example": "$ ip route show default",
            },
            {
                "command": "hostname -I",
                "description": "Wyświetla adresy IP przypisane do hosta w krótkiej formie.",
                "example": "$ hostname -I",
            },
        ],
        "practice_task": (
            "Na maszynie laboratoryjnej uruchom <code>ip -4 addr</code> i znajdź aktywny interfejs "
            "z adresem IPv4. Zapisz adres wraz z prefiksem, na przykład <code>/24</code>. Następnie "
            "wykonaj <code>ip route</code> i odszukaj wpis zaczynający się od <code>default</code>. "
            "Sprawdź, czy adres hosta należy do jednego z prywatnych zakresów IPv4. Na końcu porównaj "
            "wynik z <code>hostname -I</code> i opisz, który adres jest adresem hosta, a który wpis "
            "wskazuje bramę domyślną."
        ),
        "common_mistakes": [
            "Mylenie adresu hosta z adresem całej sieci.",
            "Pomijanie maski lub prefiksu CIDR przy analizie adresu.",
            "Zakładanie, że każdy adres 192.168.x.x jest dostępny z Internetu.",
            "Mylenie bramy domyślnej z adresem DNS.",
            "Analizowanie tylko nazwy interfejsu bez sprawdzenia, czy ma adres IPv4.",
            "Uznawanie braku trasy default za problem DNS zamiast problem routingu.",
        ],
        "summary": (
            "Adres IPv4 składa się z części sieci i części hosta, a granicę określa maska lub prefiks "
            "CIDR. Prywatne zakresy IPv4 to <code>10.0.0.0/8</code>, <code>172.16.0.0/12</code> "
            "i <code>192.168.0.0/16</code>. <code>ip addr</code> pokazuje adresy interfejsów, "
            "a <code>ip route</code> pokazuje trasy i bramę domyślną."
        ),
    },
    "quiz": {
        "title": "Quiz: podstawy adresacji IP",
        "description": "Sprawdź, czy rozumiesz adres IPv4, maskę, sieć, hosta i podstawowy routing.",
        "questions": [
            {
                "text": "Co oznacza zapis /24 przy adresie IPv4?",
                "answers": [
                    ("a", "Długość prefiksu sieci w zapisie CIDR", True),
                    ("b", "Numer portu usługi DNS", False),
                    ("c", "Liczbę aktywnych procesów", False),
                    ("d", "Wersję protokołu SSH", False),
                ],
            },
            {
                "text": "Który zakres IPv4 jest prywatny?",
                "answers": [
                    ("a", "192.168.0.0/16", True),
                    ("b", "8.8.8.0/24", False),
                    ("c", "1.1.1.0/24", False),
                    ("d", "93.184.216.0/24", False),
                ],
            },
            {
                "text": "Do czego służy brama domyślna?",
                "answers": [
                    ("a", "Do wysyłania ruchu poza lokalną sieć", True),
                    ("b", "Do przechowywania haseł użytkowników", False),
                    ("c", "Do formatowania dysku", False),
                    ("d", "Do uruchamiania zadań cron", False),
                ],
            },
            {
                "text": "Która komenda pokazuje adresy przypisane do interfejsów?",
                "answers": [
                    ("a", "ip addr", True),
                    ("b", "passwd", False),
                    ("c", "journalctl -u", False),
                    ("d", "dnf clean all", False),
                ],
            },
            {
                "text": "Co najczęściej pokazuje wpis zaczynający się od default w ip route?",
                "answers": [
                    ("a", "Trasę domyślną przez bramę", True),
                    ("b", "Domyślny edytor tekstu", False),
                    ("c", "Domyślną grupę użytkownika", False),
                    ("d", "Domyślny poziom SELinux", False),
                ],
            },
            {
                "text": "Dlaczego adres IP bez maski jest niepełną informacją?",
                "answers": [
                    ("a", "Bo nie wiadomo, jaka część adresu opisuje sieć", True),
                    ("b", "Bo nie da się wtedy uruchomić terminala", False),
                    ("c", "Bo każdy taki adres jest adresem MAC", False),
                    ("d", "Bo oznacza wyłączony firewall", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest adres IP?", "answer": "Identyfikatorem hosta w sieci IP."},
        {"question": "Jak zwykle zapisuje się adres IPv4?", "answer": "Jako cztery liczby oddzielone kropkami, na przykład 192.168.1.20."},
        {"question": "Co oznacza maska sieci?", "answer": "Określa, która część adresu należy do sieci, a która do hosta."},
        {"question": "Czym jest CIDR?", "answer": "Zapis prefiksu sieci, na przykład /24."},
        {"question": "Co oznacza 192.168.1.20/24?", "answer": "Adres hosta 192.168.1.20 w sieci opisanej prefiksem /24."},
        {"question": "Czym jest adres sieci?", "answer": "Adresem identyfikującym cały zakres hostów w danej sieci."},
        {"question": "Czym jest host w adresacji IP?", "answer": "Konkretnym urządzeniem lub interfejsem mającym adres w sieci."},
        {"question": "Czym jest brama domyślna?", "answer": "Routerem używanym do ruchu poza lokalną sieć."},
        {"question": "Co pokazuje ip addr?", "answer": "Interfejsy sieciowe i przypisane do nich adresy."},
        {"question": "Co pokazuje ip -4 addr?", "answer": "Tylko adresy IPv4 skonfigurowane w systemie."},
        {"question": "Co pokazuje ip route?", "answer": "Tablicę routingu systemu."},
        {"question": "Co oznacza default w ip route?", "answer": "Trasę domyślną używaną dla ruchu poza znanymi sieciami."},
        {"question": "Jaki zakres obejmuje 10.0.0.0/8?", "answer": "Prywatne adresy IPv4 zaczynające się od 10."},
        {"question": "Jaki zakres obejmuje 172.16.0.0/12?", "answer": "Prywatne adresy od 172.16.0.0 do 172.31.255.255."},
        {"question": "Jaki zakres obejmuje 192.168.0.0/16?", "answer": "Prywatne adresy zaczynające się od 192.168."},
        {"question": "Czy prywatny adres IPv4 jest zwykle publicznie routowany w Internecie?", "answer": "Nie, zwykle wychodzi do Internetu przez NAT."},
        {"question": "Czym jest NAT?", "answer": "Mechanizmem tłumaczenia adresów, często używanym między siecią prywatną a Internetem."},
        {"question": "Co robi hostname -I?", "answer": "Pokazuje adresy IP przypisane do hosta."},
        {"question": "Czy DNS i brama domyślna to to samo?", "answer": "Nie. DNS rozwiązuje nazwy, a brama kieruje ruch poza lokalną sieć."},
        {"question": "Czy nazwa interfejsu zawsze będzie eth0?", "answer": "Nie. Współczesne systemy często używają innych nazw, na przykład ens160."},
        {"question": "Co sprawdzić, gdy system nie ma dostępu do Internetu?", "answer": "Adres IP, trasę default, DNS i dostępność bramy."},
        {"question": "Czy adres 127.0.0.1 jest adresem sieci prywatnej LAN?", "answer": "Nie, to adres loopback lokalnego hosta."},
        {"question": "Do czego służy interfejs loopback?", "answer": "Do komunikacji systemu z samym sobą."},
        {"question": "Dlaczego warto znać prywatne zakresy IPv4?", "answer": "Pomagają rozpoznać adresy laboratoryjne, domowe i firmowe."},
        {"question": "Jaki jest pierwszy krok przy analizie konfiguracji IP?", "answer": "Sprawdzenie adresów interfejsów przez ip addr."},
    ],
}
