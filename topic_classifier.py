import re


# =========================================================
# DAFTAR TOPIK MASTER
# =========================================================

TOPIC_KEYWORDS = {

    "Jalan Karawang Timur": [
        "jalan karawang timur",
        "karawang timur",
        "interchange karawang timur",
        "akses karawang timur",
        "interchange kartim"
    ],

    "MBG": [
        "mbg",
        "makan bergizi gratis",
        "makan gratis",
        "makanan bergizi",
        "makan bergizi",
        "program makan gratis"
    ],

    "LKS": [
        "lks",
        "lembaga kesejahteraan sosial"
    ],

    "Sekolah": [
        "sekolah",
        "siswa",
        "murid",
        "guru",
        "pendidikan",
        "kelas",
        "sekolahan",
        "ruang kelas",
        "gedung sekolah",
        "atap sekolah",
        "sdn",
        "smpn",
        "sman",
        "smkn"
    ],

    "Jalan": [
        "jalan rusak",
        "jalan berlubang",
        "lubang jalan",
        "aspal rusak",
        "aspalnya bolong",
        "perbaikan jalan",
        "jalan hancur",
        "jalan jelek",
        "jalan amblas",
        "jalan retak",
        "infrastruktur jalan",
        "akses jalan",
        "jalan"
    ],

    "Banjir": [
        "banjir",
        "kebanjiran",
        "genangan",
        "tergenang",
        "air meluap",
        "meluap",
        "banjir lagi",
        "rawan banjir"
    ],

    "Bansos": [
        "bansos",
        "bantuan sosial",
        "pkh",
        "bpnt",
        "penerima bantuan",
        "bantuan pemerintah",
        "bantuan warga",
        "bansos cair"
    ],

    "Saluran": [
        "saluran",
        "drainase",
        "selokan",
        "gorong gorong",
        "gorong-gorong",
        "saluran mampet",
        "drainase mampet",
        "saluran air"
    ],

    "Air": [
        "air bersih",
        "pdam",
        "air mati",
        "susah air",
        "tidak ada air",
        "air keruh",
        "air kotor",
        "air warga"
    ],

    "Kekeringan": [
        "kekeringan",
        "krisis air",
        "kemarau panjang",
        "kekurangan air"
    ],

    "Aep Syaepuloh": [
        "aep syaepuloh",
        "pak aep",
        "bupati aep",
        "kang aep"
    ],

    "Bupati": [
        "bupati karawang",
        "pak bupati",
        "bupati",
        "kepala daerah"
    ],

    "Jembatan": [
        "jembatan rusak",
        "jembatan putus",
        "jembatan ambruk",
        "jembatan roboh",
        "jembatan"
    ],

    "Irigasi": [
        "irigasi",
        "pengairan sawah",
        "saluran sawah",
        "air sawah"
    ],

    "Kebijakan": [
        "kebijakan",
        "aturan pemerintah",
        "program pemerintah",
        "keputusan pemerintah",
        "peraturan",
        "pemkab karawang",
        "pemerintah daerah",
        "program daerah"
    ],

    "Pencurian": [
        "pencurian",
        "maling",
        "dicuri",
        "kemalingan",
        "curanmor",
        "motor hilang",
        "barang hilang"
    ],

    "Kriminalitas": [
        "kriminal",
        "kriminalitas",
        "kejahatan",
        "begal",
        "perampokan",
        "pembunuhan",
        "dibunuh",
        "bunuh",
        "penusukan",
        "ditusuk",
        "kekerasan",
        "penganiayaan",
        "tawuran",
        "kdrt",
        "kekerasan dalam rumah tangga"
    ],

    "Kerja": [
        "lowongan kerja",
        "lowongan",
        "loker",
        "pengangguran",
        "phk",
        "kesempatan kerja",
        "cari kerja",
        "butuh kerja",
        "lapangan kerja"
    ],

    "Calo": [
        "calo",
        "percaloan",
        "orang dalam",
        "titip orang",
        "uang masuk kerja",
        "bayar masuk kerja"
    ],

    "Transportasi": [
        "transportasi",
        "angkutan umum",
        "angkot",
        "bus",
        "kereta",
        "krl",
        "stasiun",
        "terminal",
        "ojek",
        "ojol",
        "macet",
        "kemacetan",
        "lalu lintas",
        "kendaraan dinas",
        "lakalantas",
        "laka lantas",
        "kecelakaan lalu lintas",
        "kecelakaan"
    ],

    "Mudik Gratis": [
        "mudik gratis",
        "program mudik gratis",
        "pendaftaran mudik gratis",
        "kuota mudik",
        "kuota mudik gratis",
        "armada mudik",
        "bus mudik",
        "tiket mudik",
        "pendaftaran mudik",
        "daftar mudik",
        "mudik lebaran"
    ],

    "Pelayanan Publik": [
        "pelayanan publik",
        "pelayanan warga",
        "kantor pelayanan",
        "administrasi",
        "dukcapil",
        "disdukcapil",
        "kecamatan",
        "kelurahan",
        "surat menyurat",
        "pelayanan pemerintah"
    ],

    "Sampah": [
        "sampah",
        "tumpukan sampah",
        "sampah menumpuk",
        "buang sampah",
        "tempat sampah"
    ],

    "Kesehatan": [
        "kesehatan",
        "rumah sakit",
        "puskesmas",
        "pasien",
        "dokter",
        "bpjs",
        "layanan kesehatan"
    ],

    "Harga": [
        "harga pangan",
        "harga sembako",
        "harga beras",
        "harga cabai",
        "harga minyak",
        "sembako mahal",
        "beras mahal"
    ],

    "Pertanian": [
        "petani",
        "pertanian",
        "sawah",
        "padi",
        "panen",
        "gagal panen",
        "pupuk"
    ],

    "Lingkungan": [
        "pencemaran",
        "polusi",
        "limbah pabrik",
        "pencemaran lingkungan",
        "pencemaran udara",
        "pencemaran air",
        "bau limbah"
    ]
}


