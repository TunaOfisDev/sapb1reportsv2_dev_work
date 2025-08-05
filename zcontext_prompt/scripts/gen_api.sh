#!/usr/bin/env bash
# path: zcontext_prompt/scripts/gen_api.sh
# =============================================================================
# SAPB1ReportsV2 – zcontext_prompt – gen_api.sh v5.0 (Ana Plan)
# =============================================================================
# Kafa karışıklığını önlemek için tüm context'i ve istemi tek bir metin
# bloğunda birleştirir. 'whitepaper' context'ini kaldırır.
# =============================================================================

set -euo pipefail

# Helper function for printing styled status messages
print_status() {
    local color_green='\033[0;32m'
    local color_yellow='\033[1;33m'
    local color_blue='\033[0;34m'
    local color_nc='\033[0m' # No Color
    echo -e "\n${color_yellow}==>${color_nc} ${color_blue}$1${color_nc}"
}

# Helper function to parse and create files
create_files_from_text() {
    local text_to_parse=$1
    
    echo "$text_to_parse" | \
    sed "/^[\`']\{3\}\(python\|javascript\|jsx\|markdown\)\?$/d" | \
    awk -v out_dir="$OUT_DIR" '
    BEGIN { in_file = 0; current_file = ""; }
    /^###/ {
        filepath = $0;
        gsub(/^###/, "", filepath);
        gsub(/###$/, "", filepath);
        
        current_file = out_dir "/" filepath;
        "mkdir -p \"$(dirname \"" current_file "\")\"" | getline;
        close("mkdir -p \"$(dirname \"" current_file "\")\"");
        in_file = 1;
        print "    Oluşturuluyor: " current_file > "/dev/stderr";
        next;
    }
    /^###END_OF_FILE###/ {
        in_file = 0;
        close(current_file);
        current_file = "";
        next;
    }
    {
        if (in_file) { print $0 >> current_file; }
    }
'
}

# ---------- Ana Betik Başlangıcı ---------------------------------------------
if [[ "${2:-}" == "--debug" ]]; then
    echo "--- DEBUG MODE AKTİF ---"
    set -x
fi

CTX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(dirname "$CTX_DIR")"
ENV_FILE="$PROJECT_ROOT/backend/.env"
PROMPTS_DIR="${CTX_DIR}/prompts"
BACKEND_CTX="${CTX_DIR}/backend_context.md"
FRONTEND_CTX="${CTX_DIR}/frontend_context.md"
# WHITEPAPER_CTX="${CTX_DIR}/whitepaper_api.md" # <-- DİKKAT: Artık context olarak kullanılmıyor.
GEMINI_ENDPOINT_DEFAULT="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
DEBUG_FILE="${CTX_DIR}/debug_gemini_output.txt"

usage () {
    echo "Kullanım: $0 <module_name> [--debug]"
    exit 1
}

[[ $# -ge 1 ]] || usage
MODULE="$1"

print_status "Proje hazırlanıyor: ${MODULE}"
OUT_DIR="${CTX_DIR}/outputs/${MODULE}"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
USER_PROMPT_FILE="${PROMPTS_DIR}/${MODULE}_user.txt"
[[ -f "$USER_PROMPT_FILE" ]] || { echo "❌ Prompt dosyası bulunamadı: $USER_PROMPT_FILE"; exit 2; }

# API Key yükleme
if [[ -z "${GEMINI_API_KEY:-}" ]]; then
    if [[ -f "$ENV_FILE" ]]; then
        export GEMINI_API_KEY="$(grep -E '^GEMINI_API_KEY=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"\r')"
    fi
fi
API_KEY="${GEMINI_API_KEY:-}"
[[ -n "$API_KEY" ]] || { echo "❌ GEMINI_API_KEY bulunamadı."; exit 3; }
ENDPOINT="${GEMINI_ENDPOINT:-$GEMINI_ENDPOINT_DEFAULT}"

print_status "Context dosyaları okunuyor ve Ana Plan oluşturuluyor..."

# DİKKAT: Tüm context'ler tek bir metin bloğunda birleştiriliyor.
MASTER_PROMPT=$(cat <<EOF
SENİN GÖREVİN:
Aşağıdaki anayasa ve iş emrine göre tam bir Django backend ve React frontend modülü oluştur.
Çıktın SADECE istenen dosya yapısı olmalı. Her dosyanın içeriği ###dosya/yolu.uzantı### ve ###END_OF_FILE### işaretçileri arasında olmalıdır.
Başka HİÇBİR açıklama veya metin ekleme.

--- ANAYASA 1: BACKEND KURALLARI ---
$(cat "$BACKEND_CTX")

--- ANAYASA 2: FRONTEND KURALLARI ---
$(cat "$FRONTEND_CTX")

--- İŞ EMRİ: KULLANICI İSTEKLERİ ---
$(cat "$USER_PROMPT_FILE")
EOF
)

REQUEST_BODY=$(jq -n \
    --arg prompt "$MASTER_PROMPT" \
    '{
      "contents":[{"role":"user","parts":[{"text": $prompt}]}],
      "generationConfig": {"temperature": 0.2, "topK": 40, "topP": 0.95, "maxOutputTokens": 8192}
    }')

print_status "🤖 Gemini'ye istek gönderiliyor..."
RAW_RESPONSE_JSON=$(curl --connect-timeout 60 --max-time 300 -s -X POST -H "Content-Type: application/json" -d "$REQUEST_BODY" "${ENDPOINT}?key=${API_KEY}")

echo "$RAW_RESPONSE_JSON" > "$DEBUG_FILE"

if jq -e '.error' >/dev/null <<< "$RAW_RESPONSE_JSON"; then
    echo -e "\n❌ Gemini API Hatası Aldı! Üretim durduruldu." >&2
    echo "Detaylar için hata kaydına bakınız: $DEBUG_FILE" >&2
    jq . < "$DEBUG_FILE" >&2
    exit 10
fi

GENERATED_TEXT=$(echo "$RAW_RESPONSE_JSON" | jq -r '.candidates[0].content.parts[0].text' 2>/dev/null)

if [[ -z "$GENERATED_TEXT" || "$GENERATED_TEXT" == "null" ]]; then
    echo -e "\n❌ Gemini'den boş yanıt alındı!" >&2
    echo "Detaylar için hata kaydına bakınız: $DEBUG_FILE" >&2
    jq . < "$DEBUG_FILE" >&2
    exit 11
fi

print_status "✅ Gemini yanıtı başarılı. Proje iskeleti oluşturuluyor..."
create_files_from_text "$GENERATED_TEXT"
print_status "✅ Tüm aşamalar tamamlandı. Proje iskeleti başarıyla oluşturuldu: $OUT_DIR"