# BIST Sinyal Botu

## Neden forex botundan farklı çalışıyor?

Forex botunda MetaTrader 5 hem veriyi çekiyor hem de emri otomatik gönderiyordu.
BIST tarafında bu mümkün değil, çünkü:

- **MetaTrader 5, Türkiye'de doğrudan BIST hisse senedi alım-satımını
  desteklemiyor** (sadece VİOP — vadeli işlemler — bazı kurumlarda MT5
  üzerinden yapılabiliyor, o da ayrı bir ürün).
- **Algolab** (Deniz Yatırım'ın ücretsiz BIST algoritmik işlem API'si,
  bu alanda bilinen tek ciddi seçenekti) **31.12.2025 itibarıyla kapandı.**
  Şu an bireysel yatırımcının ücretsiz/uygun fiyatlı kullanabileceği bir
  BIST otomatik emir API'si yok.

Bu yüzden bot **otomatik emir göndermez, sinyal üretir.** Aynı trend+momentum
mantığıyla BIST hisselerini izler, bir fırsat gördüğünde seni bilgilendirir;
işlemi sen kendi aracı kurumunun uygulamasından (Midas, İş Yatırım, Gedik,
N Kolay, hangisini kullanıyorsan) manuel olarak yaparsın. Bunun avantajı:
minimum tutar sınırı da ortadan kalkıyor — bir payın fiyatı kadar bütçeyle
başlayabilirsin.

## Strateji mantığı

| Katman | Zaman dilimi | Ne yapar |
|---|---|---|
| Trend filtresi | Günlük | EMA50 vs EMA200 → sadece YÜKSELEN trend aranır |
| Giriş sinyali | Saatlik | EMA9/EMA21 yukarı kesişimi + RSI(14) filtresi |
| Bilgi amaçlı seviyeler | Saatlik | ATR(14) tabanlı stop (1.5x) ve hedef (2.75x) |

**Sadece AL sinyali üretir, satış/açığa satış sinyali vermez** — çünkü BIST'te
açığa satış küçük bütçeli bireysel yatırımcılar için genelde erişilebilir
değil (ek sözleşme, ek teminat gerektiriyor). Günlük trend düşüşteyse bot
o hisse için sessiz kalır, "bu hissede şu an fırsat yok" demiş olur.

## Kurulum — Android (önerilen yöntem: GitHub Actions + Telegram)

Telefon Python çalıştıramadığı için bot **bulutta, ücretsiz** çalışır;
telefonun tek işi Telegram bildirimini almak. Kurulum tek seferlik:

1. **GitHub hesabı aç** (yoksa) — telefon tarayıcısından veya GitHub'ın
   Android uygulamasından yapılabilir.
2. **Yeni bir private repo oluştur** (örn. `bist-sinyal-botu`) ve bu
   klasördeki tüm dosyaları oraya yükle. (Bilgisayarın yoksa: GitHub'ın
   web arayüzünde "Add file → Upload files" ile telefondan bile dosyaları
   tek tek sürükleyip yükleyebilirsin.)
3. **Telegram botu oluştur:**
   - Telegram'da **@BotFather**'a yaz, `/newbot` komutuyla bot oluştur,
     sana bir **token** verecek.
   - Botunla bir kere mesajlaş (herhangi bir şey yaz).
   - **@userinfobot**'a yazıp kendi **chat_id**'ni öğren.
4. Repo'da **Settings → Secrets and variables → Actions → New repository
   secret** ile iki secret ekle:
   - `TELEGRAM_BOT_TOKEN` → BotFather'ın verdiği token
   - `TELEGRAM_CHAT_ID` → kendi chat_id'n
5. Repo'da **Actions** sekmesine gir, workflow'u onayla/etkinleştir.
   Artık BIST işlem saatlerinde (10:00-18:00, hafta içi) her saat başı
   otomatik çalışıp sinyal varsa Telegram'a bildirim atacak — telefon
   kapalı bile olsa çalışır, açtığında bildirimi görürsün.
6. Elle test etmek istersen: **Actions → BIST Sinyal Botu → Run workflow**
   butonuna basman yeterli (bunu GitHub'ın Android uygulamasından da
   yapabilirsin).

Bu yöntemde broker hesabı/API anahtarı gerekmez, tamamen ücretsiz veri
kullanılır (yfinance/Yahoo Finance) — **0 TL** ile başlayabilirsin.

