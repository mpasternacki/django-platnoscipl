# -*- coding: utf-8 -*-

# error codes
ERR_NO_POS_ID = 100
ERR_NO_SESSION_ID = 101
ERR_NO_TS = 102
ERR_NO_SIG = 103
ERR_NO_DESC = 104
ERR_NO_CLIENT_IP = 105
ERR_NO_FIRST_NAME = 106
ERR_NO_LAST_NAME = 107
ERR_NO_STREET = 108
ERR_NO_CITY = 109
ERR_NO_POST_CODE = 110
ERR_NO_AMOUNT = 111
ERR_INVALID_BANK_ACCOUNT_NUMBER = 112
ERR_NO_EMAIL = 113
ERR_NO_PHONE = 114
ERR_TEMPORARY_OTHER = 200
ERR_TEMPORARY_DB_OTHER = 201
ERR_LOCKED_POS = 202
ERR_INVALID_PAY_TYPE = 203
ERR_LOCKED_PAY_TYPE = 204
ERR_AMOUT_TOO_SMALL = 205
ERR_AMOUNT_TOO_BIG = 206
ERR_TOTAL_AMOUNT_EXCEEDED = 207
ERR_EXPRESS_PAYMENT_INACTIVE = 208
ERR_INVALID_POS_ID = 209
ERR_INVALID_TRANSACTION = 500
ERR_UNAUTHORISED = 501
ERR_TRANSACTION_ALREADY_OPEN = 502
ERR_TRANSACTION_ALREADY_AUTHORISED = 503
ERR_TRANSACTION_CANCELLED = 504
ERR_TRANSACTION_ALREADY_SENT_TO_ACCEPT = 505
ERR_TRANSACTION_ALREADY_CONFIRMED = 506
ERR_RETURNING_PAYMENT = 507
ERR_INVALID_STATUS = 599
ERR_CRITICAL_OTHER = 999

ERR_MESSAGES = {
    ERR_NO_POS_ID: u"brak lub błędna wartość parametru pos id",
    ERR_NO_SESSION_ID: u"brak parametru session id",
    ERR_NO_TS: u"brak parametru ts",
    ERR_NO_SIG: u"brak lub błędna wartość parametru sig",
    ERR_NO_DESC: u"brak parametru desc",
    ERR_NO_CLIENT_IP: u"brak parametru client ip",
    ERR_NO_FIRST_NAME: u"brak parametru first name",
    ERR_NO_LAST_NAME: u"brak parametru last name",
    ERR_NO_STREET: u"brak parametru street",
    ERR_NO_CITY: u"brak parametru city",
    ERR_NO_POST_CODE: u"brak parametru post code",
    ERR_NO_AMOUNT: u"brak parametru amount",
    ERR_INVALID_BANK_ACCOUNT_NUMBER: u"błędny numer konta bankowego",
    ERR_NO_EMAIL: u"brak parametru email",
    ERR_NO_PHONE: u"brak numeru telefonu",
    ERR_TEMPORARY_OTHER: u"inny chwilowy błąd",
    ERR_TEMPORARY_DB_OTHER: u"inny chwilowy błąd bazy danych",
    ERR_LOCKED_POS: u"Pos o podanym identyfikatorze jest zablokowany",
    ERR_INVALID_PAY_TYPE: u"niedozwolona wartość pay type dla danego pos id",
    ERR_LOCKED_PAY_TYPE: u"podana metoda płatności (wartość pay type) jest"
    u" chwilowo zablokowana dla danego pos id, np. przerwa konserwacyjna"
    u" bramki płatniczej",
    ERR_AMOUT_TOO_SMALL: u"kwota transakcji mniejsza od wartości minimalnej",
    ERR_AMOUNT_TOO_BIG: u"kwota transakcji większa od wartości maksymalnej",
    ERR_TOTAL_AMOUNT_EXCEEDED: u"przekroczona wartość wszystkich transakcji"
    u" dla jednego klienta w ostatnim przedziale czasowym",
    ERR_EXPRESS_PAYMENT_INACTIVE: u"Pos działa w wariancie ExpressPayment"
    u" lecz nie nastąpiła aktywacja tego wariantu współpracy (czekamy"
    u" na zgodę działu obsługi klienta)",
    ERR_INVALID_POS_ID: u"błędny numer pos id lub pos auth key",
    ERR_INVALID_TRANSACTION: u"transakcja nie istnieje",
    ERR_UNAUTHORISED: u"brak autoryzacji dla danej transakcji",
    ERR_TRANSACTION_ALREADY_OPEN: u"transakcja rozpoczęta wcześniej",
    ERR_TRANSACTION_ALREADY_AUTHORISED: u"autoryzacja do transakcji"
    u" była już przeprowadzana",
    ERR_TRANSACTION_CANCELLED: u"transakcja anulowana wcześniej",
    ERR_TRANSACTION_ALREADY_SENT_TO_ACCEPT: u"transakcja przekazana"
    u" do odbioru wcześniej",
    ERR_TRANSACTION_ALREADY_CONFIRMED: u"transakcja już odebrana",
    ERR_RETURNING_PAYMENT: u"błąd podczas zwrotu środków do klienta",
    ERR_INVALID_STATUS: u"błędny stan transakcji, np. nie można uznać"
    u" transakcji kilka razy lub inny, prosimy o kontakt",
    ERR_CRITICAL_OTHER: u"inny błąd krytyczny - prosimy o kontakt",
}

