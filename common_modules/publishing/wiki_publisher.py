import os
import shutil
import git
from datetime import datetime

class WikiPublisher:
    def __init__(self, repo_url=None):
        self.repo_url = repo_url
        if not self.repo_url:
            self.repo_url = os.getenv("WIKI_REPO_URL")
        
        # Local path to clone wiki
        self.local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../wiki_repo"))

    def publish_report(self, report_content, page_title):
        if not self.repo_url:
            print("Wiki Repo URL not configured. Skipping publication.")
            return False

        try:
            repo = self._get_repo()
            
            # Create filename from title
            filename = f"{page_title.replace(' ', '_')}.md"
            file_path = os.path.join(self.local_path, filename)
            
            # Write content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            
            # Update Home/Sidebar if needed (Optional, skipping for MVP)
            
            # Commit and Push
            if repo.is_dirty(untracked_files=True):
                repo.index.add([filename])
                repo.index.commit(f"Add report: {page_title}")
                original_remote = repo.remote(name='origin')
                original_remote.push()
                print(f"Successfully published to Wiki: {page_title}")
                return True
            else:
                print("No changes to publish.")
                return True

        except Exception as e:
            print(f"Failed to publish to Wiki: {e}")
            return False

    def _get_repo(self):
        if os.path.exists(self.local_path):
            try:
                repo = git.Repo(self.local_path)
                # Pull latest
                repo.remotes.origin.pull()
                return repo
            except:
                # If invalid repo, remove and re-clone
                shutil.rmtree(self.local_path)
        
        print(f"Cloning Wiki from {self.repo_url}...")
        return git.Repo.clone_from(self.repo_url, self.local_path)