## Alternatif: Termux ile telefonun üzerinde çalıştırmak

GitHub'a hiç bulaşmadan doğrudan telefonda çalıştırmak istersen:

1. **Termux**'u Play Store'dan değil, [F-Droid](https://f-droid.org/) ya da
   GitHub üzerinden kur (Play Store sürümü güncellenmiyor, sorun çıkarabilir).
2. Termux'ta:
   ```
   pkg update && pkg upgrade
   pkg install python
   pip install -r requirements.txt
   ```
   (numpy/pandas kurulumu telefonda biraz uzun sürebilir, sabırlı ol.)
3. Sürekli döngüde çalıştırmak için: `RUN_ONCE=false python watcher.py`

**Dezafyanı bil:** Android, arka planda uzun süre açık kalan uygulamaları
pil tasarrufu için kapatabilir — Termux'a pil optimizasyonundan muafiyet
vermen gerekir, yine de %100 garantili değildir. Bu yüzden 7/24 çalışması
gereken bir şey için GitHub Actions yöntemi daha güvenilir; Termux'u daha
çok "elimle açıp kontrol edeyim" tarzı kullanım için düşün.

## Sinyal geldiğinde ne olur?

Konsola yazdırır, `signals_log.csv` dosyasına kaydeder, ve (açarsan) Telegram'a
bildirim gönderir:

```
[THYAO.IS] AL sinyali
Fiyat: 285.40 TL
Stop: 274.10 TL | Hedef: 316.90 TL
Onerilen adet (bilgi amacli, 5000 TL butceye gore): 17
```

Buradaki "önerilen adet" tamamen bilgi amaçlıdır, senin girdiğin
`config.py > BUDGET_TRY` değerine ve %1 risk kuralına göre hesaplanır.
**Hiçbir emir otomatik gönderilmez** — gördüğün fiyat/stop/hedef seviyelerini
kendi uygulamandan manuel giriyorsun.

## Ayarlar (`config.py`)

- `WATCHLIST`: takip edilecek hisseler (yfinance formatı, `.IS` eki ile).
- `BUDGET_TRY`: yaklaşık bütçen — kendi durumuna göre güncelle.
- `RISK_PER_TRADE_PCT`: işlem başına risk edilecek yüzde (varsayılan %1).

## Telegram bildirimi (opsiyonel)

1. Telegram'da **@BotFather** ile konuşup yeni bir bot oluştur, sana bir
   **token** verecek.
2. Oluşturduğun botla bir kere mesajlaş, sonra **@userinfobot** ile kendi
   **chat_id**'ni öğren.
3. `config.py` içinde `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` doldur,
   `USE_TELEGRAM = True` yap.

## Varant (warrant) hakkında not

Yahoo Finance / yfinance, BIST'te işlem gören varantların fiyat verisini
sağlamıyor — bu yüzden bot doğrudan varant fiyatlarını izleyemiyor. Pratik
çözüm: bot sana bir hissede (örn. THYAO) AL sinyali verdiğinde, o hisseye
dayalı varantı kendi aracı kurumunun varant ekranından sen seçip
işlem yapabilirsin. Varantın kendi kaldıracı olduğu için pozisyon
büyüklüğü/riski hisseden farklı hesaplanır — küçük tutarlarla dikkatli ol.

## Önerilen yol haritası

1. Botu birkaç hafta **sadece izle** (sinyalleri gözlemle, henüz işlem açma).
2. Sinyallerin mantıklı görünüp görünmediğini kendi bildiğin hisselerle
   karşılaştır.
3. Küçük, kaybetmeyi göze alabileceğin bir tutarla ilk birkaç sinyali
   manuel uygula, sonuçları `signals_log.csv`'den takip et.
4. İleride bir aracı kurumdan ücretli/kurumsal bir algo-trading API'sine
   erişimin olursa (ya da VİOP tarafında MT5 destekleyen NCM/NoorCM gibi
   bir kurumla çalışmak istersen), otomatik emir gönderme kısmını o zaman
   ekleyebiliriz.

## Sınırlamalar

- Kâr garantisi yoktur.
- Yahoo Finance verisi birkaç dakika gecikmeli olabilir, saniyelik
  scalping için uygun değildir — günlük/saatlik strateji için yeterlidir.
- BIST işlem saatleri (10:00-18:00 civarı) dışında bot bekleme modunda kalır.