# transaction states
STATUS_NEW = 1
STATUS_CANCELLED = 2
STATUS_REJECTED = 3
STATUS_OPEN = 4
STATUS_WAITING_FOR_ACCEPT = 5
STATUS_PAYMENT_REJECTED = 7
STATUS_CONFIRMED = 99
STATUS_ERROR = 888

STATUS_NAMES = {
    STATUS_NEW: u"nowa",
    STATUS_CANCELLED: u"anulowana",
    STATUS_REJECTED: u"odrzucona",
    STATUS_OPEN: u"rozpoczęta",
    STATUS_WAITING_FOR_ACCEPT: u"oczekuje na odbiór",
    STATUS_PAYMENT_REJECTED: u"płatność odrzucona",
    STATUS_CONFIRMED: u"płatność odebrana - zakończona",
    STATUS_ERROR: u"błędny status - prosimy o kontakt",
    -1: u'brak',
    }

PAY_TYPES = {
    'b': u'Przelew bankowy',
    'c': u'karta kredytowa',
    'd': u'Płać z Nordea',
    'g': u'Płać z ING',
    'h': u'Płać z BPH',
    'i': u'Płacę z Inteligo',
    'l': u'LUKAS e-przelew',
    'm': u'mTransfer - mBank',
    'n': u'MultiTransfer - MultiBank',
    'o': u'Pekao24Przelew - Bank Pekao',
    'p': u'Płać z iPKO',
    't': u'Płatność testowa',
    'w': u'BZWBK - Przelew24',
    'wc': u'Przelew z Citibank',
    'wd': u'Przelew z Deutsche Bank',
    'wg': u'Przelew z BGŻ',
    'wk': u'Przelew z Kredyt Bank',
    'wm': u'Przelew z Millennium',
    'wp': u'Przelew z Polbank',
    'wr': u'Przelew z Raiffeisen Bank',
    None: u'brak',
    }

OK_URL_QUERY_STRING = 'transaction_id=%transId%' \
                      '&pos_id=%posId%' \
                      '&pay_type=%payType%' \
                      '&session_id=%sessionId%' \
                      '&amount=%amountCS%' \
                      '&amount_with_dot=%amountPS%' \
                      '&order_id=%orderId%'

FAIL_URL_QUERY_STRING = OK_URL_QUERY_STRING + '&error=%error%'
