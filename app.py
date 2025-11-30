import gradio as gr
from typing import List, Optional
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from npi_mcp_server.tools import search_providers, get_provider_by_npi
from npi_mcp_server.schemas import ProviderSummary, ProviderDetail

async def search_providers_tool(query: str, state: str = None, taxonomy: str = None) -> List[dict]:
    """
    Search for healthcare providers via the NPI API.

    Args:
        query: Name (first/last) or organization name.
        state: Two-letter state code.
        taxonomy: Taxonomy code or description.

    Returns:
        List of ProviderSummary objects as dictionaries.
    """
    results = await search_providers(query, state, taxonomy)
    return [r.model_dump() for r in results]

async def get_provider_by_npi_tool(npi: str) -> Optional[dict]:
    """
    Retrieve details for a specific provider by NPI.

    Args:
        npi: 10-digit NPI string.

    Returns:
        ProviderDetail object as dictionary or None if not found.
    """
    result = await get_provider_by_npi(npi)
    if result:
        return result.model_dump()
    return None

with gr.Blocks() as demo:
    gr.Markdown("# NPI Registry MCP Server")
    gr.Markdown("This interface exposes NPI Registry tools as an MCP server.")

    with gr.Tab("Search Providers"):
        with gr.Row():
            query_input = gr.Textbox(label="Query", placeholder="Name or Organization")
            state_input = gr.Textbox(label="State", placeholder="2-letter code (e.g., CA)")
            taxonomy_input = gr.Textbox(label="Taxonomy", placeholder="Taxonomy code")
        search_btn = gr.Button("Search")
        search_output = gr.JSON(label="Results")

        search_btn.click(
            fn=search_providers_tool,
            inputs=[query_input, state_input, taxonomy_input],
            outputs=search_output
        )

        gr.Examples(
            examples=[
                ["SHELLEY AKEY", "AZ", "363LN0000X"],
                ["KATHERYN ALIOTO", "CA", "101YA0400X"],
                ["Counselor", "CA", ""],
                ["Physical Therapist", "WA", "225100000X"],
            ],
            inputs=[query_input, state_input, taxonomy_input],
            label="Try Examples"
        )

    with gr.Tab("Get Provider by NPI"):
        npi_input = gr.Textbox(label="NPI", placeholder="10-digit NPI")
        get_btn = gr.Button("Get Details")
        get_output = gr.JSON(label="Provider Details")

        get_btn.click(
            fn=get_provider_by_npi_tool,
            inputs=[npi_input],
            outputs=get_output
        )

    with gr.Tab("Debug"):
        gr.Markdown("## Connectivity Test")
        debug_btn = gr.Button("Run Diagnostics")
        debug_output = gr.Textbox(label="Logs", lines=20)
        
        async def run_diagnostics():
            import httpx
            import subprocess
            import json
            from npi_mcp_server.config import NPI_API_BASE_URL
            
            logs = []
            logs.append(f"Base URL: {NPI_API_BASE_URL}")
            
            url = f"{NPI_API_BASE_URL.rstrip('/')}/search_providers"
            payload = {
                "query": "SHELLEY AKEY",
                "state": "AZ",
                "taxonomy": "363LN0000X"
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Test 1: Python httpx
            logs.append("\n--- Test 1: Python httpx ---")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                    logs.append(f"Status: {response.status_code}")
                    logs.append(f"Response: {response.text}")
            except Exception as e:
                logs.append(f"Error: {e}")
                
            # Test 2: System curl
            logs.append("\n--- Test 2: System curl ---")
            try:
                cmd = [
                    "curl", "-v", "-X", "POST", url,
                    "-H", "Content-Type: application/json",
                    "-H", f"User-Agent: {headers['User-Agent']}",
                    "-d", json.dumps(payload)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                logs.append(f"Return Code: {result.returncode}")
                logs.append(f"Stdout: {result.stdout}")
                logs.append(f"Stderr: {result.stderr}")
            except Exception as e:
                logs.append(f"Curl Error: {e}")
                
            return "\n".join(logs)

        debug_btn.click(fn=run_diagnostics, outputs=debug_output)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
