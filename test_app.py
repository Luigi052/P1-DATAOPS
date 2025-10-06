#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento da aplicação Flask
"""

import urllib.request
import urllib.error
import json
import time
import sys

def test_health_endpoint():
    """Testa o endpoint de health check"""
    try:
        with urllib.request.urlopen('http://localhost:5001/', timeout=10) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                print("✅ Health endpoint funcionando:", data)
                return True
            else:
                print(f"❌ Health endpoint falhou: {response.status}")
                return False
    except urllib.error.URLError as e:
        print(f"❌ Erro ao conectar com health endpoint: {e}")
        return False

def test_produtos_endpoint():
    """Testa o endpoint de produtos"""
    try:
        with urllib.request.urlopen('http://localhost:5001/produtos', timeout=10) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                produtos = json.loads(data)
                print("✅ Produtos endpoint funcionando:")
                print(f"   Total de produtos: {len(produtos)}")
                for produto in produtos:
                    print(f"   - {produto['nome']}: R$ {produto['preco']}")
                return True
            else:
                print(f"❌ Produtos endpoint falhou: {response.status}")
                return False
    except urllib.error.URLError as e:
        print(f"❌ Erro ao conectar com produtos endpoint: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes da aplicação Flask...")
    print("=" * 50)
    
    # Aguardar um pouco para garantir que a aplicação esteja rodando
    print("⏳ Aguardando aplicação inicializar...")
    time.sleep(5)
    
    # Testar endpoints
    health_ok = test_health_endpoint()
    produtos_ok = test_produtos_endpoint()
    
    print("=" * 50)
    if health_ok and produtos_ok:
        print("🎉 Todos os testes passaram! Aplicação funcionando corretamente.")
        sys.exit(0)
    else:
        print("💥 Alguns testes falharam!")
        sys.exit(1)

if __name__ == "__main__":
    main()
