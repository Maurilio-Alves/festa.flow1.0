import sqlite3

def listar_financeiro_clientes():
    # Conectando ao banco genérico correto
    conexao = sqlite3.connect("festa_flow.db")
    cursor = conexao.cursor()
    
    # Buscando da tabela genérica 'clientes'
    cursor.execute("SELECT nome, whatsapp, atendente_responsavel, status, valor_total, valor_pago FROM clientes")
    clientes = cursor.fetchall()
    conexao.close()
    
    if not clientes:
        print("\nNenhum cliente cadastrado ainda. Use o 'cadastrar.py' primeiro!")
        return

    print("\n======================= PAINEL FINANCEIRO (FESTA-FLOW) =======================")
    for cliente in clientes:
        nome, whatsapp, atendente, status, total, pago = cliente
        falta_pagar = total - pago
        
        # Lógica de pagamento limpa e profissional
        if falta_pagar <= 0 and total > 0:
            status_pagamento = "✅ QUITADO"
        elif total == 0:
            status_pagamento = "⏳ Sem contrato gerado (R$ 0,00)"
        else:
            status_pagamento = f"⚠️ Falta: R$ {falta_pagar:.2f}"
        
        print(f"Cliente: {nome:<18} | Zap: {whatsapp:<12} | Atend: {atendente:<10}")
        print(f"Etapa: {status:<18} | {status_pagamento}")
        print("-" * 78)
    print("==============================================================================\n")

if __name__ == "__main__":
    listar_financeiro_clientes()