# =========================================================
# DAFTAR TOPIK DASHBOARD
# =========================================================

TOPIC_LIST = list(
    TOPIC_KEYWORDS.keys()
) + [
    "Lainnya"
]


# =========================================================
# KEYWORD KONTEN KOMERSIAL / TIDAK RELEVAN
# =========================================================

COMMERCIAL_KEYWORDS = [
    "order sekarang",
    "pesan sekarang",
    "wa sekarang",
    "hubungi kami",
    "promo",
    "diskon",
    "checkout",
    "jual",
    "jualan",
    "ready stock",
    "harga kamar",
    "penginapan",
    "villa",
    "homestay",
    "hotel",
    "kursus jahit",
    "kursus menjahit",
    "daftar kursus",
    "es krim",
    "ice cream",
    "kuliner",
    "menu makanan",
    "open order"
]


# =========================================================
# KEYWORD ISU PUBLIK
# =========================================================

PUBLIC_ISSUE_KEYWORDS = [

    # Pemerintahan
    "bupati",
    "wakil bupati",
    "wabup",
    "pemkab",
    "pemerintah daerah",
    "dinas",
    "satpol pp",

    # Infrastruktur
    "jalan rusak",
    "jalan berlubang",
    "perbaikan jalan",
    "jalan amblas",
    "jembatan rusak",
    "jembatan putus",
    "drainase",
    "irigasi",

    # Banjir / air
    "banjir",
    "kebanjiran",
    "genangan",
    "kekeringan",
    "krisis air",
    "pdam",

    # Sosial
    "bansos",
    "bantuan sosial",
    "mbg",
    "makan bergizi gratis",

    # Pendidikan
    "sekolah rusak",
    "atap sekolah",
    "ruang kelas rusak",

    # Kriminalitas
    "pembunuhan",
    "dibunuh",
    "kdrt",
    "begal",
    "pencurian",
    "curanmor",
    "penganiayaan",
    "tawuran",
    "kriminal",

    # Transportasi
    "kecelakaan",
    "kecelakaan lalu lintas",
    "lakalantas",
    "laka lantas",
    "transportasi",
    "kereta",
    "krl",
    "angkutan umum",
    "kemacetan",

    # Mudik Gratis
    "mudik gratis",
    "program mudik gratis",
    "pendaftaran mudik gratis",
    "kuota mudik",
    "armada mudik",

    # Pelayanan publik
    "pelayanan publik",
    "dukcapil",
    "disdukcapil",

    # Lingkungan
    "sampah menumpuk",
    "pencemaran",
    "limbah pabrik",

    # Kesehatan
    "puskesmas",
    "rumah sakit",
    "bpjs",

    # Ketenagakerjaan
    "lowongan kerja",
    "pengangguran",
    "phk",
    "lapangan kerja",
    "calo kerja",

    # Pertanian
    "petani",
    "irigasi",
    "gagal panen"
]


