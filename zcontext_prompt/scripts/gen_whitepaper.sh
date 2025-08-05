#!/usr/bin/env bash
# path: /var/www/sapb1reportsv2/zcontext_prompt/scripts/gen_whitepaper.sh
# =============================================================================
# SAPB1ReportsV2 – zcontext_prompt – gen_whitepaper.sh v1.1 (Hata Düzeltme)
# =============================================================================
# - Modül isimlendirmesinde büyük/küçük harf tutarlılığı sağlandı.
# =============================================================================

set -euo pipefail

# Stil sahibi durum mesajları için yardımcı fonksiyon
print_status() {
    local color_green='\033[0;32m'
    local color_yellow='\033[1;33m'
    local color_blue='\033[0;34m'
    local color_nc='\033[0m' # No Color
    echo -e "\n${color_yellow}==>${color_nc} ${color_blue}$1${color_nc}"
}

# ---------- Ana Betik Başlangıcı ---------------------------------------------
# ... (Başlangıç ve değişken tanımlamaları aynı) ...
CTX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(dirname "$CTX_DIR")"
ENV_FILE="$PROJECT_ROOT/backend/.env"
PROMPTS_DIR="${CTX_DIR}/prompts"
OUTPUTS_DIR="${CTX_DIR}/outputs"
WHITEPAPER_TEMPLATE="${CTX_DIR}/whitepaper_api.md"
GEMINI_ENDPOINT_DEFAULT="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
DEBUG_FILE_WP="${CTX_DIR}/debug_gemini_whitepaper_output.txt"

usage () {
    echo "Kullanım: $0 <module_name>"
    echo "Örnek: $0 formforgeapi"
    exit 1
}

