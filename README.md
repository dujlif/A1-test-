# BIST Sinyal Botu

## Bu bot ne yapar, ne yapmaz

- **Ne yapar:** Kural tabanlı bir sinyal sistemi. Teknik analiz + (deneysel)
  haber taraması + (deneysel) analist/banka önerisi taraması birleştirip
  "AL sinyali" üretir. Her işlemde bilgi amaçlı stop/hedef ve önerilen
  pay adedi hesaplar.
- **Ne yapmaz:** Kâr garanti ETMEZ, otomatik emir GÖNDERMEZ. Sinyal
  üretir, işlemi sen kendi aracı kurumunun uygulamasından manuel yaparsın.

## Neden otomatik emir göndermiyor?

- **MetaTrader 5, Türkiye'de BIST hisse senedi alım-satımını desteklemiyor**
  (sadece VİOP — vadeli işlemler — bazı kurumlarda destekleniyor, o ayrı
  bir ürün).
- **Algolab** (Deniz Yatırım'ın ücretsiz BIST algoritmik işlem API'si)
  **31.12.2025 itibarıyla kapandı.** Şu an bireysel yatırımcının
  ücretsiz/uygun fiyatlı kullanabileceği bir BIST otomatik emir API'si yok.

Bunun avantajı: minimum tutar sınırı da yok — bir payın fiyatı kadar
bütçeyle başlayabilirsin.

## Üç sinyal tipi

| Tip | Kapsam | Kaynak | Güvenilirlik |
|---|---|---|---|
| **AL sinyali (teknik)** | `WATCHLIST` (40 hisse) | EMA20/50 trend + EMA9/21 kesişim + RSI | En güvenilir, kural tabanlı |
| **AL sinyali (haber bazlı)** | `NEWS_COMPANIES` (40 şirket, genişletilebilir) | Google News RSS + anahtar kelime | Deneysel |
| **AL sinyali (analist/banka önerisi)** | `NEWS_COMPANIES` | Google News RSS + banka adı + tavsiye kelimesi | Deneysel |

### Teknik sinyal nasıl çalışıyor

| Katman | Zaman dilimi | Ne yapar |
|---|---|---|
| Trend filtresi | Günlük | EMA20 vs EMA50 → sadece YÜKSELEN trend aranır |
| Giriş sinyali | Saatlik | EMA9/EMA21'in son 3 mum içinde yukarı kesişimi + RSI(35-75) |
| Bilgi amaçlı seviyeler | Saatlik | ATR(14) tabanlı stop (1.5x) ve hedef (2.75x) |

Daha SIK sinyal üretmesi için trend filtresi hızlandırıldı (EMA50/200 yerine
EMA20/50), RSI bandı genişletildi, kesişim son mum yerine son 3 mumda
aranıyor. **Bunun bedeli:** daha fazla sinyal, ama muhtemelen biraz daha
fazla yanlış sinyal de demek. Çok sık geliyorsa `config.py`'de
`RSI_LONG_MIN/MAX` daraltıp `TREND_EMA_SLOW`'u büyüterek sıkılaştırabilirsin;
çok az geliyorsa tam tersini yapabilirsin.

Sadece AL sinyali üretir, satış/açığa satış sinyali vermez — BIST'te açığa
satış küçük bütçeli bireysel yatırımcılar için genelde erişilebilir değil.

### Haber ve analist sinyalleri hakkında önemli not

**Bunlar gerçek bir yapay zeka duygu analizi ya da resmi analist konsensüsü
DEĞİL.** KAP'ın (Kamuyu Aydınlatma Platformu) kendi API'si kurumsal/ücretli
abonelik gerektiriyor, bireysel kullanıcıya kapalı — bu yüzden onu
kullanamadık. Bunun yerine ücretsiz Google News RSS üzerinden başlıkları
tarayıp:
- **Haber sinyali:** başlıkta olumlu görünen kelimeler (rekor, kâr artışı,
  temettü, anlaşma imzaladı vb.) var mı diye basit kelime eşleştirmesi yapar.
