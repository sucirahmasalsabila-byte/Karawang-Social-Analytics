import os
import re
import base64
import bcrypt

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from database import get_connection, create_tables
from topic_classifier import (
    TOPIC_LIST,
    classify_topic,
    classify_comment_with_context
)

from sentiment import classify_sentiment

import hashlib
import secrets
import time

from datetime import datetime, timedelta

from streamlit_cookies_controller import CookieController

import streamlit.components.v1 as components


# =========================================================
# SETUP
# =========================================================


load_dotenv(override=True)


def bootstrap_admin_from_secrets():
    """Pulihkan akun admin melalui Streamlit Secrets."""
    try:
        username = st.secrets["APP_USERNAME"]
        password = st.secrets["APP_PASSWORD"]
    except Exception:
        # Secrets belum tersedia; jangan ubah akun.
        return

    if not username or not password:
        return

    reset_enabled = str(
        st.secrets.get("ADMIN_RESET_PASSWORD", "false")
    ).lower() == "true"

    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username = ? LIMIT 1",
            (username,)
        )
        user = cursor.fetchone()

        if user is None:
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute(
                """
                INSERT INTO users
                    (username, password, role, created_at)
                VALUES (?, ?, 'admin', datetime('now'))
                """,
                (username, password_hash)
            )
            conn.commit()

        elif reset_enabled:
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (password_hash, username)
            )
            conn.commit()

    finally:
        conn.close()


create_tables()
bootstrap_admin_from_secrets()


st.set_page_config(
    page_title="Karawang Social Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LOAD CSS
# =========================================================

def load_css(file_name):

    with open(
        file_name,
        "r",
        encoding="utf-8"
    ) as file:

        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )


load_css("style.css")


# =========================================================
# LOAD LOGO
# =========================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def get_image_base64(image_path):
    full_path = BASE_DIR / image_path

    try:
        with open(full_path, "rb") as image_file:
            encoded = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        return encoded

    except FileNotFoundError:
        print(f"FILE LOGO TIDAK DITEMUKAN: {full_path}")
        return ""

logo_diskominfo = get_image_base64(
    "assets/logo_diskominfo.png"
)

logo_karawang = get_image_base64(
    "assets/logo_karawang.png"
)

logo_instagram = get_image_base64(
    "assets/logo_instagram.png"
)

logo_tiktok = get_image_base64(
    "assets/logo_tiktok.png"
)

background_login = get_image_base64(
    "assets/kantor_karawang.png"
)

# =========================================================
# DEBUG LOGO - CEK DI STREAMLIT CLOUD
# =========================================================

st.write("Status logo Instagram:", {
    "terbaca": bool(logo_instagram),
    "panjang_data": len(logo_instagram)
})

st.write("Status logo TikTok:", {
    "terbaca": bool(logo_tiktok),
    "panjang_data": len(logo_tiktok)
})

# =========================================================
# AUTH LOGIN DATABASE
# =========================================================

COOKIE_NAME = "karawang_auth"
SESSION_DAYS = 7
IDLE_MINUTES = 10

cookie_controller = CookieController()


def get_user_by_username(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            username,
            password,
            role
        FROM users
        WHERE username = ?
        LIMIT 1
        """,
        (
            username,
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user


def verify_login(
    username,
    password
):

    user = get_user_by_username(
        username
    )

    if user is None:
        return None

    user_id = user[0]
    username_db = user[1]
    password_hash = user[2]
    role = user[3]

    try:

        cocok = bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    except Exception:

        return None

    if not cocok:
        return None

    return {
        "id": user_id,
        "username": username_db,
        "role": role
    }


# =========================================================
# BUAT SESSION LOGIN
# =========================================================

def create_login_session(user_id):

    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    sekarang = datetime.now()

    expires_at = (
        sekarang
        + timedelta(days=SESSION_DAYS)
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO login_sessions (
            user_id,
            token_hash,
            created_at,
            last_activity,
            expires_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            token_hash,
            sekarang.isoformat(),
            sekarang.isoformat(),
            expires_at.isoformat()
        )
    )

    conn.commit()
    conn.close()

    # Simpan token sementara
    st.session_state["pending_cookie_token"] = token
    st.session_state["pending_cookie_expiry"] = (
        expires_at.isoformat()
    )

    return True


# =========================================================
# AMBIL TOKEN COOKIE
# =========================================================

def get_cookie_token():

    try:

        cookie_value = cookie_controller.get(
            COOKIE_NAME
        )

    except TypeError:

        # CookieController belum siap dibaca
        return None

    except Exception:

        return None

    if not cookie_value:
        return None

    if isinstance(
        cookie_value,
        dict
    ):

        return cookie_value.get(
            "value"
        )

    return str(
        cookie_value
    )


# =========================================================
# HAPUS SESSION LOGIN
# =========================================================

def delete_login_session():

    token = get_cookie_token()

    if token:

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM login_sessions
            WHERE token_hash = ?
            """,
            (
                token_hash,
            )
        )

        conn.commit()
        conn.close()

    cookie_controller.remove(
        COOKIE_NAME
    )


# =========================================================
# CEK COOKIE SAAT REFRESH
# =========================================================

def check_login_cookie():

    token = get_cookie_token()

    if not token:
        return None

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            users.id,
            users.username,
            users.role,
            login_sessions.expires_at

        FROM login_sessions

        INNER JOIN users
            ON users.id =
               login_sessions.user_id

        WHERE login_sessions.token_hash = ?

        LIMIT 1
        """,
        (
            token_hash,
        )
    )

    session = cursor.fetchone()

    conn.close()

    if session is None:
        return None

    try:
        expires_at = datetime.fromisoformat(
        session[3]
        )   

    except Exception:

        return None

    if datetime.now() >= expires_at:

        delete_login_session()

        return None

    return {
        "id": session[0],
        "username": session[1],
        "role": session[2]
    }

# =========================================================
# LOGIN
# =========================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

if "role" not in st.session_state:
    st.session_state["role"] = ""

if "cookie_retry" not in st.session_state:
    st.session_state["cookie_retry"] = 0

# =========================================================
# SIMPAN COOKIE SETELAH LOGIN
# =========================================================

if "pending_cookie_token" in st.session_state:

    try:

        cookie_controller.set(
            COOKIE_NAME,
            {
                "value": st.session_state[
                    "pending_cookie_token"
                ],
                "expiry_date": st.session_state[
                    "pending_cookie_expiry"
                ]
            }
        )

        del st.session_state[
            "pending_cookie_token"
        ]

        del st.session_state[
            "pending_cookie_expiry"
        ]

        st.session_state[
            "cookie_save_retry"
        ] = 0

    except TypeError:

        retry = st.session_state.get(
            "cookie_save_retry",
            0
        )

        if retry < 5:

            st.session_state[
                "cookie_save_retry"
            ] = retry + 1

            time.sleep(0.3)

            st.rerun()

    except Exception:

        pass

# =========================================================
# RESTORE LOGIN SETELAH REFRESH / F5
# =========================================================

if not st.session_state["authenticated"]:

    saved_user = check_login_cookie()

    if saved_user:

        st.session_state["authenticated"] = True
        st.session_state["username"] = saved_user["username"]
        st.session_state["role"] = saved_user["role"]

        st.session_state["cookie_retry"] = 0

    elif st.session_state["cookie_retry"] < 3:

        st.session_state["cookie_retry"] += 1

        time.sleep(0.25)

        st.rerun()


# =========================================================
# TAMPILKAN LOGIN JIKA BENAR-BENAR BELUM LOGIN
# =========================================================

if not st.session_state["authenticated"]:
    # =====================================================
    # BACKGROUND LOGIN
    # =====================================================

    background_login = get_image_base64(
        "assets/kantor_karawang.png"
    )

    # =====================================================
    # CSS KHUSUS HALAMAN LOGIN
    # =====================================================

    st.markdown(
        f"""
<style>

/* =========================================================
   HALAMAN LOGIN
   ========================================================= */

.block-container {{
    max-width: 1250px !important;
    padding-top: 3rem !important;
    padding-bottom: 3rem !important;
}}


/* =========================================================
   CONTAINER LOGIN
   ========================================================= */

[data-testid="stHorizontalBlock"]:has(.login-left-marker) {{
    gap: 0 !important;

    min-height: 650px;

    border-radius: 24px;

    overflow: hidden;

    background: #071b35;

    box-shadow:
        0 20px 60px
        rgba(0, 0, 0, 0.22);
}}


/* =========================================================
   KOLOM KIRI
   ========================================================= */

[data-testid="stColumn"]:has(.login-left-marker) {{

    min-height: 650px;

    padding:
        42px
        48px
        42px
        48px;

    position: relative;

    background-image:
        linear-gradient(
            90deg,
            rgba(8, 42, 82, 0.91),
            rgba(5, 31, 65, 0.86)
        ),
        url("data:image/png;base64,{background_login}");

    background-size: cover;

    background-position: center;

    display: flex;

    flex-direction: column;

    justify-content: center;
}}


