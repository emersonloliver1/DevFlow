#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevFlow - Launcher
Script para executar o DevFlow em modo Desktop ou Web
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_desktop():
    """Executa a versão desktop do DevFlow"""
    print("🖥️  Iniciando DevFlow - Versão Desktop...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 DevFlow Desktop encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar DevFlow Desktop: {e}")

def run_web():
    """Executa a versão web do DevFlow com Streamlit"""
    print("🌐 Iniciando DevFlow - Versão Web...")
    print("📱 Acesse: http://localhost:8501")
    print("⏹️  Para parar, pressione Ctrl+C")
    
    try:
        # Define variável de ambiente para pular configuração inicial do Streamlit
        os.environ['STREAMLIT_EMAIL'] = ''
        
        # Executa o Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.headless", "true",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 DevFlow Web encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar DevFlow Web: {e}")

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import customtkinter
        desktop_ok = True
    except ImportError:
        desktop_ok = False
    
    try:
        import streamlit
        web_ok = True
    except ImportError:
        web_ok = False
    
    return desktop_ok, web_ok

def main():
    """Função principal do launcher"""
    parser = argparse.ArgumentParser(
        description="DevFlow - Sistema de Gestão para Freelancers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_devflow.py              # Menu interativo
  python run_devflow.py --desktop    # Executa versão desktop
  python run_devflow.py --web        # Executa versão web
  python run_devflow.py --install    # Instala dependências
        """
    )
    
    parser.add_argument('--desktop', action='store_true', help='Executa a versão desktop')
    parser.add_argument('--web', action='store_true', help='Executa a versão web')
    parser.add_argument('--install', action='store_true', help='Instala dependências')
    
    args = parser.parse_args()
    
    # Verifica se estamos no diretório correto
    if not Path('main.py').exists() or not Path('streamlit_app.py').exists():
        print("❌ Erro: Execute este script no diretório raiz do DevFlow")
        sys.exit(1)
    
    # Instalar dependências
    if args.install:
        print("📦 Instalando dependências...")
        try:
            print("\n🖥️  Instalando dependências para versão Desktop...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            
            print("\n🌐 Instalando dependências para versão Web...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"], check=True)
            
            print("\n✅ Todas as dependências foram instaladas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao instalar dependências: {e}")
        return
    
    # Verifica dependências
    desktop_ok, web_ok = check_dependencies()
    
    # Execução direta via argumentos
    if args.desktop:
        if not desktop_ok:
            print("❌ Dependências da versão desktop não encontradas.")
            print("💡 Execute: python run_devflow.py --install")
            sys.exit(1)
        run_desktop()
        return
    
    if args.web:
        if not web_ok:
            print("❌ Dependências da versão web não encontradas.")
            print("💡 Execute: python run_devflow.py --install")
            sys.exit(1)
        run_web()
        return
    
    # Menu interativo
    print("\n" + "="*50)
    print("🚀 DevFlow - Sistema de Gestão para Freelancers")
    print("="*50)
    
    print("\n📋 Status das dependências:")
    print(f"   🖥️  Desktop (CustomTkinter): {'✅ OK' if desktop_ok else '❌ Não instalado'}")
    print(f"   🌐 Web (Streamlit): {'✅ OK' if web_ok else '❌ Não instalado'}")
    
    if not desktop_ok and not web_ok:
        print("\n❌ Nenhuma dependência encontrada!")
        print("💡 Execute: python run_devflow.py --install")
        sys.exit(1)
    
    print("\n🎯 Escolha uma opção:")
    options = []
    
    if desktop_ok:
        options.append(("1", "🖥️  Executar versão Desktop", run_desktop))
    
    if web_ok:
        options.append(("2", "🌐 Executar versão Web", run_web))
    
    options.append(("i", "📦 Instalar/Atualizar dependências", None))
    options.append(("q", "🚪 Sair", None))
    
    for key, desc, _ in options:
        print(f"   [{key}] {desc}")
    
    while True:
        try:
            choice = input("\n👉 Digite sua escolha: ").strip().lower()
            
            if choice == "q":
                print("👋 Até logo!")
                break
            
            if choice == "i":
                print("\n📦 Instalando dependências...")
                try:
                    print("\n🖥️  Instalando dependências para versão Desktop...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
                    
                    print("\n🌐 Instalando dependências para versão Web...")
                    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"], check=True)
                    
                    print("\n✅ Dependências instaladas! Reinicie o launcher.")
                    break
                except Exception as e:
                    print(f"❌ Erro ao instalar dependências: {e}")
                continue
            
            # Procura a opção escolhida
            found = False
            for key, desc, func in options:
                if choice == key and func:
                    print(f"\n{desc}")
                    func()
                    found = True
                    break
            
            if not found:
                print("❌ Opção inválida! Tente novamente.")
            else:
                break
                
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except EOFError:
            print("\n👋 Até logo!")
            break

if __name__ == "__main__":
    main()