- **Analist sinyali:** başlıkta bir banka/aracı kurum adı (İş Yatırım, Ak
  Yatırım vb.) VE bir tavsiye ifadesi (AL tavsiyesi, hedef fiyat yükseltildi
  vb.) birlikte geçiyor mu diye bakar.

İkisi de ironiyi, olumsuzlamayı anlamaz, yanlış pozitif verebilir, kaçırdığı
gerçek haberler/tavsiyeler olabilir. Mesajda hangi başlık(lar) tetiklediğini
görürsün — kararı vermeden önce o başlığı kendin okuman önemli. Ayrı ayrı
etiketlenmelerinin sebebi bu: teknik sinyalle aynı güven seviyesinde değiller.

Kapatmak istersen `config.py` içinde `USE_NEWS_SIGNAL = False` veya
`USE_ANALYST_SIGNAL = False` yap.

## Kurulum — Android (önerilen yöntem: GitHub Actions + Telegram)

Telefon Python çalıştıramadığı için bot **bulutta, ücretsiz** çalışır;
telefonun tek işi Telegram bildirimini almak.

1. **GitHub hesabı aç** (yoksa).
2. **Yeni bir private repo oluştur** ve bu klasördeki tüm dosyaları oraya
   yükle. `.github/workflows/sinyal.yml` dosyasının GERÇEKTEN
   `.github/workflows/` klasörünün İÇİNDE olduğundan emin ol (mobilde
   yüklerken en sık hata bu).
3. **Telegram botu oluştur:**
   - **@BotFather**'a yaz, `/newbot` ile bot oluştur, token al.
   - Botunla bir kere mesajlaş.
   - **@userinfobot**'a yazıp kendi chat_id'ni öğren.
4. Repo → **Settings → Secrets and variables → Actions** → iki secret ekle:
   `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
5. **Actions** sekmesinden workflow'u etkinleştir. Artık BIST işlem
   saatlerinde (10:00-18:00, hafta içi) her saat başı otomatik çalışır.
6. Test için: **Actions → BIST Sinyal Botu → Run workflow** — açılan
   kutuda **force_run**'ı işaretlersen piyasa kapalı olsa bile çalışır.

## Alternatif: Termux

```
pkg update && pkg upgrade
pkg install python
pip install -r requirements.txt
RUN_ONCE=false python watcher.py
```

Android pil optimizasyonu arka planda uzun süre açık kalan işlemleri
kapatabilir — 7/24 güvenilirlik için GitHub Actions yöntemi daha sağlam.

## Ayarlar (`config.py`)

- `WATCHLIST`: teknik sinyal için takip edilen 40 hisse.
- `NEWS_COMPANIES`: haber/analist taraması için şirket adı eşlemesi
  (aynı formatta `"TICKER.IS": "Şirket Adı"` ekleyebilirsin).
- `BUDGET_TRY`, `RISK_PER_TRADE_PCT`: pozisyon büyüklüğü önerisi için.
- `USE_NEWS_SIGNAL`, `USE_ANALYST_SIGNAL`: açma/kapama.

## Önerilen yol haritası

1. Botu birkaç hafta **sadece izle**, henüz işlem açma.
2. Üç sinyal tipini birbirinden ayırt ederek değerlendir — teknik olana
   diğerlerinden daha çok güven.
3. Küçük, kaybetmeyi göze alabileceğin bir tutarla ilk birkaç sinyali
   manuel uygula, sonuçları `signals_log.csv`'den takip et.

## Sınırlamalar

- Kâr garantisi yoktur.
- Yahoo Finance verisi birkaç dakika gecikmeli olabilir.
- Google News RSS gerçek zamanlı değildir, saatler/günler gecikmeli
  haberler de dönebilir.
- BIST işlem saatleri dışında bot bekleme modunda kalır.