# =========================================================
# NORMALISASI TEXT
# =========================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    text = re.sub(
        r"[@#]",
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# CEK KEYWORD
# =========================================================

def keyword_match(
    text,
    keyword
):

    keyword = normalize_text(
        keyword
    )

    if not keyword:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(keyword)
        + r"(?!\w)"
    )

    return (
        re.search(
            pattern,
            text
        )
        is not None
    )


# =========================================================
# HITUNG SCORE TOPIK
# =========================================================

def get_topic_scores(text):

    text = normalize_text(
        text
    )

    scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            keyword_normalized = normalize_text(
                keyword
            )

            if keyword_match(
                text,
                keyword_normalized
            ):

                word_count = len(
                    keyword_normalized.split()
                )

                if word_count >= 3:
                    score += 6

                elif word_count == 2:
                    score += 4

                else:
                    score += 2

        scores[topic] = score

    return scores


# =========================================================
# CLASSIFY TOPIC
# =========================================================

def classify_topic(text):

    if not text:
        return "Lainnya"

    text = normalize_text(
        text
    )

    if not text:
        return "Lainnya"

    scores = get_topic_scores(
        text
    )

    if not scores:
        return "Lainnya"

    best_topic = max(
        scores,
        key=scores.get
    )

    best_score = scores[
        best_topic
    ]

    if best_score <= 0:
        return "Lainnya"

    return best_topic


# =========================================================
# HITUNG SINYAL KEYWORD
# =========================================================

def count_keyword_matches(
    text,
    keywords
):

    total = 0

    for keyword in keywords:

        if keyword_match(
            text,
            keyword
        ):
            total += 1

    return total


# =========================================================
# CEK POST RELEVAN ATAU TIDAK
# =========================================================

def is_relevant_post(text):

    if not text:
        return False

    normalized = normalize_text(
        text
    )

    if not normalized:
        return False

    # -----------------------------------------------------
    # 1. CEK KONTEN KOMERSIAL
    # -----------------------------------------------------

    commercial_score = count_keyword_matches(
        normalized,
        COMMERCIAL_KEYWORDS
    )

    # -----------------------------------------------------
    # 2. CEK SINYAL ISU PUBLIK
    # -----------------------------------------------------

    public_score = count_keyword_matches(
        normalized,
        PUBLIC_ISSUE_KEYWORDS
    )

    # -----------------------------------------------------
    # 3. TENTUKAN TOPIK
    # -----------------------------------------------------

    detected_topic = classify_topic(
        normalized
    )

    # -----------------------------------------------------
    # 4. KONTEN KOMERSIAL
    #
    # Jika jelas jualan/promosi dan tidak mempunyai
    # sinyal isu publik, jangan dimonitor.
    # -----------------------------------------------------

    if (
        commercial_score > 0
        and public_score == 0
    ):
        return False

    # -----------------------------------------------------
    # 5. ADA SINYAL ISU PUBLIK
    # -----------------------------------------------------

    if public_score > 0:
        return True

    # -----------------------------------------------------
    # 6. TOPIK YANG CUKUP SPESIFIK
    #
    # Hanya topik tertentu yang boleh membuat post
    # relevan tanpa PUBLIC_ISSUE_KEYWORDS.
    #
    # Jangan masukkan Harga karena kata-kata komersial
    # dapat menyebabkan iklan/jualan ikut masuk.
    # -----------------------------------------------------

    strong_relevant_topics = [

        "Jalan Karawang Timur",

        "MBG",

        "LKS",

        "Banjir",

        "Bansos",

        "Kekeringan",

        "Aep Syaepuloh",

        "Bupati",

        "Jembatan",

        "Irigasi",

        "Kebijakan",

        "Pencurian",

        "Kriminalitas",

        "Mudik Gratis",

        "Calo",

        "Sampah",

        "Kesehatan",

        "Pertanian",

        "Lingkungan"
    ]

    if detected_topic in strong_relevant_topics:
        return True

    # -----------------------------------------------------
    # 7. TOPIK YANG BUTUH KONTEKS LEBIH KUAT
    #
    # Topik seperti Jalan, Sekolah, Kerja, Transportasi,
    # Air, dll terlalu umum jika berdiri sendiri.
    # -----------------------------------------------------

    context_topics = [

        "Sekolah",
        "Jalan",
        "Saluran",
        "Air",
        "Kerja",
        "Transportasi",
        "Pelayanan Publik"
    ]

    if detected_topic in context_topics:

        context_keywords = [

            "rusak",
            "roboh",
            "ambruk",
            "berlubang",
            "bolong",
            "mati",
            "mampet",
            "susah",
            "krisis",
            "keluhan",
            "dikeluhkan",
            "perbaikan",
            "pemerintah",
            "pemkab",
            "bupati",
            "dinas",
            "warga",
            "masyarakat",
            "kecelakaan",
            "macet",
            "pelayanan",
            "program",
            "bantuan",
            "belum diperbaiki",
            "tidak diperbaiki"
        ]

        context_score = count_keyword_matches(
            normalized,
            context_keywords
        )

        if context_score > 0:
            return True

    # -----------------------------------------------------
    # 8. SELAIN ITU TIDAK RELEVAN
    # -----------------------------------------------------

    return False


