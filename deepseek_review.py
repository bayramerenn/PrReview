import os
import requests
from github import Github

# Konfigürasyon
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GITHUB_TOKEN = os.getenv("PRTOKEN")

# PR Bilgilerini Al
github = Github(GITHUB_TOKEN)
repo = github.get_repo(os.getenv("GITHUB_REPOSITORY"))
pr = repo.get_pull(int(os.getenv("GITHUB_REF").split("/")[-2]))

# Diff'i Topla
diff_content = ""
for file in pr.get_files():
    diff_content += f"\n\n--- {file.filename} ---\n{file.patch}"

# DeepSeek API'yi Çağır
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {
            "role": "system",
            "content": """Sen bir kod inceleme uzmanısın. PR diff'ini şu kurallara göre analiz et:
            1. Dil stil rehberine uygunluk (Python: PEP8, JS: ES6)
            2. Güvenlik açıkları
            3. Projeye özel kurallar"""
        },
        {
            "role": "user",
            "content": f"Şu kod değişikliklerini incele:\n{diff_content[:3000]}"  # Token limiti için kırp
        }
    ]
}

response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers=headers,
    json=data
)

# Sonuçları İşle
if response.status_code == 200:
    review_comment = response.json()["choices"][0]["message"]["content"]
    pr.create_issue_comment(f"🔍 **DeepSeek Review**:\n\n{review_comment}")
else:
    print("Hata:", response.text)