/* Overlay supaya foto tidak terlalu terang */

[data-testid="stColumn"]:has(.login-left-marker)::before {{

    content: "";

    position: absolute;

    inset: 0;

    background:
        linear-gradient(
            180deg,
            rgba(4, 30, 66, 0.05),
            rgba(3, 20, 46, 0.30)
        );

    pointer-events: none;
}}


/* =========================================================
   DEKORASI KIRI BAWAH
   ========================================================= */

[data-testid="stColumn"]:has(.login-left-marker)::after {{

    content: "";

    position: absolute;

    width: 430px;

    height: 430px;

    left: -280px;

    bottom: -280px;

    border-radius: 50%;

    border:
        70px solid
        rgba(35, 133, 235, 0.13);

    pointer-events: none;
}}


/* =========================================================
   KOLOM KANAN
   ========================================================= */

[data-testid="stColumn"]:has(.login-right-marker) {{

    min-height: 650px;

    padding:
        50px
        55px;

    background:
        linear-gradient(
            145deg,
            #071b35,
            #041326
        );

    display: flex;

    flex-direction: column;

    justify-content: center;
}}


/* =========================================================
   MARKER DISEMBUNYIKAN
   ========================================================= */

.login-left-marker,
.login-right-marker {{
    display: none;
}}


/* =========================================================
   LOGO
   ========================================================= */

.login-logo-area {{
    position: relative;
    z-index: 2;

    display: flex;
    align-items: center;
    justify-content: center;

    width: 100%;

    gap: 24px;

    margin-bottom: 55px;
}}

.login-logo-box {{
    width: 170px;
    height: 110px;

    display: flex;
    align-items: center;
    justify-content: center;
}}


.login-logo-diskominfo {{
    width: 170px !important;
    height: 105px !important;

    object-fit: contain !important;
    object-position: center !important;

    transform: scale(1.75) !important;
    transform-origin: center center !important;

    flex-shrink: 0 !important;
}}


.login-logo-line {{
    width: 1px;
    height: 80px;

    margin: 0 !important;

    background: rgba(255, 255, 255, 0.35);

    flex-shrink: 0 !important;
}}


.login-logo-karawang {{
    width: 95px !important;
    height: 95px !important;

    object-fit: contain !important;

    transform: none !important;
}}


/* =========================================================
   JUDUL
   ========================================================= */

.login-title-new {{

    position: relative;

    z-index: 2;
}}


.login-title-new h1 {{

    margin: 0 !important;

    padding: 0 !important;

    font-size: 48px !important;

    line-height: 1.07 !important;

    letter-spacing: -1px;

    font-weight: 750;

    color: #ffffff !important;
}}


.login-title-new h3 {{

    margin:
        22px
        0
        0
        0 !important;

    font-size: 19px !important;

    line-height: 1.45;

    font-weight: 550;

    color:
        rgba(
            255,
            255,
            255,
            0.88
        ) !important;
}}


/* Garis biru */

.login-title-line {{

    width: 55px;

    height: 5px;

    margin-top: 19px;

    border-radius: 20px;

    background:
        linear-gradient(
            90deg,
            #139aff,
            #3950ff
        );
}}


/* Deskripsi */

.login-description-new {{

    max-width: 430px;

    margin-top: 22px;

    font-size: 14px;

    line-height: 1.7;

    color:
        rgba(
            255,
            255,
            255,
            0.68
        ) !important;
}}


/* =========================================================
   FITUR
   ========================================================= */

.login-features-new {{

    position: relative;

    z-index: 2;

    display: flex;

    flex-wrap: wrap;

    gap: 9px;

    margin-top: 27px;
}}


.login-feature-new {{

    padding:
        9px
        13px;

    border-radius: 9px;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.13
        );

    background:
        rgba(
            255,
            255,
            255,
            0.08
        );

    color:
        rgba(
            255,
            255,
            255,
            0.82
        ) !important;

    font-size: 12px;
}}


/* =========================================================
   FORM KANAN
   ========================================================= */

.login-form-header {{

    margin-bottom: 27px;
}}


.login-form-header h2 {{

    margin: 0 !important;

    font-size: 29px !important;

    font-weight: 700;

    color: #ffffff !important;
}}


.login-form-header p {{

    margin:
        9px
        0
        0
        0 !important;

    font-size: 13px;

    line-height: 1.5;

    color:
        rgba(
            255,
            255,
            255,
            0.55
        ) !important;
}}


/* =========================================================
   LABEL INPUT
   ========================================================= */

[data-testid="stColumn"]:has(.login-right-marker)
label {{

    color:
        rgba(
            255,
            255,
            255,
            0.88
        ) !important;

    font-weight: 500;
}}


/* =========================================================
   INPUT USERNAME / PASSWORD
   ========================================================= */

[data-testid="stColumn"]:has(.login-right-marker)
[data-baseweb="input"] > div {{

    min-height: 48px;

    background:
        rgba(
            255,
            255,
            255,
            0.08
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.09
        ) !important;

    border-radius: 9px !important;
}}


[data-testid="stColumn"]:has(.login-right-marker)
[data-baseweb="input"] input {{

    color: #ffffff !important;

    background: transparent !important;
}}


[data-testid="stColumn"]:has(.login-right-marker)
[data-baseweb="input"] input::placeholder {{

    color:
        rgba(
            255,
            255,
            255,
            0.35
        ) !important;
}}


/* =========================================================
   CHECKBOX
   ========================================================= */

[data-testid="stColumn"]:has(.login-right-marker)
[data-testid="stCheckbox"] {{

    margin-top: 4px;

    margin-bottom: 13px;
}}


[data-testid="stColumn"]:has(.login-right-marker)
[data-testid="stCheckbox"] p {{

    color:
        rgba(
            255,
            255,
            255,
            0.75
        ) !important;
}}


/* =========================================================
   TOMBOL LOGIN
   ========================================================= */

[data-testid="stColumn"]:has(.login-right-marker)
.stButton > button {{

    width: 100%;

    min-height: 49px;

    margin-top: 7px;

    border: none !important;

    border-radius: 9px !important;

    background:
        linear-gradient(
            90deg,
            #1598ff,
            #3e3df2
        ) !important;

    color: #ffffff !important;

    font-weight: 650 !important;

    box-shadow:
        0 8px 22px
        rgba(
            29,
            108,
            255,
            0.27
        );

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease;
}}


[data-testid="stColumn"]:has(.login-right-marker)
.stButton > button:hover {{

    transform:
        translateY(-1px);

    color:
        #ffffff !important;

    box-shadow:
        0 11px 27px
        rgba(
            29,
            108,
            255,
            0.38
        );
}}


/* =========================================================
   INFO ADMIN
   ========================================================= */

.login-security-new {{

    margin-top: 28px;

    padding-top: 20px;

    border-top:
        1px solid
        rgba(
            255,
            255,
            255,
            0.10
        );

    text-align: center;

    font-size: 12px;

    line-height: 1.5;

    color:
        rgba(
            255,
            255,
            255,
            0.47
        ) !important;
}}


/* =========================================================
   ERROR LOGIN
   ========================================================= */

[data-testid="stColumn"]:has(.login-right-marker)
[data-testid="stAlert"] {{

    margin-top: 12px;
}}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 800px) {{

    [data-testid="stHorizontalBlock"]:has(.login-left-marker) {{

        display: block !important;

        min-height: auto;
    }}


    [data-testid="stColumn"]:has(.login-left-marker) {{

        min-height: 500px;

        padding:
            35px
            30px;
    }}


    [data-testid="stColumn"]:has(.login-right-marker) {{

        min-height: auto;

        padding:
            40px
            30px;
    }}


    .login-logo-area {{

        margin-bottom: 35px;
    }}


    .login-logo-diskominfo {{

    width: 80px !important;

    height: 80px !important;

    min-width: 80px !important;

    max-width: 80px !important;

    object-fit: contain !important;

    transform: scale(1.55) !important;

    transform-origin: center center !important;
}}


    .login-logo-karawang {{

        width: 58px !important;

        height: 58px !important;
    }}


    .login-title-new h1 {{

        font-size: 39px !important;
    }}

}}