# =========================================================
# CLASSIFY COMMENT DENGAN KONTEKS POST
# =========================================================

def classify_comment_with_context(
    comment_text,
    post_caption="",
    post_topic="Lainnya"
):

    # =============================================
    # 1. COBA DARI TEKS KOMENTAR
    # =============================================

    comment_topic = classify_topic(
        comment_text
    )

    if comment_topic != "Lainnya":
        return comment_topic

    # =============================================
    # 2. JIKA KOMENTAR TIDAK JELAS,
    #    PAKAI TOPIK POST
    # =============================================

    if (
        post_topic
        and post_topic != "Lainnya"
    ):
        return post_topic

    # =============================================
    # 3. COBA DARI CAPTION POST
    # =============================================

    caption_topic = classify_topic(
        post_caption
    )

    if caption_topic != "Lainnya":
        return caption_topic

    return "Lainnya"


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    samples = [

        "Pak aspalnya bolong besar di sini",

        "MBG di sekolah kami belum dapat",

        "Selokan depan rumah mampet terus",

        "Bansos kapan cair ya",

        "Banyak lowongan tapi banyak calo",

        "Setiap hujan daerah sini tergenang",

        "Atap SDN ini hampir roboh",

        "Air PDAM sudah dua hari mati",

        "Cari kerja di Karawang susah sekali",

        "Pelayanan dukcapil lama banget",

        "Sampah menumpuk sudah beberapa hari",

        "Pak Bupati tolong diperhatikan",

        "kdrt kejam tapi bunuh bukan solusi",

        "Kecelakaan lalu lintas terjadi di Galuh Mas",

        "Pendaftaran program Mudik Gratis Karawang dibuka hari ini"
    ]

    print("=" * 60)
    print("TEST CLASSIFIER")
    print("=" * 60)

    for text in samples:

        print(
            text,
            "->",
            classify_topic(text)
        )


    print()
    print("=" * 60)
    print("TEST RELEVANSI POST")
    print("=" * 60)

    relevant_samples = [

        "Jalan rusak di Karawang belum diperbaiki",

        "Wabup Karawang naik kereta menuju kantor",

        "Remaja melakukan pembunuhan setelah diduga mengalami KDRT",

        "Villa Karawang murah tersedia weekend ini",

        "Bikin daster 3 jam daftar kursus jahit Karawang",

        "Bansos warga Karawang belum cair",

        "Program Mudik Gratis Karawang menambah armada bus"
    ]


    for text in relevant_samples:

        print(
            text,
            "->",
            is_relevant_post(text)
        )


    print()
    print("=" * 60)
    print("TEST KOMENTAR + KONTEKS")
    print("=" * 60)

    print(
        classify_comment_with_context(
            "tolong segera diperbaiki pak",
            "Jalan rusak di Karawang",
            "Jalan"
        )
    )

    print(
        classify_comment_with_context(
            "semoga konsisten pak",
            "Wabup Karawang naik kereta",
            "Transportasi"
        )
    )
