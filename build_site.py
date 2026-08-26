#!/usr/bin/env python3
"""
RenderPhoenix Website — Build Entrypoint
========================================
CLI entry point that initializes and executes the modular SiteBuilder engine.
Usage: python3 build_site.py
"""

import sys
from builder import SiteBuilder

def main():
    try:
        builder = SiteBuilder()
        builder.build()
    except Exception as e:
        print(f"Build failed with error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
