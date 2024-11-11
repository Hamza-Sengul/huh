# chat/views.py
from django.shortcuts import render
from django.http import JsonResponse
import openai
from django.conf import settings
import fitz  # PyMuPDF

# OpenAI API anahtarını ayarla
openai.api_key = settings.OPENAI_API_KEY

def pdf_to_text(pdf_path):
    """PDF'den metin çıkarma fonksiyonu."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def chatbot_response(request):
    """Sadece metin mesajlarını işleyen view."""
    if request.method == "POST":
        user_message = request.POST.get("message", "")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # veya "gpt-4" modelini kullanabilirsiniz
                messages=[{"role": "user", "content": user_message}]
            )
            bot_reply = response.choices[0].message.content
            return JsonResponse({"reply": bot_reply})
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return JsonResponse({"reply": "Sorry, there was an error processing your request."}, status=500)
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def chatbot_pdf_response(request):
    """PDF dosyasını işleyen ve API'ye gönderen view."""
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]

        # PDF dosyasını geçici bir dosyaya kaydet
        with open("temp_pdf.pdf", "wb") as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        # PDF'den metin çıkar
        pdf_text = pdf_to_text("temp_pdf.pdf")

        # Metni OpenAI API'ye gönder
        try:
            response = openai.Completion.create(
                model="gpt-4",
                prompt=pdf_text[:2000],  # Çok uzun metinleri kırpın
                max_tokens=150
            )
            bot_reply = response.choices[0].text.strip()
            return JsonResponse({"reply": bot_reply})
        except Exception as e:
            print("OpenAI API Error:", e)
            return JsonResponse({"reply": "Bir hata oluştu."}, status=500)
    
    return JsonResponse({"error": "PDF dosyası yüklenmedi."}, status=400)

def chatbot_pdf_text_response(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")
        pdf_text = ""

        if request.FILES.get("pdf_file"):
            pdf_file = request.FILES["pdf_file"]

            # PDF dosyasını geçici bir dosyaya kaydedin ve işleyin
            try:
                with open("temp_pdf.pdf", "wb") as f:
                    for chunk in pdf_file.chunks():
                        f.write(chunk)

                # PDF'den metin çıkar
                pdf_text = pdf_to_text("temp_pdf.pdf")
            except Exception as e:
                print("PDF İşleme Hatası:", e)
                return JsonResponse({"reply": "PDF dosyası işlenirken bir hata oluştu."}, status=500)

        # API'ye gönderilecek birleşik içerik oluşturun
        combined_prompt = f"{user_message}\n\n{pdf_text[:2000]}"  # Çok uzun metinleri kısaltın

        # OpenAI API çağrısı yapın
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # veya "gpt-4"
                messages=[{"role": "user", "content": combined_prompt}]
            )
            bot_reply = response.choices[0].message.content
            return JsonResponse({"reply": bot_reply})
        except Exception as e:
            print("OpenAI API Hatası:", e)
            return JsonResponse({"reply": "GPT yanıtı alınırken bir hata oluştu."}, status=500)
    
    return JsonResponse({"error": "Geçersiz istek."}, status=400)


def chatbot_page(request):
    """Ana sayfa view'i."""
    return render(request, "index.html")