</style>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # DUA KOLOM LOGIN
    # =====================================================

    login_left, login_right = st.columns(
        [1.15, 0.85],
        gap=None
    )


        # =====================================================
    # BAGIAN KIRI
    # =====================================================

    with login_left:

        st.markdown(
            '<div class="login-left-marker"></div>',
            unsafe_allow_html=True
        )

        logo_html = (
    f'<div class="login-logo-area">'
        f'<div class="login-logo-box">'
            f'<img src="data:image/png;base64,{logo_diskominfo}" class="login-logo-diskominfo">'
        f'</div>'

        f'<div class="login-logo-line"></div>'

        f'<div class="login-logo-box">'
            f'<img src="data:image/png;base64,{logo_karawang}" class="login-logo-karawang">'
        f'</div>'
    f'</div>'
)

        st.markdown(
            logo_html,
            unsafe_allow_html=True
        )

        title_html = (
            '<div class="login-title-new">'
            '<h1>Karawang<br>Social Analytics</h1>'
            '<h3>Analisis Sentimen Publik<br>Kabupaten Karawang</h3>'
            '<div class="login-title-line"></div>'
            '</div>'
            '<div class="login-description-new">'
            'Memahami opini publik melalui analisis percakapan media sosial '
            'untuk membantu monitoring informasi Kabupaten Karawang.'
            '</div>'
        )

        st.markdown(
            title_html,
            unsafe_allow_html=True
        )

        feature_html = (
            '<div class="login-features-new">'
            '<div class="login-feature-new">◉ Analisis Sentimen</div>'
            '<div class="login-feature-new"># Monitoring Topik</div>'
            '<div class="login-feature-new">↗ Tren Percakapan</div>'
            '</div>'
        )

        st.markdown(
            feature_html,
            unsafe_allow_html=True
        )

    # =====================================================
    # BAGIAN KANAN
    # =====================================================

    with login_right:

        st.markdown(
            '<div class="login-right-marker"></div>',
            unsafe_allow_html=True
        )

        login_header_html = (
            '<div class="login-form-header">'
            '<h2>Masuk ke Dashboard</h2>'
            '<p>Silakan masukkan akun administrator untuk mengakses dashboard.</p>'
            '</div>'
        )

        st.markdown(
            login_header_html,
            unsafe_allow_html=True
        )

        username = st.text_input(
            "Username",
            placeholder="Masukkan username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Masukkan password",
            key="login_password"
        )

        remember_me = st.checkbox(
            "Ingat saya",
            key="login_remember"
        )

        if st.button(
            "Masuk ke Dashboard  →",
            width="stretch",
            type="primary",
            key="login_button"
        ):

            user = verify_login(
                username.strip(),
                password
            )

            if user:

                st.session_state[
                    "authenticated"
                ] = True

                st.session_state[
                    "username"
                ] = user[
                    "username"
                ]

                st.session_state[
                    "role"
                ] = user[
                    "role"
                ]

                create_login_session(
                    user["id"]
            )

                st.rerun()

            else:

                st.error(
                    "Username atau password salah."
                )

        login_security_html = (
            '<div class="login-security-new">'
            '🔒 Masukkan akun administrator untuk membuka dashboard.'
            '</div>'
        )

        st.markdown(
            login_security_html,
            unsafe_allow_html=True
        )

    st.stop()

# =========================================================
# AUTO LOGOUT JIKA IDLE 10 MENIT
# =========================================================

components.html(
    f"""
    <script>

    const IDLE_TIME =
        {IDLE_MINUTES * 60 * 1000};

    let idleTimer;


    function logoutIdle() {{

        parent.document.cookie =
            "{COOKIE_NAME}=; "
            + "expires=Thu, 01 Jan 1970 00:00:00 UTC; "
            + "path=/;";

        parent.location.reload();

    }}


    function resetIdleTimer() {{

        clearTimeout(
            idleTimer
        );

        idleTimer = setTimeout(
            logoutIdle,
            IDLE_TIME
        );

    }}


    const events = [
        "mousemove",
        "mousedown",
        "keydown",
        "click",
        "scroll",
        "touchstart"
    ];


    events.forEach(
        function(eventName) {{

            parent.document.addEventListener(
                eventName,
                resetIdleTimer,
                true
            );

        }}
    );


    resetIdleTimer();

    </script>
    """,
    height=0
)

# =========================================================
# HELPER
# =========================================================

def safe_text(value):

    if value is None:
        return ""

    try:

        if pd.isna(value):
            return ""

    except Exception:
        pass

    return str(value)


def normalize_platform_value(value):

    value = safe_text(value).strip().casefold()

    if value == "instagram":
        return "Instagram"

    if value == "tiktok":
        return "TikTok"

    return safe_text(value).strip()


# =========================================================
# LOGOUT
# =========================================================

def logout():

    delete_login_session()

    st.session_state.clear()

    st.session_state[
        "authenticated"
    ] = False


def safe_number(value):

    number = pd.to_numeric(
        value,
        errors="coerce"
    )

    if pd.isna(number):
        return 0

    return int(number)


def format_angka_ringkas(value):

    angka = safe_number(value)

    if angka >= 1_000_000:

        hasil = angka / 1_000_000

        if hasil.is_integer():
            return f"{int(hasil)}M"

        return (
            f"{hasil:.1f}"
            .replace(".", ",")
            + "M"
        )

    if angka >= 1_000:

        hasil = angka / 1_000

        if hasil.is_integer():
            return f"{int(hasil)}K"

        return (
            f"{hasil:.1f}"
            .replace(".", ",")
            + "K"
        )

    return str(angka)


def format_date(value):

    if pd.isna(value):
        return "-"

    try:

        tanggal = pd.to_datetime(
            value,
            errors="coerce"
        )

        if pd.isna(tanggal):
            return "-"

        return tanggal.strftime(
            "%d-%m-%Y"
        )

    except Exception:

        return "-"


def normalize_topic_value(value):

    value = safe_text(value).strip()

    if not value:
        return "Lainnya"

    return value


def topic_equals(series, selected_topic):

    selected = normalize_topic_value(
        selected_topic
    ).casefold()

    return (
        series
        .fillna("Lainnya")
        .astype(str)
        .str.strip()
        .str.casefold()
        == selected
    )


def get_related_post_ids(
    posts_df,
    comments_df,
    selected_topic
):

    if selected_topic == "Semua":

        return set(
            posts_df["post_id"]
            .astype(str)
            .tolist()
        )

    related_ids = set()

    if not posts_df.empty:

        post_match = posts_df[
            topic_equals(
                posts_df["topic"],
                selected_topic
            )
        ]

        related_ids.update(
            post_match["post_id"]
            .astype(str)
            .tolist()
        )

    if not comments_df.empty:

        comment_match = comments_df[
            topic_equals(
                comments_df["topic"],
                selected_topic
            )
        ]

        related_ids.update(
            comment_match["post_id"]
            .astype(str)
            .tolist()
        )

    return related_ids


def show_source_button(
    url,
    label="🔗 Buka Sumber"
):

    url = safe_text(
        url
    ).strip()

    if (
        url.startswith("http://")
        or url.startswith("https://")
    ):

        st.link_button(
            label,
            url,
            width="content"
        )


# =========================================================
# SKOR KUALITAS KOMENTAR
# =========================================================

GENERIC_SHORT_COMMENTS = {
    "mantap",
    "mantap pak",
    "mantap min",
    "keren",
    "keren pak",
    "bagus",
    "bagus pak",
    "hadir",
    "present",
    "presen",
    "pertama",
    "first",
    "lebay",
    "setuju",
    "betul",
    "benar",
    "sip",
    "oke",
    "ok",
    "nice",
    "good",
    "semangat",
    "lanjut",
    "gas",
    "wkwk",
    "wkwkwk",
    "haha",
    "hehe",
    "lol"
}


IMPORTANT_SHORT_PATTERNS = [
    "jalan rusak",
    "jalan bolong",
    "aspal rusak",
    "tambah armada",
    "kurang armada",
    "mudik gratis",
    "bansos kapan",
    "air mati",
    "pdam mati",
    "banjir lagi",
    "butuh kerja",
    "cari kerja",
    "sekolah rusak",
    "atap roboh",
    "tolong perbaiki",
    "tolong diperbaiki",
    "macet parah",
    "sampah menumpuk",
    "saluran mampet",
    "drainase mampet"
]


