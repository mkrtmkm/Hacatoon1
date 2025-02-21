import re
from collections import Counter
import git
import os
from typing import Dict, Set

class TextAnalyzer:
    def __init__(self, repo_path: str, file_path: str = "document.txt"):
        self.repo_path = repo_path
        self.file_path = file_path
        self.repo = git.Repo(repo_path)

    def get_file_content(self, commit: str) -> str:
        try:
            return self.repo.git.show(f"{commit}:{self.file_path}")
        except git.exc.GitCommandError:
            return ""

    def process_text(self, text: str) -> Dict[str, int]:
        words = re.findall(r'\b\w+\b', text.lower())
        return dict(Counter(words))

    def get_word_stats(self, word_freq: Dict[str, int]) -> dict:
        if not word_freq:
            return {}

        total_unique = len(word_freq)
        most_common = max(word_freq.items(), key=lambda x: x[1])
        least_common = min(word_freq.items(), key=lambda x: x[1])

        return {
            "total_unique": total_unique,
            "most_common": (most_common[0], most_common[1]),
            "least_common": (least_common[0], least_common[1])
        }

    def compare_commits(self, commit1: str, commit2: str) -> dict:
        text1 = self.get_file_content(commit1)
        text2 = self.get_file_content(commit2)

        words1 = set(self.process_text(text1).keys())
        words2 = set(self.process_text(text2).keys())

        added = words2 - words1
        removed = words1 - words2

        return {
            "added_words": added,
            "removed_words": removed,
            "added_count": len(added),
            "removed_count": len(removed)
        }

    def analyze_latest_version(self) -> dict:
        latest_commit = self.repo.head.commit.hexsha
        text = self.get_file_content(latest_commit)
        word_freq = self.process_text(text)
        stats = self.get_word_stats(word_freq)

        return {
            "word_frequency": word_freq,
            "statistics": stats,
            "commit": latest_commit
        }

def main():
    try:
        analyzer = TextAnalyzer("./")
        latest_analysis = analyzer.analyze_latest_version()
        print("Аналіз останньої версії:")
        print(f"Коміт: {latest_analysis['commit']}")
        print(f"Загальна кількість унікальних слів: {latest_analysis['statistics']['total_unique']}")
        print(f"Найчастіше слово: {latest_analysis['statistics']['most_common']}")
        print(f"Найрідше слово: {latest_analysis['statistics']['least_common']}")
        print("\nЧастота слів:")
        for word, freq in latest_analysis['word_frequency'].items():
            print(f"{word}: {freq}")

        commits = list(analyzer.repo.iter_commits(paths=analyzer.file_path))
        if len(commits) >= 2:
            print("\nПорівняння між останніми двома комітами:")
            comparison = analyzer.compare_commits(commits[1].hexsha, commits[0].hexsha)
            print(f"Додані слова ({comparison['added_count']}): {comparison['added_words']}")
            print(f"Видалені слова ({comparison['removed_count']}): {comparison['removed_words']}")

    except Exception as e:
        print(f"Помилка: {str(e)}")

if __name__ == "__main__":
    main()