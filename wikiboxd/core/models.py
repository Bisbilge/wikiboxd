from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Makale (Article) Modeli: Kullanıcıların okuyup puanlayacağı makaleleri temsil eder.
class Article(models.Model):
    # Makalenin başlığı. En fazla 255 karakter alabilir.
    title = models.CharField(max_length=255)
    
    # Makalenin asıl metni. Sınır yoktur, uzun metinler için kullanılır.
    content = models.TextField()
    
    # Makaleyi yazan kullanıcı (Yazar). Django'nun yerleşik User tablosuna bağlanır.
    # on_delete=models.SET_NULL: Kullanıcı silinirse makale silinmez, yazar kısmı boş (null) kalır.
    # null=True: Veritabanında yazar kısmı boş bırakılabilir izni verir.
    # related_name='articles': Bir kullanıcının makalelerini 'user.articles.all()' ile çekmemizi sağlar.
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    
    # Makalenin oluşturulduğu anın tarih ve saatini otomatik kaydeder (sadece ilk eklendiğinde çalışır).
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Makale her güncellendiğinde (kaydedildiğinde) tarihi otomatik olarak o ana günceller.
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Admin panelinde makalenin adının (başlığının) düzgün görünmesini sağlar.
        return self.title

# Puanlama (Rating) Modeli: Kullanıcıların makalelere verdiği puanları ve yorumları tutar.
class Rating(models.Model):
    # Puanı veren kullanıcı. 
    # on_delete=models.CASCADE: Kullanıcı silinirse, verdiği tüm puanlar da veritabanından silinir.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    
    # Puan verilen makale. 
    # on_delete=models.CASCADE: Makale silinirse, ona verilen puanlar da otomatik silinir.
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    
    # Kullanıcının verdiği puan (1 ile 10 arasında sınırlandırılmıştır). 
    # Validators ile 1'den küçük, 10'dan büyük bir sayı girilmesi engellenir.
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Kullanıcının makale hakkındaki isteğe bağlı inceleme metni. 
    # null=True, blank=True: Bu alanın hem veritabanında hem de formlarda boş bırakılabileceği anlamına gelir.
    review_text = models.TextField(null=True, blank=True)
    
    # Puanın/yorumun girildiği anın tarih ve saati.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ÖNEMLİ KISITLAMA: Bir kullanıcının aynı makaleye sadece BİR KERE puan verebilmesini sağlar.
        # Aynı kullanıcı aynı makaleye ikinci kez puan vermeye çalışırsa veritabanı hata döndürür.
        unique_together = ('user', 'article')

    def __str__(self):
        # Admin panelinde puanları listelerken "Kullanıcı Adı - Makale Başlığı - Puan" formatında okunaklı sunar.
        return f"{self.user.username} - {self.article.title} - {self.score}"