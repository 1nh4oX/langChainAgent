#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全启动脚本 - 设置正确的编码
"""

import sys
import os
import locale

# 设置编码
if sys.platform.startswith('win'):
    # Windows
    os.system('chcp 65001')
else:
    # Unix/Linux/Mac
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    os.environ['LANG'] = 'en_US.UTF-8'
    
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 启动 Streamlit
os.system('streamlit run ui/streamlit_app.py')


