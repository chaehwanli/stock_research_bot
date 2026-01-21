import os
import shutil
import git
from datetime import datetime
from urllib.parse import quote

class WikiPublisher:
    def __init__(self, repo_url=None):
        self.repo_url = repo_url
        if not self.repo_url:
            self.repo_url = os.getenv("WIKI_REPO_URL")
            
        # Inject Credentials if available and URL is HTTPS
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_username = os.getenv("GITHUB_USERNAME")
        self.github_password = os.getenv("GITHUB_PASSWORD")
        
        if self.repo_url and self.repo_url.startswith("https://github.com"):
            url_no_protocol = self.repo_url.replace("https://", "")
            
        if self.repo_url and self.repo_url.startswith("https://github.com"):
            url_no_protocol = self.repo_url.replace("https://", "")
            
            if self.github_token:
                # Use Token (Prioritized)
                safe_token = quote(self.github_token, safe='')
                self.authed_repo_url = f"https://{safe_token}@{url_no_protocol}"
            elif self.github_username and self.github_password:
                # Use Username/Password
                safe_user = quote(self.github_username, safe='')
                safe_pass = quote(self.github_password, safe='')
                self.authed_repo_url = f"https://{safe_user}:{safe_pass}@{url_no_protocol}"
            else:
                self.authed_repo_url = self.repo_url
        else:
            self.authed_repo_url = self.repo_url
        
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
                
                # Construct Public URL
                # Repo URL: https://github.com/user/repo.wiki.git -> Public: https://github.com/user/repo/wiki/Page_Title
                public_url = ""
                if self.repo_url and "github.com" in self.repo_url:
                    base_url = self.repo_url.replace(".wiki.git", "/wiki").replace(".git", "/wiki")
                    # GitHub Wiki URLs usually use hyphens for spaces, but if we saved as filename with underscores...
                    # If we write "Page_Title.md", the URL is ".../wiki/Page_Title"
                    page_url_segment = page_title.replace(' ', '_')
                    public_url = f"{base_url}/{page_url_segment}"
                
                return public_url if public_url else True
            else:
                print("No changes to publish.")
                # Still try to construct URL as the page exists
                public_url = ""
                if self.repo_url and "github.com" in self.repo_url:
                    base_url = self.repo_url.replace(".wiki.git", "/wiki").replace(".git", "/wiki")
                    page_url_segment = page_title.replace(' ', '_')
                    public_url = f"{base_url}/{page_url_segment}"
                return public_url if public_url else True

        except Exception as e:
            print(f"Failed to publish to Wiki: {e}")
            return False

    def _get_repo(self):
        if os.path.exists(self.local_path):
            try:
                repo = git.Repo(self.local_path)
                # Pull latest
                origin = repo.remotes.origin
                
                # Update remote URL if token changed or needed
                if self.authed_repo_url and origin.url != self.authed_repo_url:
                    print("Updating remote URL with new credentials...")
                    origin.set_url(self.authed_repo_url)
                    
                origin.pull()
                return repo
            except Exception as e:
                print(f"Error loading local repo: {e}. Re-cloning...")
                # If invalid repo, remove and re-clone
                if os.path.exists(self.local_path):
                    shutil.rmtree(self.local_path)
        
        print(f"Cloning Wiki from {self.repo_url}...")
        # Use authed URL for cloning/pushing
        return git.Repo.clone_from(self.authed_repo_url, self.local_path)
