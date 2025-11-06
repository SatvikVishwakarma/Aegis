"""
Agent Package Builder Routes
Provides API endpoints for building and downloading customized agent packages
"""
import logging
import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent_builder import build_agent_package
from authentication import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


class BuildPackageRequest(BaseModel):
    """Request model for building agent package"""
    server_url: str = Field(..., description="Full URL to server API (e.g., http://192.168.1.100:5000)")
    group: str = Field(..., description="Node group assignment", min_length=1, max_length=50)


class BuildPackageResponse(BaseModel):
    """Response model for build package request"""
    message: str
    filename: str
    size_bytes: int


@router.post(
    "/build-package",
    response_class=FileResponse,
    summary="Build and download customized agent package",
    description="Generates a customized Windows agent package with provided configuration"
)
async def build_package_endpoint(
    request: BuildPackageRequest,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Build customized agent package
    
    Requires authentication. Generates a ZIP file containing:
    - Pre-built agent executable and dependencies
    - Customized appsettings.json
    - Installation scripts (INSTALL.ps1, UNINSTALL.ps1)
    - README with deployment instructions
    
    Args:
        request: Build parameters (server_url, group)
        current_user: Authenticated user (from JWT token)
    
    Returns:
        FileResponse: ZIP file download
    """
    try:
        logger.info(f"Building agent package for user: {current_user.get('email', 'unknown')}, group: {request.group}")
        
        # Get API key from environment
        api_key = os.getenv("AGENT_API_KEY")
        if not api_key:
            logger.error("AGENT_API_KEY not configured in server environment")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: AGENT_API_KEY not set"
            )
        
        # Build package
        zip_path = build_agent_package(
            server_url=request.server_url,
            api_key=api_key,
            group=request.group
        )
        
        # Verify ZIP file was created
        if not os.path.exists(zip_path):
            logger.error(f"Package build failed: ZIP file not found at {zip_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Package build failed"
            )
        
        # Get file size for logging
        file_size = os.path.getsize(zip_path)
        logger.info(f"Package built successfully: {zip_path} ({file_size:,} bytes)")
        
        # Generate filename for download
        filename = f"AegisAgent-{request.group}.zip"
        
        # Return file as download
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Package-Group": request.group,
                "X-Package-Size": str(file_size)
            }
        )
        
    except ValueError as e:
        logger.error(f"Invalid build parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileNotFoundError as e:
        logger.error(f"Template files not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent template not found on server. Please contact administrator."
        )
    except Exception as e:
        logger.error(f"Error building agent package: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build agent package: {str(e)}"
        )


@router.get(
    "/template-info",
    summary="Get agent template information",
    description="Returns information about the available agent template"
)
async def get_template_info(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Get agent template information
    
    Returns details about the pre-built agent template:
    - Version
    - Platform
    - Available collectors
    - Template size
    
    Args:
        current_user: Authenticated user (from JWT token)
    
    Returns:
        Template information dictionary
    """
    try:
        # Get template directory
        template_dir = Path(__file__).parent / "agent-template"
        
        if not template_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent template not found on server"
            )
        
        # Check for executable
        exe_path = template_dir / "AegisAgent.exe"
        if not exe_path.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent executable not found in template"
            )
        
        # Calculate template size
        total_size = sum(f.stat().st_size for f in template_dir.rglob('*') if f.is_file())
        
        return {
            "status": "available",
            "platform": "Windows (x64)",
            "runtime": ".NET 8.0 (self-contained)",
            "collectors": [
                "Process Monitor",
                "Network Monitor",
                "Registry Monitor",
                "Process Control"
            ],
            "template_size_mb": round(total_size / (1024 * 1024), 2),
            "deployment_method": "Windows Service or Console",
            "requirements": [
                "Windows 10/11 or Windows Server 2016+",
                "Administrator privileges for service installation",
                "Network access to Aegis server"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template information: {str(e)}"
        )
