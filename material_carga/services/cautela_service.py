
def close_all_emprestimos(cautela):
    """Atualiza a data_devolucao de todos os emprestimos
    de acordo com a data de baixa da Cautela

    Args:
        cautela (Cautela): cautela cujos emprestimos serão atualizados

    Returns:
        Cautela: cautela atualizada
    """
    for emprestimo in cautela.emprestimos.all():
        if not emprestimo.data_devolucao:
            emprestimo.data_devolucao = cautela.data_baixa
            emprestimo.save()


def close_requested_emprestimos(cautela, cautela_request):
    """Atualiza os emprestimos da cautela cuja baixa foi solicitada na request

    Args:
        cautela (Cautela): Cautela persistida no banco
        cautela_request (Dict): dados da cautela recebida na request

    Returns:
        Cautela: Cautela atualizada
    """
    for emprestimo_req in cautela_request.get('emprestimos', []):
        emprestimo = next(
            emprestimo for emprestimo in cautela.emprestimos.all()
            if emprestimo.id == emprestimo_req['id']
            and not emprestimo.data_devolucao
        )
        emprestimo.data_devolucao = emprestimo_req.get(
            'data_devolucao', emprestimo.data_devolucao)
        emprestimo.save()
