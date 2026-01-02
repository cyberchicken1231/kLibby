#!/usr/bin/env python3
"""
Wrapper to run main_simple with SSL disabled
This avoids stdin issues with heredoc in shell script
"""
import ssl

# Disable SSL verification (Kindle has outdated CA certificates)
ssl._create_default_https_context = ssl._create_unverified_context

# Now run main_simple
import main_simple
main_simple.main()