[[ $# -ge 1 ]] || usage
MODULE_INPUT="$1"
# DÜZELTME: Girdi ne olursa olsun, standart olarak küçük harfli versiyonu kullan.
MODULE_LOWER=$(echo "$MODULE_INPUT" | tr '[:upper:]' '[:lower:]')
MODULE_OUTPUT_DIR="${OUTPUTS_DIR}/${MODULE_LOWER}"
FINAL_WHITEPAPER_PATH="${MODULE_OUTPUT_DIR}/whitepaper.md"

print_status "White Paper üretimi başlatılıyor: ${MODULE_LOWER}"

# --- Gerekli Dosyaların Varlığını Kontrol Et ---
# DÜZELTME: Prompt dosyasını büyük harfle ararken, diğer tüm yollarda küçük harfli versiyonu kullan.
USER_PROMPT_FILE="${PROMPTS_DIR}/${MODULE_INPUT}_user.txt"
MODELS_FILE="${MODULE_OUTPUT_DIR}/backend/${MODULE_LOWER}/models/${MODULE_LOWER}.py"
VIEWS_FILE="${MODULE_OUTPUT_DIR}/backend/${MODULE_LOWER}/api/views.py"
URLS_FILE="${MODULE_OUTPUT_DIR}/backend/${MODULE_LOWER}/api/urls.py"
TASKS_FILE="${MODULE_OUTPUT_DIR}/backend/${MODULE_LOWER}/tasks/${MODULE_LOWER}_tasks.py"

[[ -f "$USER_PROMPT_FILE" ]] || { echo "❌ İş Emri dosyası bulunamadı: $USER_PROMPT_FILE"; exit 2; }
[[ -f "$MODELS_FILE" ]] || { echo "❌ Model dosyası bulunamadı: $MODELS_FILE"; exit 2; }
[[ -f "$VIEWS_FILE" ]] || { echo "❌ View dosyası bulunamadı: $VIEWS_FILE"; exit 2; }
[[ -f "$URLS_FILE" ]] || { echo "❌ URL dosyası bulunamadı: $URLS_FILE"; exit 2; }
[[ -f "$WHITEPAPER_TEMPLATE" ]] || { echo "❌ White Paper şablonu bulunamadı: $WHITEPAPER_TEMPLATE"; exit 2; }

# ... (API Key yükleme ve Master Prompt oluşturma aynı) ...
if [[ -z "${GEMINI_API_KEY:-}" ]]; then
    if [[ -f "$ENV_FILE" ]]; then
        export GEMINI_API_KEY="$(grep -E '^GEMINI_API_KEY=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"\r')"
    fi
fi
API_KEY="${GEMINI_API_KEY:-}"
[[ -n "$API_KEY" ]] || { echo "❌ GEMINI_API_KEY bulunamadı."; exit 3; }
ENDPOINT="${GEMINI_ENDPOINT:-$GEMINI_ENDPOINT_DEFAULT}"

print_status "Referans materyaller okunuyor ve dokümantasyon planı oluşturuluyor..."
CELERY_TASKS_CONTENT="Bu modülde özel bir Celery görevi bulunmamaktadır."
if [[ -f "$TASKS_FILE" ]]; then
    CELERY_TASKS_CONTENT=$(cat "$TASKS_FILE")
fi

MASTER_PROMPT=$(cat <<EOF
SENİN GÖREVİN:
Aşağıdaki referans materyalleri (iş gereksinimleri, şablon ve üretilmiş Python kodu) kullanarak, "WHITE PAPER ŞABLONU" bölümünü eksiksiz bir şekilde doldurmak. Çıktın, SADECE ve SADECE doldurulmuş markdown metni olmalıdır. Başka hiçbir açıklama, kod bloğu veya ayraç ekleme. Tarih alanlarını doldururken bugünün tarihini kullan: $(date +'%Y-%m-%d').
--- BÖLÜM 1: WHITE PAPER ŞABLONU (BUNU DOLDUR) ---
$(cat "$WHITEPAPER_TEMPLATE")
--- BÖLÜM 2: REFERANS MATERYALLER (BUNLARI KULLAN) ---
REFERANS 2.1: İŞ GEREKSİNİMLERİ VE META BİLGİLER (Kullanıcı Prompt'u)
$(cat "$USER_PROMPT_FILE")
REFERANS 2.2: ÜRETİLEN KOD - DJANGO MODELLERİ (models.py)
\`\`\`python
$(cat "$MODELS_FILE")
\`\`\`
REFERANS 2.3: ÜRETİLEN KOD - API ENDPOINT'LERİ (views.py ve urls.py)
\`\`\`python
# views.py
$(cat "$VIEWS_FILE")
# urls.py
$(cat "$URLS_FILE")
\`\`\`
REFERANS 2.4: ÜRETİLEN KOD - ZAMANLANMIŞ GÖREVLER (tasks.py)
\`\`\`python
${CELERY_TASKS_CONTENT}
\`\`\`
EOF
)

REQUEST_BODY=$(jq -n --arg prompt "$MASTER_PROMPT" '{"contents":[{"role":"user","parts":[{"text": $prompt}]}],"generationConfig": {"temperature": 0.1, "topK": 40, "topP": 0.95, "maxOutputTokens": 4096}}')

print_status "🤖 Gemini'ye dokümantasyon isteği gönderiliyor..."
RAW_RESPONSE_JSON=$(curl --connect-timeout 60 --max-time 180 -s -X POST -H "Content-Type: application/json" -d "$REQUEST_BODY" "${ENDPOINT}?key=${API_KEY}")

echo "$RAW_RESPONSE_JSON" > "$DEBUG_FILE_WP"

if jq -e '.error' >/dev/null <<< "$RAW_RESPONSE_JSON"; then
    echo -e "\n❌ Gemini API Hatası Aldı! Üretim durduruldu." >&2; jq . < "$DEBUG_FILE_WP" >&2; exit 10;
fi

GENERATED_TEXT=$(echo "$RAW_RESPONSE_JSON" | jq -r '.candidates[0].content.parts[0].text' 2>/dev/null | sed "s/^[\`']\{3\}markdown//; s/[\`']\{3\}$//")

if [[ -z "$GENERATED_TEXT" || "$GENERATED_TEXT" == "null" ]]; then
    echo -e "\n❌ Gemini'den boş yanıt alındı!" >&2; jq . < "$DEBUG_FILE_WP" >&2; exit 11;
fi

print_status "✅ Gemini yanıtı başarılı. White Paper dosyası oluşturuluyor..."
echo "$GENERATED_TEXT" > "$FINAL_WHITEPAPER_PATH"
print_status "✅ Tüm aşamalar tamamlandı. White Paper başarıyla oluşturuldu: $FINAL_WHITEPAPER_PATH"