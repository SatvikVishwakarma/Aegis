"""
Aegis Agent Package Builder
Customizes pre-built agent template and creates deployment package
"""
import os
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

class AgentPackageBuilder:
    """Builds customized agent packages from pre-built template"""
    
    def __init__(self, template_dir: str = None):
        """
        Initialize builder with template directory
        
        Args:
            template_dir: Path to agent-template folder (default: ./agent-template)
        """
        if template_dir is None:
            # Default to agent-template in same directory as this script
            script_dir = Path(__file__).parent
            template_dir = script_dir / "agent-template"
        
        self.template_dir = Path(template_dir)
        
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")
        
        # Verify required template files exist
        required_files = [
            "AegisAgent.exe",
            "appsettings.template.json",
            "INSTALL.template.ps1",
            "UNINSTALL.template.ps1",
            "README.template.txt"
        ]
        
        for filename in required_files:
            file_path = self.template_dir / filename
            if not file_path.exists():
                raise FileNotFoundError(f"Required template file not found: {filename}")
    
    def build_package(
        self,
        server_url: str,
        api_key: str,
        group: str,
        output_path: str = None
    ) -> str:
        """
        Build customized agent package
        
        Args:
            server_url: Full URL to server API (e.g., http://192.168.1.100:5000)
            api_key: Agent API key from server
            group: Node group assignment
            output_path: Path for output ZIP file (default: temp file)
        
        Returns:
            Path to generated ZIP file
        """
        # Validate inputs
        if not server_url or not api_key or not group:
            raise ValueError("server_url, api_key, and group are required")
        
        # Parse server URL to extract host and port
        parsed_url = urlparse(server_url)
        server_host = parsed_url.hostname or "unknown"
        server_port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
        
        # Create temporary directory for package assembly
        with tempfile.TemporaryDirectory() as temp_dir:
            package_dir = Path(temp_dir) / "AegisAgent"
            package_dir.mkdir()
            
            # Copy all files from template directory
            self._copy_template_files(package_dir)
            
            # Customize configuration files
            self._customize_appsettings(
                package_dir / "appsettings.json",
                server_url,
                api_key,
                group
            )
            
            self._customize_install_script(
                package_dir / "INSTALL.ps1",
                group,
                server_url
            )
            
            self._customize_readme(
                package_dir / "README.txt",
                server_url,
                server_host,
                server_port,
                group
            )
            
            # Create ZIP file
            if output_path is None:
                # Generate timestamped filename in temp directory
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output_path = Path(tempfile.gettempdir()) / f"AegisAgent-{group}-{timestamp}.zip"
            else:
                output_path = Path(output_path)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create ZIP archive
            self._create_zip(package_dir, output_path)
            
            return str(output_path)
    
    def _copy_template_files(self, dest_dir: Path):
        """Copy all files from template directory to destination"""
        for item in self.template_dir.iterdir():
            # Skip template files (they'll be processed and renamed)
            if item.name.endswith('.template.json') or item.name.endswith('.template.ps1') or item.name.endswith('.template.txt'):
                continue
            
            dest = dest_dir / item.name
            
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest)
    
    def _customize_appsettings(
        self,
        output_file: Path,
        server_url: str,
        api_key: str,
        group: str
    ):
        """Generate appsettings.json from template with user values"""
        template_file = self.template_dir / "appsettings.template.json"
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace placeholders
        content = content.replace('{{SERVER_URL}}', server_url)
        content = content.replace('{{API_KEY}}', api_key)
        content = content.replace('{{GROUP}}', group)
        
        # Write customized configuration
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _customize_install_script(
        self,
        output_file: Path,
        group: str,
        server_url: str
    ):
        """Generate INSTALL.ps1 from template"""
        template_file = self.template_dir / "INSTALL.template.ps1"
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace placeholders
        content = content.replace('{{GROUP}}', group)
        content = content.replace('{{SERVER_URL}}', server_url)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _customize_readme(
        self,
        output_file: Path,
        server_url: str,
        server_host: str,
        server_port: int,
        group: str
    ):
        """Generate README.txt from template"""
        template_file = self.template_dir / "README.template.txt"
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace placeholders
        content = content.replace('{{GROUP}}', group)
        content = content.replace('{{SERVER_URL}}', server_url)
        content = content.replace('{{SERVER_HOST}}', server_host)
        content = content.replace('{{SERVER_PORT}}', str(server_port))
        content = content.replace('{{BUILD_TIME}}', datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_zip(self, source_dir: Path, output_file: Path):
        """Create ZIP archive of package directory"""
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            # Walk through directory
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    # Add file to ZIP with relative path
                    arcname = file_path.relative_to(source_dir.parent)
                    zipf.write(file_path, arcname)


# Convenience function for API endpoint
def build_agent_package(server_url: str, api_key: str, group: str) -> str:
    """
    Build agent package and return path to ZIP file
    
    Args:
        server_url: Full URL to server API
        api_key: Agent API key
        group: Node group assignment
    
    Returns:
        Path to generated ZIP file
    """
    builder = AgentPackageBuilder()
    return builder.build_package(server_url, api_key, group)