def normalize_comment_for_quality(text):

    text = safe_text(text).lower()

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    text = re.sub(
        r"[@#]\w+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def comment_quality_score(text):

    cleaned = normalize_comment_for_quality(text)

    if not cleaned:
        return 0

    alpha_words = re.findall(
        r"[a-zA-Z]+",
        cleaned
    )

    if not alpha_words:
        return 0

    normalized_words = " ".join(
        alpha_words
    ).lower()

    if normalized_words in GENERIC_SHORT_COMMENTS:
        return 1

    score = 0
    word_count = len(alpha_words)

    if word_count >= 3:
        score += 2

    if word_count >= 6:
        score += 2

    if word_count >= 12:
        score += 2

    total_letters = sum(
        len(word)
        for word in alpha_words
    )

    if total_letters >= 15:
        score += 1

    if total_letters >= 30:
        score += 1

    if any(
        pattern in normalized_words
        for pattern in IMPORTANT_SHORT_PATTERNS
    ):
        score += 4

    if "?" in cleaned:
        score += 1

    if word_count <= 1:
        score = min(
            score,
            1
        )

    return score


# =========================================================
# LOAD POSTS
# =========================================================

@st.cache_data(ttl=30)
def load_posts():
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()

        if not rows:
            return pd.DataFrame()

        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(
                df["tanggal"],
                format="mixed",
                errors="coerce",
                utc=True,
            ).dt.tz_localize(None)

            df.loc[
                df["tanggal"] < pd.Timestamp("2020-01-01"),
                "tanggal"
            ] = pd.NaT

        return df

    except Exception as e:
        print(f"ERROR load_posts: {type(e).__name__}: {e}")
        raise

    finally:
        if conn is not None:
            conn.close()


# =========================================================
# LOAD COMMENTS
# =========================================================

@st.cache_data(ttl=30)
def load_comments():
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comments")
        rows = cursor.fetchall()

        if not rows:
            return pd.DataFrame()

        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(
                df["tanggal"],
                format="mixed",
                errors="coerce",
                utc=True,
            ).dt.tz_localize(None)

            df.loc[
                df["tanggal"] < pd.Timestamp("2020-01-01"),
                "tanggal"
            ] = pd.NaT

        return df

    except Exception as e:
        print(f"ERROR load_comments: {type(e).__name__}: {e}")
        raise

    finally:
        if conn is not None:
            conn.close()

# =========================================================
# AMBIL DATA
# =========================================================

posts = load_posts()
comments = load_comments()


if not posts.empty:

    posts["platform"] = (
        posts["platform"]
        .apply(normalize_platform_value)
    )


if not comments.empty:

    comments["platform"] = (
        comments["platform"]
        .apply(normalize_platform_value)
    )


if not posts.empty:

    posts["topic"] = (
        posts["topic"]
        .fillna("Lainnya")
        .astype(str)
        .str.strip()
    )


if not comments.empty:

    comments["topic"] = (
        comments["topic"]
        .fillna("Lainnya")
        .astype(str)
        .str.strip()
    )


# =========================================================
# URL POST BERDASARKAN POST_ID
# =========================================================

post_url_map = {}
post_caption_map = {}

if not posts.empty:

    post_url_map = dict(
        zip(
            posts["post_id"].astype(str),
            posts["url"]
            .fillna("")
            .astype(str)
        )
    )

    post_caption_map = dict(
        zip(
            posts["post_id"].astype(str),
            posts["caption"]
            .fillna("")
            .astype(str)
        )
    )


# =========================================================
# SATUKAN POSTINGAN + KOMENTAR
# =========================================================

if not posts.empty:

    posts_data = pd.DataFrame(
        {
            "id":
                posts["post_id"],

            "post_id":
                posts["post_id"],

            "platform":
                posts["platform"],

            "jenis_data":
                "Konten",

            "teks":
                posts["caption"],

            "tanggal":
                posts["tanggal"],

            "sentiment":
                posts["sentiment"],

            "topic":
                posts["topic"],

            "url":
                posts["url"],

            "username":
                ""
        }
    )

else:

    posts_data = pd.DataFrame(
        columns=[
            "id",
            "post_id",
            "platform",
            "jenis_data",
            "teks",
            "tanggal",
            "sentiment",
            "topic",
            "url",
            "username"
        ]
    )


if not comments.empty:

    comments_data = pd.DataFrame(
        {
            "id":
                comments["comment_id"],

            "post_id":
                comments["post_id"],

            "platform":
                comments["platform"],

            "jenis_data":
                "Komentar",

            "teks":
                comments["text"],

            "tanggal":
                comments["tanggal"],

            "sentiment":
                comments["sentiment"],

            "topic":
                comments["topic"],

            "url": (
                comments["post_id"]
                .astype(str)
                .map(post_url_map)
                .fillna("")
                .where(
                    comments["post_id"]
                    .astype(str)
                    .map(post_url_map)
                    .fillna("")
                    .str.strip()
                    != "",
                    comments["url"]
                    .fillna("")
                    .astype(str)
                    )
                    ),

            "username":
                comments[
                    "username"
                ].fillna("")
        }
    )

else:

    comments_data = pd.DataFrame(
        columns=[
            "id",
            "post_id",
            "platform",
            "jenis_data",
            "teks",
            "tanggal",
            "sentiment",
            "topic",
            "url",
            "username"
        ]
    )


data = pd.concat(
    [
        posts_data,
        comments_data
    ],
    ignore_index=True
)


# =========================================================
# BERSIHKAN DATA
# =========================================================

if not data.empty:

    data["sentiment"] = (
        data["sentiment"]
        .fillna("Belum Dianalisis")
    )

    data["topic"] = (
        data["topic"]
        .fillna("Lainnya")
    )

    data["teks"] = (
        data["teks"]
        .fillna("")
    )

    data["url"] = (
        data["url"]
        .fillna("")
    )

    data["username"] = (
        data["username"]
        .fillna("")
    )

    # =========================================================
# HELPER UPLOAD DATASET
# =========================================================

def cari_kolom_otomatis(
    df,
    kandidat
):

    for nama_kandidat in kandidat:

        for nama_kolom in df.columns:

            if (
                str(nama_kolom)
                .strip()
                .casefold()
                ==
                str(nama_kandidat)
                .strip()
                .casefold()
            ):
                return nama_kolom

    return None


def ambil_nilai(
    row,
    kolom,
    default=""
):

    if kolom is None:
        return default

    try:

        value = row[kolom]

        if pd.isna(value):
            return default

        return value

    except Exception:
        return default


def angka_aman(
    value
):

    try:

        if pd.isna(value):
            return 0

        return int(
            float(value)
        )

    except Exception:
        return 0


def tanggal_aman(
    value
):

    if value is None:
        return ""

    try:

        if pd.isna(value):
            return ""

    except Exception:
        pass

    try:

        tanggal = pd.to_datetime(
            value,
            errors="coerce",
            utc=True
        )

        if pd.isna(tanggal):
            return str(value)

        tanggal = tanggal.tz_convert(
            None
        )

        return tanggal.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except Exception:

        return str(value)


def buat_id_otomatis(
    platform,
    jenis_data,
    text,
    tanggal="",
    url=""
):

    bahan = (
        f"{platform}|"
        f"{jenis_data}|"
        f"{text}|"
        f"{tanggal}|"
        f"{url}"
    )

    return hashlib.sha256(
        bahan.encode(
            "utf-8",
            errors="ignore"
        )
    ).hexdigest()[:32]


def ambil_hashtag(
    text
):

    if not text:
        return ""

    hasil = re.findall(
        r"#\w+",
        str(text)
    )

    return " ".join(
        hasil
    )


# =========================================================
# PROSES DATASET UPLOAD
# =========================================================

def proses_dataset_upload(
    df,
    platform,
    jenis_data
):

    # -----------------------------------------------------
    # HASIL PROSES
    # -----------------------------------------------------

    hasil = {
        "total": len(df),
        "berhasil": 0,
        "duplikat": 0,
        "kosong": 0,
        "gagal": 0
    }


    # =====================================================
    # DETEKSI KOLOM TEKS
    # =====================================================

    if jenis_data == "Konten":

        kolom_teks = cari_kolom_otomatis(
            df,
            [
                "caption",
                "text",
                "fullText",
                "description",
                "content",
                "title"
            ]
        )

    else:

        kolom_teks = cari_kolom_otomatis(
            df,
            [
                "text",
                "comment",
                "comments",
                "commentText",
                "content",
                "fullText"
            ]
        )


    if kolom_teks is None:

        raise ValueError(
            "Kolom teks tidak ditemukan pada "
            "dataset CSV."
        )


    # =====================================================
    # KOLOM UMUM
    # =====================================================

    kolom_tanggal = cari_kolom_otomatis(
        df,
        [
            "timestamp",
            "createdAt",
            "createTime",
            "createTimeISO",
            "date",
            "datetime",
            "publishedAt",
            "takenAt",
            "tanggal"
        ]
    )


    kolom_url = cari_kolom_otomatis(
    df,
    [
        "commentUrl",
        "url",
        "postUrl",
        "postUrl_postingan",
        "videoUrl",
        "inputUrl",
        "webVideoUrl"
    ]
)


    # =====================================================
    # DATABASE
    # =====================================================

    conn = get_connection()
    cursor = conn.cursor()

    waktu_sekarang = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    try:

        # =================================================
        # KONTEN / POSTINGAN
        # =================================================

        if jenis_data == "Konten":

            kolom_post_id = cari_kolom_otomatis(
                df,
                [
                    "post_id",
                    "postId",
                    "shortCode",
                    "shortcode",
                    "id",
                    "videoId",
                    "aweme_id"
                ]
            )


            kolom_likes = cari_kolom_otomatis(
                df,
                [
                    "likesCount",
                    "likes",
                    "diggCount",
                    "likeCount"
                ]
            )


            kolom_comments_count = (
                cari_kolom_otomatis(
                    df,
                    [
                        "commentsCount",
                        "commentCount",
                        "comments"
                    ]
                )
            )


            kolom_views = cari_kolom_otomatis(
                df,
                [
                    "views",
                    "viewsCount",
                    "playCount",
                    "viewCount"
                ]
            )


            kolom_shares = cari_kolom_otomatis(
                df,
                [
                    "shares",
                    "sharesCount",
                    "shareCount"
                ]
            )


            kolom_hashtag = cari_kolom_otomatis(
                df,
                [
                    "hashtag",
                    "hashtags"
                ]
            )


            kolom_source_query = (
                cari_kolom_otomatis(
                    df,
                    [
                        "source_query",
                        "query",
                        "searchQuery",
                        "searchTerm"
                    ]
                )
            )


            for _, row in df.iterrows():

                try:

                    caption = str(
                        ambil_nilai(
                            row,
                            kolom_teks,
                            ""
                        )
                    ).strip()


                    if not caption:

                        hasil["kosong"] += 1
                        continue


                    tanggal = tanggal_aman(
                        ambil_nilai(
                            row,
                            kolom_tanggal,
                            ""
                        )
                    )


                    url = str(
                        ambil_nilai(
                            row,
                            kolom_url,
                            ""
                        )
                    ).strip()


                    post_id = str(
                        ambil_nilai(
                            row,
                            kolom_post_id,
                            ""
                        )
                    ).strip()


                    # -------------------------------------
                    # BUAT ID JIKA DATASET TIDAK PUNYA ID
                    # -------------------------------------

                    if not post_id:

                        post_id = buat_id_otomatis(
                            platform,
                            jenis_data,
                            caption,
                            tanggal,
                            url
                        )


                    # -------------------------------------
                    # CEK DUPLIKAT
                    # -------------------------------------

                    cursor.execute(
                        """
                        SELECT 1
                        FROM posts
                        WHERE post_id = ?
                        LIMIT 1
                        """,
                        (
                            post_id,
                        )
                    )


                    if cursor.fetchone():

                        hasil["duplikat"] += 1
                        continue


                    # -------------------------------------
                    # SENTIMEN
                    # -------------------------------------

                    sentiment = classify_sentiment(
                        caption
                    )


                    # -------------------------------------
                    # TOPIK
                    # -------------------------------------

                    topic = classify_topic(
                        caption
                    )


                    # -------------------------------------
                    # ENGAGEMENT
                    # -------------------------------------

                    likes = angka_aman(
                        ambil_nilai(
                            row,
                            kolom_likes,
                            0
                        )
                    )


                    comments_count = angka_aman(
                        ambil_nilai(
                            row,
                            kolom_comments_count,
                            0
                        )
                    )


                    views = angka_aman(
                        ambil_nilai(
                            row,
                            kolom_views,
                            0
                        )
                    )


                    shares = angka_aman(
                        ambil_nilai(
                            row,
                            kolom_shares,
                            0
                        )
                    )


                    # -------------------------------------
                    # HASHTAG
                    # -------------------------------------

                    hashtag = str(
                        ambil_nilai(
                            row,
                            kolom_hashtag,
                            ""
                        )
                    ).strip()


                    if not hashtag:

                        hashtag = ambil_hashtag(
                            caption
                        )


                    source_query = str(
                        ambil_nilai(
                            row,
                            kolom_source_query,
                            ""
                        )
                    ).strip()


                    # -------------------------------------
                    # INSERT DATABASE
                    # -------------------------------------

                    cursor.execute(
                        """
                        INSERT INTO posts (
                            post_id,
                            platform,
                            caption,
                            tanggal,
                            hashtag,
                            url,
                            likes,
                            comments_count,
                            views,
                            shares,
                            sentiment,
                            topic,
                            first_seen_at,
                            last_checked_at,
                            collection_type,
                            source_query
                        )
                        VALUES (
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?
                        )
                        """,
                        (
                            post_id,
                            platform,
                            caption,
                            tanggal,
                            hashtag,
                            url,
                            likes,
                            comments_count,
                            views,
                            shares,
                            sentiment,
                            topic,
                            waktu_sekarang,
                            waktu_sekarang,
                            "upload_csv",
                            source_query
                        )
                    )


                    hasil["berhasil"] += 1


                except Exception:

                    hasil["gagal"] += 1


        # =================================================
        # KOMENTAR
        # =================================================

        else:

            kolom_comment_id = (
                cari_kolom_otomatis(
                    df,
                    [
                        "comment_id",
                        "commentId",
                        "id",
                        "cid"
                    ]
                )
            )


            kolom_post_id = cari_kolom_otomatis(
                df,
                [
                    "post_id",
                    "postId",
                    "shortCode",
                    "shortcode",
                    "videoId",
                    "aweme_id"
                ]
            )


            for _, row in df.iterrows():

                try:

                    text = str(
                        ambil_nilai(
                            row,
                            kolom_teks,
                            ""
                        )
                    ).strip()


                    if not text:

                        hasil["kosong"] += 1
                        continue


                    tanggal = tanggal_aman(
                        ambil_nilai(
                            row,
                            kolom_tanggal,
                            ""
                        )
                    )


                    url = str(
                        ambil_nilai(
                            row,
                            kolom_url,
                            ""
                        )
                    ).strip()


                    post_id = str(
                        ambil_nilai(
                            row,
                            kolom_post_id,
                            ""
                        )
                    ).strip()


                    comment_id = str(
                        ambil_nilai(
                            row,
                            kolom_comment_id,
                            ""
                        )
                    ).strip()


                    # -------------------------------------
                    # BUAT COMMENT ID OTOMATIS
                    # -------------------------------------

                    if not comment_id:

                        comment_id = (
                            buat_id_otomatis(
                                platform,
                                jenis_data,
                                text,
                                tanggal,
                                (
                                    post_id
                                    or url
                                )
                            )
                        )


                    # -------------------------------------
                    # CEK DUPLIKAT
                    # -------------------------------------

                    cursor.execute(
                        """
                        SELECT 1
                        FROM comments
                        WHERE comment_id = ?
                        LIMIT 1
                        """,
                        (
                            comment_id,
                        )
                    )


                    if cursor.fetchone():

                        hasil["duplikat"] += 1
                        continue


                    # -------------------------------------
                    # SENTIMEN
                    # -------------------------------------

                    sentiment = classify_sentiment(
                        text
                    )


                    # -------------------------------------
                    # CARI KONTEKS POSTINGAN
                    # -------------------------------------

                    post_caption = ""
                    post_topic = "Lainnya"


                    if post_id:

                        cursor.execute(
                            """
                            SELECT
                                caption,
                                topic
                            FROM posts
                            WHERE post_id = ?
                            LIMIT 1
                            """,
                            (
                                post_id,
                            )
                        )


                        post_data = cursor.fetchone()


                        if post_data:

                            post_caption = (
                                post_data[0]
                                or ""
                            )

                            post_topic = (
                                post_data[1]
                                or "Lainnya"
                            )


                    # -------------------------------------
                    # TOPIK KOMENTAR
                    # -------------------------------------

                    topic = (
                        classify_comment_with_context(
                            text,
                            post_caption,
                            post_topic
                        )
                    )

                    # -------------------------------------
                    # # INSERT COMMENT
                    # # -------------------------------------
                     
                    cursor.execute(
                        """
                        INSERT INTO comments (
                        comment_id,
                        post_id,
                        platform,
                        text,
                        tanggal,
                        sentiment,
                        topic,
                        url,
                        first_seen_at,
                        collection_type
                        )
                        VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?
                     )
                    """,
                    (
                        comment_id,
                        post_id,
                        platform,
                        text,
                        tanggal,
                        sentiment,
                        topic,
                        url,
                        waktu_sekarang,
                        "upload_csv"
                        )
                    )


                    hasil["berhasil"] += 1


                except Exception as e:

                    hasil["gagal"] += 1
                    print(f"ERROR UPLOAD COMMENT: {e}")


        # =================================================
        # COMMIT
        # =================================================

        conn.commit()


    except Exception:

        conn.rollback()
        raise


    finally:

        conn.close()


    return hasil

# =========================================================
# STATE UPLOAD DATASET
# =========================================================

if "tampilkan_upload" not in st.session_state:
    st.session_state["tampilkan_upload"] = False

# =========================================================
# HEADER
# =========================================================

logo_header_html = (
    f'<img src="data:image/png;base64,{logo_karawang}" '
    'class="hero-logo">'
    if logo_karawang
    else ""
)

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">
            {logo_header_html}
            <h1>Karawang Social Analytics</h1>
        </div>
        <p>
            Analisis otomatis postingan dan komentar Instagram
            serta TikTok berdasarkan sentimen dan topik.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# UPLOAD DATASET DI DASHBOARD
# =========================================================

if st.session_state["tampilkan_upload"]:

    st.markdown("## Upload Dataset")

    st.caption(
        "Unggah dataset CSV baru untuk diproses "
        "dan dianalisis."
    )


    # =====================================================
    # PENGATURAN DATASET
    # =====================================================

    upload_col1, upload_col2 = st.columns(2)

    with upload_col1:

        upload_platform = st.selectbox(
            "Platform",
            [
                "Instagram",
                "TikTok"
            ],
            key="upload_platform"
        )

    with upload_col2:

        upload_jenis_data = st.selectbox(
            "Jenis Data",
            [
                "Konten",
                "Komentar"
            ],
            key="upload_jenis_data"
        )


    # =====================================================
    # SYARAT DATASET
    # =====================================================

    with st.expander(
        "Syarat dan Ketentuan Dataset",
        expanded=False
    ):

        st.markdown(
            """
            **Ketentuan Dataset:**

            - Dataset harus menggunakan format **CSV (.csv)**.
            - Dataset dapat berasal dari **Instagram** atau **TikTok**.
            - Dataset dapat berupa **Konten** atau **Komentar**.
            - Dataset harus memiliki caption postingan
              atau teks komentar.
            - Data dengan teks kosong tidak akan diproses.
            - Dataset dapat berasal dari hasil pengumpulan
              menggunakan **Apify**.
            - Struktur kolom akan dikenali secara otomatis.

            **Proses Dataset:**

            Dataset akan diperiksa terlebih dahulu.
            Setelah itu sistem akan melakukan analisis sentimen
            dan klasifikasi topik sebelum data disimpan
            ke database.
            """
        )


    # =====================================================
    # UPLOAD CSV
    # =====================================================

    uploaded_file = st.file_uploader(
        "Upload Dataset CSV",
        type=["csv"],
        help=(
            "Upload dataset hasil pengumpulan data "
            "Instagram atau TikTok."
        ),
        key="dataset_uploader"
    )


    # =====================================================
    # JIKA FILE SUDAH DIPILIH
    # =====================================================

    if uploaded_file is not None:

        try:

            try:

                df_upload = pd.read_csv(
                    uploaded_file
                )

            except UnicodeDecodeError:

                uploaded_file.seek(0)

                df_upload = pd.read_csv(
                    uploaded_file,
                    encoding="latin-1"
                )


            # =================================================
            # CEK DATASET KOSONG
            # =================================================

            if df_upload.empty:

                st.error(
                    "Dataset kosong dan tidak dapat diproses."
                )

            else:

                # =============================================
                # INFORMASI DATASET
                # =============================================

                st.success(
                    f"Dataset berhasil dibaca: "
                    f"{len(df_upload):,} baris data."
                )

                upload_info1, upload_info2, upload_info3 = (
                    st.columns(3)
                )

                upload_info1.metric(
                    "Jumlah Data",
                    f"{len(df_upload):,}"
                )

                upload_info2.metric(
                    "Jumlah Kolom",
                    len(df_upload.columns)
                )

                upload_info3.metric(
                    "Nama File",
                    uploaded_file.name
                )


                # =============================================
                # PREVIEW DATASET
                # =============================================

                st.subheader(
                    "Preview Dataset"
                )

                st.caption(
                    "Menampilkan 10 baris pertama."
                )

                st.dataframe(
                    df_upload.head(10),
                    width="stretch",
                    hide_index=True
                )


                # =============================================
                # KANDIDAT KOLOM TEKS
                # =============================================

                if upload_jenis_data == "Konten":

                    kandidat_teks_upload = [
                        "caption",
                        "text",
                        "fullText",
                        "description",
                        "content",
                        "title"
                    ]

                else:

                    kandidat_teks_upload = [
                        "text",
                        "comment",
                        "comments",
                        "commentText",
                        "content",
                        "fullText"
                    ]


                # =============================================
                # DETEKSI KOLOM TEKS
                # =============================================

                kolom_teks_upload = cari_kolom_otomatis(
                    df_upload,
                    kandidat_teks_upload
                )


                # =============================================
                # VALIDASI STRUKTUR
                # =============================================

                if kolom_teks_upload is None:

                    st.error(
                        "Struktur dataset tidak sesuai. "
                        "Kolom caption atau teks komentar "
                        "tidak ditemukan."
                    )

                    st.caption(
                        "Kolom yang ditemukan: "
                        + ", ".join(
                            str(kolom)
                            for kolom in df_upload.columns
                        )
                    )

                else:

                    st.success(
                        f"Struktur dataset berhasil dikenali. "
                        f"Kolom teks: {kolom_teks_upload}"
                    )


                    # =========================================
                    # HITUNG DATA VALID
                    # =========================================

                    teks_valid_upload = (
                        df_upload[
                            kolom_teks_upload
                        ]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                    )

                    jumlah_valid_upload = int(
                        (
                            teks_valid_upload != ""
                        ).sum()
                    )

                    jumlah_kosong_upload = int(
                        (
                            teks_valid_upload == ""
                        ).sum()
                    )


                    valid1, valid2, valid3 = st.columns(3)

                    valid1.metric(
                        "Total Data",
                        len(df_upload)
                    )

                    valid2.metric(
                        "Data Valid",
                        jumlah_valid_upload
                    )

                    valid3.metric(
                        "Teks Kosong",
                        jumlah_kosong_upload
                    )


                    # =========================================
                    # TOMBOL PROSES
                    # =========================================

                    if jumlah_valid_upload == 0:

                        st.error(
                            "Tidak terdapat data teks "
                            "yang dapat diproses."
                        )

                    else:

                        if st.button(
                            "Proses Dataset",
                            type="primary",
                            width="stretch",
                            key="btn_proses_dataset"
                        ):

                            try:

                                with st.spinner(
                                    "Menganalisis sentimen "
                                    "dan topik..."
                                ):

                                    hasil_proses = (
                                        proses_dataset_upload(
                                            df_upload,
                                            upload_platform,
                                            upload_jenis_data
                                        )
                                    )


                                st.success(
                                    "Dataset selesai diproses "
                                    "dan disimpan ke database."
                                )


                                hasil1, hasil2, hasil3, hasil4 = (
                                    st.columns(4)
                                )

                                hasil1.metric(
                                    "Berhasil",
                                    hasil_proses["berhasil"]
                                )

                                hasil2.metric(
                                    "Duplikat",
                                    hasil_proses["duplikat"]
                                )

                                hasil3.metric(
                                    "Teks Kosong",
                                    hasil_proses["kosong"]
                                )

                                hasil4.metric(
                                    "Gagal",
                                    hasil_proses["gagal"]
                                )


                                # Refresh data dashboard
                                load_posts.clear()
                                load_comments.clear()


                                st.info(
                                    "Data yang berhasil diproses "
                                    "sudah dapat digunakan pada "
                                    "dashboard."
                                )

                            except Exception as e:

                                st.error(
                                    f"Dataset gagal diproses: {e}"
                                )


        except Exception as e:

            st.error(
                f"Dataset gagal dibaca: {e}"
            )


    st.divider()

# =========================================================
# CALLBACK SIDEBAR
# =========================================================

def buka_tutup_upload():

    st.session_state["tampilkan_upload"] = (
        not st.session_state.get(
            "tampilkan_upload",
            False
        )
    )

    # Kalau Upload Dataset dibuka,
    # kosongkan pilihan platform sementara.
    # Jadi Semua / Instagram / TikTok
    # semuanya bisa diklik untuk kembali.
    if st.session_state["tampilkan_upload"]:
        st.session_state["platform_filter"] = None


def pilih_platform_dashboard():

    # Begitu salah satu platform dipilih,
    # tutup halaman Upload Dataset.
    st.session_state["tampilkan_upload"] = False
    
# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # =====================================================
    # FILTER ANALISIS
    # =====================================================

    st.markdown(
        "## Filter Analisis"
    )


    # =====================================================
    # UPLOAD DATASET
    # =====================================================
    
    st.button(
        "Upload Dataset",
        width="stretch",
        key="btn_toggle_upload",
        on_click=buka_tutup_upload
    )

    # =====================================================
    # PLATFORM
    # =====================================================

    platform = st.radio(
        "Platform",
        [
            "Semua",
            "Instagram",
            "TikTok"
        ],
        index=None,
        key="platform_filter",
        on_change=pilih_platform_dashboard
    )

    if platform is None:
        platform_aktif = "Semua"
    else:
        platform_aktif = platform

    st.markdown(
        f"""
        <style>

        .st-key-platform_filter
        [role="radiogroup"] label {{
            position: relative !important;
            padding-left: 55px !important;
        }}

        .st-key-platform_filter
        [role="radiogroup"]
        label:nth-child(1)::before {{
            content: "🌐";
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 27px;
            height: 27px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 23px;
        }}

        .st-key-platform_filter
        [role="radiogroup"]
        label:nth-child(2)::before {{
            content: "";
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 27px;
            height: 27px;
            background-image:
                url("data:image/png;base64,{logo_instagram}");
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
        }}

        .st-key-platform_filter
        [role="radiogroup"]
        label:nth-child(3)::before {{
            content: "";
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 27px;
            height: 27px;
            background-image:
                url("data:image/png;base64,{logo_tiktok}");
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

        # =====================================================
    # JENIS DATA
    # =====================================================

    jenis_data = st.selectbox(
        "Jenis Data",
        ["Semua", "Konten", "Komentar"],
        key="jenis_data_filter"
    )

    # =====================================================
    # SENTIMEN
    # =====================================================

    sentimen = st.radio(
        "Sudut Pandang Sentimen",
        ["Semua", "Positif", "Netral", "Negatif"],
        horizontal=True,
        key="sentimen_filter"
    )

    # =====================================================
    # TOPIK
    # =====================================================

    topik_list = ["Semua"] + TOPIC_LIST

    topik = st.selectbox(
        "Topik",
        topik_list,
        key="topik_filter"
    )

    # =====================================================
    # JUMLAH SAMPEL
    # =====================================================

    jumlah_sample = st.selectbox(
        "Jumlah Sampel per Sentimen",
        [5, 10, 20, 50],
        index=1,
        key="jumlah_sample_filter"
    )

    # =====================================================
    # PERIODE
    # =====================================================

    data_periode = data.copy()

    if platform_aktif != "Semua":

        data_periode = data_periode[
            data_periode["platform"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.casefold()
            == platform_aktif.casefold()
        ].copy()

    if (
        not data_periode.empty
        and data_periode["tanggal"].notna().any()
    ):
        
        # Pastikan tanggal valid sebelum menentukan periode
        tanggal_valid = pd.to_datetime(
            data_periode["tanggal"],
            errors="coerce",
            utc=True
        ).dropna()

        if not tanggal_valid.empty:
            tanggal_min = tanggal_valid.min().date()
            tanggal_max = tanggal_valid.max().date()

            periode = st.date_input(
                "Periode",
                value=(tanggal_min, tanggal_max),
                min_value=tanggal_min,
                max_value=datetime(
                    datetime.now().year + 1,
                    12,
                    31
                ).date(),
                key=f"periode_{platform_aktif}"
            )

            if (
                isinstance(periode, (tuple, list))
                and len(periode) == 2
            ):
                tanggal_mulai = periode[0]
                tanggal_selesai = periode[1]
            else:
                tanggal_mulai = tanggal_min
                tanggal_selesai = tanggal_max

        else:
            st.warning(
                "Tidak ada tanggal valid pada data untuk periode ini."
            )
            tanggal_mulai = None
            tanggal_selesai = None

    else:
        tanggal_mulai = None
        tanggal_selesai = None


    # =====================================================
    # LOGOUT
    # =====================================================

    st.markdown("---")

    if st.button(
        "➜] Keluar",
        width="stretch",
        key="btn_logout_global"
    ):
        logout()
        st.rerun()


# =========================================================
# JIKA SEDANG MEMBUKA UPLOAD DATASET
# JANGAN TAMPILKAN ISI DASHBOARD
# =========================================================

if st.session_state.get(
    "tampilkan_upload",
    False
):
    st.stop()

# =========================================================
# FILTER DATA
# =========================================================

filtered = data.copy()

filtered["platform"] = (
    filtered["platform"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.casefold()
)

if platform_aktif != "Semua":

    filtered = filtered[
        filtered["platform"]
        == platform_aktif.casefold()
    ].copy()

if jenis_data != "Semua":

    filtered = filtered[
        filtered["jenis_data"]
        == jenis_data
    ].copy()

if sentimen != "Semua":

    filtered = filtered[
        filtered["sentiment"]
        == sentimen
    ].copy()

if topik != "Semua":

    filtered = filtered[
        topic_equals(
            filtered["topic"],
            topik
        )
    ].copy()

if (
    tanggal_mulai is not None
    and tanggal_selesai is not None
    and not filtered.empty
):

    filtered = filtered[
        (
            filtered["tanggal"].dt.date
            >= tanggal_mulai
        )
        &
        (
            filtered["tanggal"].dt.date
            <= tanggal_selesai
        )
    ].copy()


# =========================================================
# RINGKASAN
# =========================================================

jumlah_total = len(
    filtered
)


jumlah_post = len(
    filtered[
        filtered["jenis_data"]
        == "Konten"
    ]
)


jumlah_comment = len(
    filtered[
        filtered["jenis_data"]
        == "Komentar"
    ]
)


sentiment_valid = filtered[
    filtered["sentiment"].isin(
        [
            "Positif",
            "Netral",
            "Negatif"
        ]
    )
]


total_sentiment = len(
    sentiment_valid
)


def hitung_persen(
    sentiment_name
):

    if total_sentiment == 0:
        return 0.0

    jumlah = len(
        sentiment_valid[
            sentiment_valid["sentiment"]
            == sentiment_name
        ]
    )

    return round(
        jumlah
        / total_sentiment
        * 100,
        1
    )


persen_positif = hitung_persen(
    "Positif"
)

persen_netral = hitung_persen(
    "Netral"
)

persen_negatif = hitung_persen(
    "Negatif"
)


st.subheader(
    "Ringkasan Monitoring"
)


r1, r2, r3, r4, r5, r6 = (
    st.columns(6)
)


r1.metric(
    "Total Data",
    jumlah_total
)

r2.metric(
    "Postingan",
    jumlah_post
)

r3.metric(
    "Komentar",
    jumlah_comment
)

r4.metric(
    "Positif",
    f"{persen_positif}%"
)

r5.metric(
    "Netral",
    f"{persen_netral}%"
)

r6.metric(
    "Negatif",
    f"{persen_negatif}%"
)


st.divider()


# =========================================================
# DISTRIBUSI SENTIMEN + TOPIK
# =========================================================

grafik1, grafik2 = st.columns(2)


with grafik1:

    st.subheader(
        "Distribusi Sentimen"
    )

    sentiment_count = (
        sentiment_valid[
            "sentiment"
        ]
        .value_counts()
        .reset_index()
    )

    sentiment_count.columns = [
        "Sentimen",
        "Jumlah"
    ]

    if not sentiment_count.empty:

        fig_sentiment = px.pie(
            sentiment_count,
            names="Sentimen",
            values="Jumlah",
            hole=0.55
        )

        fig_sentiment.update_traces(
            textinfo="percent+label"
        )

        fig_sentiment.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            )
        )

        st.plotly_chart(
            fig_sentiment,
            width="stretch"
        )

    else:

        st.info(
            "Tidak ada data sentimen "
            "untuk filter ini."
        )


with grafik2:

    st.subheader(
        "Topik Paling Banyak Dibahas"
    )

    topic_count = (
        filtered[
            filtered["topic"]
            != "Lainnya"
        ]["topic"]
        .value_counts()
        .reset_index()
    )

    topic_count.columns = [
        "Topik",
        "Jumlah"
    ]

    if not topic_count.empty:

        fig_topic = px.bar(
            topic_count,
            x="Jumlah",
            y="Topik",
            orientation="h"
        )

        fig_topic.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )

        st.plotly_chart(
            fig_topic,
            width="stretch"
        )

    else:

        st.info(
            "Belum ada topik "
            "yang terdeteksi."
        )


# =========================================================
# TREN SENTIMEN
# =========================================================

st.subheader(
    "Tren Sentimen"
)


trend_data = (
    sentiment_valid
    .dropna(
        subset=["tanggal"]
    )
    .copy()
)


if not trend_data.empty:

    trend_data[
        "Bulan"
    ] = (
        trend_data[
            "tanggal"
        ]
        .dt.to_period("M")
        .astype(str)
    )

    trend = (
        trend_data
        .groupby(
            [
                "Bulan",
                "sentiment"
            ]
        )
        .size()
        .reset_index(
            name="Jumlah"
        )
    )

    fig_trend = px.line(
        trend,
        x="Bulan",
        y="Jumlah",
        color="sentiment",
        markers=True,
        labels={
            "sentiment":
                "Sentimen",

            "Jumlah":
                "Jumlah Data",

            "Bulan":
                "Periode"
        }
    )

    st.plotly_chart(
        fig_trend,
        width="stretch"
    )


else:

    st.info(
        "Belum ada data "
        "untuk tren sentimen."
    )


st.divider()

# =========================================================
# SAMPEL HASIL ANALISIS
# =========================================================

st.subheader(
    "Sampel Data Hasil Analisis"
)

st.caption(
    "Jumlah sampel dapat diatur melalui sidebar."
)


def tampilkan_sample(sample_df):

    if sample_df.empty:

        st.caption(
            "Belum ada sampel."
        )

        return

    for _, row in sample_df.iterrows():

        with st.container(
            border=True
        ):

            st.caption(
                f"{row['platform']} "
                f"• {row['jenis_data']} "
                f"• {row['topic']}"
            )

            if row["jenis_data"] == "Komentar":

                username = safe_text(
                    row["username"]
                ).strip()

                if username:

                    st.markdown(
                        f"**@{username}**"
                    )

            st.write(
                row["teks"]
            )

            if pd.notna(
                row["tanggal"]
            ):

                st.caption(
                    "Tanggal: "
                    + format_date(
                        row["tanggal"]
                    )
                )

            if row["jenis_data"] == "Komentar":

                show_source_button(
                    row["url"],
                    "🔗 Buka Postingan Sumber"
                )

            else:

                show_source_button(
                    row["url"],
                    "🔗 Buka Konten Asli"
                )


if filtered.empty:

    st.info(
        "Belum ada data untuk ditampilkan."
    )

else:

    sample = (
        filtered
        .sort_values(
            "tanggal",
            ascending=False
        )
        .head(
            jumlah_sample
        )
    )

    tampilkan_sample(
        sample
    )


st.divider()


# =========================================================
# TOPIK KELUHAN TERBANYAK
# =========================================================

st.subheader(
    "Topik dengan Keluhan Terbanyak"
)


negative_topic = (
    filtered[
        (
            filtered["sentiment"]
            == "Negatif"
        )
        &
        (
            filtered["topic"]
            != "Lainnya"
        )
    ]["topic"]
    .value_counts()
    .reset_index()
)


negative_topic.columns = [
    "Topik",
    "Jumlah Keluhan"
]


if not negative_topic.empty:

    fig_negative = px.bar(
        negative_topic,
        x="Jumlah Keluhan",
        y="Topik",
        orientation="h"
    )

    fig_negative.update_layout(
        yaxis={
            "categoryorder":
                "total ascending"
        }
    )

    st.plotly_chart(
        fig_negative,
        width="stretch"
    )


else:

    st.info(
        "Belum ada data "
        "keluhan negatif."
    )


# =========================================================
# KONTEN RAMAI
# =========================================================

st.subheader(
    "Konten Ramai Dibahas"
)


if posts.empty:

    st.info(
        "Belum ada data postingan."
    )


else:

    viral_posts = posts.copy()

    if platform_aktif != "Semua":

        viral_posts = viral_posts[
            viral_posts["platform"]
            == platform_aktif
        ]

    if topik != "Semua":

        viral_posts = viral_posts[
            topic_equals(
                viral_posts["topic"],
                topik
            )
        ]

    if sentimen != "Semua":

        viral_posts = viral_posts[
            viral_posts["sentiment"]
            == sentimen
        ]

    if (
        tanggal_mulai
        and tanggal_selesai
    ):

        viral_posts = viral_posts[
            (
                viral_posts[
                    "tanggal"
                ].dt.date
                >= tanggal_mulai
            )
            &
            (
                viral_posts[
                    "tanggal"
                ].dt.date
                <= tanggal_selesai
            )
        ]

    viral_posts = (
        viral_posts
        .sort_values(
            by="comments_count",
            ascending=False
        )
    )

    if viral_posts.empty:

        st.info(
            "Belum ada konten ramai "
            "untuk filter ini."
        )

    else:

        for _, row in (
            viral_posts
            .head(5)
            .iterrows()
        ):

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {row['platform']} "
                    f"— {row['topic']}"
                )

                st.write(
                    row["caption"]
                )

                c1, c2, c3, c4 = (
                    st.columns(4)
                )

                c1.metric(
                    "Komentar",
                    format_angka_ringkas(
                        row["comments_count"]
                    )

                )
                c2.metric(
                    "Likes",
                    format_angka_ringkas(
                        row["likes"]
                    )
                )
                c3.metric(
                    "Views",
                    format_angka_ringkas(
                        row["views"]
                    )
            )
            c4.metric(
                "Share",
                format_angka_ringkas(
                    row["shares"]
                    )
            )

            st.caption(
                    f"Sentimen Konten: "
                    f"{row['sentiment']}"
                )

            show_source_button(
                    row["url"],
                    "🔗 Buka Konten Asli"
                )


# =========================================================
# DATA POSTINGAN + KOMENTAR
# =========================================================

st.divider()


st.subheader(
    "Data Postingan dan Komentar"
)


if filtered.empty:

    st.info(
        "Tidak ada data untuk "
        "filter yang dipilih."
    )


else:

    tabel = filtered[
        [
            "tanggal",
            "platform",
            "jenis_data",
            "username",
            "teks",
            "sentiment",
            "topic",
            "url"
        ]
    ].copy()

    tabel["tanggal"] = (
        tabel["tanggal"]
        .dt.strftime(
            "%d-%m-%Y"
        )
    )

    tabel.columns = [
        "Tanggal",
        "Platform",
        "Jenis Data",
        "Username",
        "Teks",
        "Sentimen",
        "Topik",
        "Sumber"
    ]

    st.dataframe(
        tabel,
        width="stretch",
        hide_index=True,
        column_config={
            "Sumber":
                st.column_config.LinkColumn(
                    "Sumber",
                    display_text="Buka"
                )
        }
    )

# =========================================================
# AMBIL SEMUA KOMENTAR
# =========================================================

komentar_tampil = comments.copy()

# Pastikan struktur data tersedia sebelum mengakses kolom
if komentar_tampil.empty:
    st.info(
        "Data komentar belum tersedia untuk ditampilkan. "
        "Periksa koneksi database dan hasil load_comments()."
    )

elif "post_id" not in komentar_tampil.columns:
    st.error(
        "Kolom post_id tidak ditemukan pada data komentar. "
        "Periksa struktur tabel comments dan fungsi load_comments()."
    )

elif posts.empty or "post_id" not in posts.columns:
    st.warning(
        "Data postingan kosong atau kolom post_id tidak ditemukan. "
        "Komentar belum dapat dicocokkan dengan postingan."
    )

else:
    # Jika kolom topic tersedia, abaikan postingan bertopik Lainnya.
    # Jika belum tersedia, jangan langsung menggagalkan dashboard.
    if "topic" in posts.columns:
        post_relevan_ids = (
            posts.loc[
                posts["topic"].fillna("").astype(str) != "Lainnya",
                "post_id"
            ]
            .astype(str)
            .tolist()
        )
    else:
        print(
            "PERINGATAN: kolom topic tidak ditemukan pada posts. "
            "Pencocokan komentar dilakukan tanpa filter topic."
        )
        post_relevan_ids = (
            posts["post_id"]
            .dropna()
            .astype(str)
            .tolist()
        )

    komentar_tampil = komentar_tampil[
        komentar_tampil["post_id"]
        .astype(str)
        .isin(post_relevan_ids)
    ]

    # Filter platform
    if (
        "platform" in komentar_tampil.columns
        and platform_aktif != "Semua"
    ):
        komentar_tampil = komentar_tampil[
            komentar_tampil["platform"] == platform_aktif
        ]

    # Filter sentimen
    if (
        "sentiment" in komentar_tampil.columns
        and sentimen != "Semua"
    ):
        komentar_tampil = komentar_tampil[
            komentar_tampil["sentiment"] == sentimen
        ]

    # Filter tanggal hanya jika kolom tanggal tersedia
    if (
        "tanggal" in komentar_tampil.columns
        and tanggal_mulai is not None
        and tanggal_selesai is not None
        and not komentar_tampil.empty
    ):
        tanggal_data = pd.to_datetime(
            komentar_tampil["tanggal"],
            errors="coerce"
        )

        komentar_tampil = komentar_tampil.loc[
            tanggal_data.notna()
            & (tanggal_data.dt.date >= tanggal_mulai)
            & (tanggal_data.dt.date <= tanggal_selesai)
        ].copy()

    # Hitung kualitas komentar jika kolom text tersedia
    if "text" in komentar_tampil.columns:
        komentar_tampil["quality_score"] = (
            komentar_tampil["text"]
            .fillna("")
            .astype(str)
            .apply(comment_quality_score)
        )
    else:
        komentar_tampil["quality_score"] = 0

    # Urutkan berdasarkan kualitas dan tanggal yang tersedia
    kolom_urut = ["quality_score"]
    urutan = [False]

    if "tanggal" in komentar_tampil.columns:
        komentar_tampil["_tanggal_urut"] = pd.to_datetime(
            komentar_tampil["tanggal"],
            errors="coerce"
        )
        kolom_urut.append("_tanggal_urut")
        urutan.append(False)

    komentar_tampil = komentar_tampil.sort_values(
        by=kolom_urut,
        ascending=urutan
    )

    total_hasil_filter = len(komentar_tampil)

    st.caption(
        f"Ditemukan {total_hasil_filter} komentar. "
        f"Menampilkan {min(30, total_hasil_filter)} komentar."
    )

    if komentar_tampil.empty:
        st.info(
            "Tidak ada komentar yang sesuai filter. "
            "Coba pilih Semua pada filter platform dan sentimen."
        )

    else:
        for _, row in komentar_tampil.head(30).iterrows():
            with st.container(border=True):
                bagian1, bagian2 = st.columns([4, 1])

                with bagian1:
                    sentiment_value = safe_text(
                        row.get("sentiment", "Belum dianalisis")
                    )
                    topic_value = safe_text(
                        row.get("topic", "Belum diklasifikasikan")
                    )

                    st.markdown(
                        f"**{sentiment_value} • {topic_value}**"
                    )

                    username = safe_text(
                        row.get("username", "")
                    ).strip()

                    if username:
                        st.caption(f"👤 @{username}")

                    st.write(
                        safe_text(row.get("text", ""))
                    )

                    tanggal_value = format_date(
                        row.get("tanggal", "")
                    )

                    likes_value = safe_number(
                        row.get("likes", 0)
                    )

                    st.caption(
                        f"Tanggal: {tanggal_value} • "
                        f"Likes: {likes_value}"
                    )

                with bagian2:
                    post_id_comment = safe_text(
                        row.get("post_id", "")
                    )

                    source_url = post_url_map.get(
                        post_id_comment,
                        ""
                    )

                    show_source_button(
                        source_url,
                        "🔗 Sumber"
                    )

