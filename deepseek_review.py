import os
import requests
from github import Github

# Konfigürasyon
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Debug
print("GITHUB_REPOSITORY:", os.getenv("GITHUB_REPOSITORY"))

# GitHub Bağlantısı
try:
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(os.getenv("GITHUB_REPOSITORY"))
    pr_number = int(os.getenv("GITHUB_REF").split("/")[-2])
    pr = repo.get_pull(pr_number)
except Exception as e:
    print("GitHub Hatası:", str(e))
    exit(1)

# Diff'i Topla
diff_content = ""
try:
    for file in pr.get_files():
        diff_content += f"\n\n--- {file.filename} ---\n{file.patch}"
except Exception as e:
    print("Diff Alınamadı:", str(e))
    exit(1)

# DeepSeek API
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {
            "role": "system",
            "content": "Kod incelemesi yap. Hataları ve iyileştirmeleri belirt."
        },
        {
            "role": "user", 
            "content": f"Şu PR diff'ini incele:\n{diff_content[:3000]}"
        }
    ]
}

try:
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    review_comment = response.json()["choices"][0]["message"]["content"]
    pr.create_issue_comment(f"🔍 **DeepSeek Review**:\n\n{review_comment}")
except Exception as e:
    print("DeepSeek API Hatası:", str(e))
    exit(1)