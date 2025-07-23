#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevFlow - Sistema de Gestão para Freelancers
Aplicação principal
"""

import sys
import os
import customtkinter as ctk
from config import config
from src.gui.main_window import MainWindow
from src.database.connection import DatabaseManager
from src.utils.logger import setup_logger

def main():
    """Função principal da aplicação"""
    try:
        # Configura o logger
        logger = setup_logger()
        logger.info(f"Iniciando {config.APP_NAME} v{config.APP_VERSION}")
        
        # Valida configurações
        config.validate_config()
        
        # Configura o CustomTkinter
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        
        # Inicializa o gerenciador de banco de dados
        db_manager = DatabaseManager()
        
        # Verifica conexão com o banco
        if not db_manager.test_connection():
            logger.error("Falha na conexão com o banco de dados")
            sys.exit(1)
        
        # Executa migrações se necessário
        db_manager.run_migrations()
        
        # Cria e executa a janela principal
        app = MainWindow()
        app.run()
        
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()