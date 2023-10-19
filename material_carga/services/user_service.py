
import pandas as pd
from material_carga.models import \
    Conta, Material, Setor


def update_database(csv_file):
    file = pd.read_csv(
        filepath_or_buffer=csv_file,
        sep=';',
        encoding='iso-8859-1')

    for i in range(0, len(file)):
        dependencia = file['DEPENDENCIA'][i]
        if not isinstance(dependencia, str):
            continue

        conta_raw = file['CONTA'][i]
        if not isinstance(conta_raw, str):
            continue

        try:
            sigla, nome = Setor.format_dependencia(dependencia)
            setor = Setor.objects.get_or_create(sigla=sigla, nome=nome)[0]

            conta_numero, conta_nome = Conta.format_conta(conta_raw)
            conta = Conta.objects.get_or_create(
                numero=conta_numero, nome=conta_nome)[0]
            material = Material(
                setor=setor,
                conta=conta,
                n_bmp=int(file['Nº BMP'][i]),
                nomenclatura=file['NOMECLATURA/COMPONENTE'][i],
                n_serie=file['Nº SERIE'][i],
                vl_atualizado=float(
                    0 if not isinstance(file['VL. ATUALIZ.'][i], str)
                    else file['VL. ATUALIZ.'][i].replace(',', '.')
                ),
                vl_liquido=float(
                    0 if not isinstance(file['VL. LIQUIDO'][i], str)
                    else file['VL. LIQUIDO'][i].replace(',', '.')
                ),
                situacao=file['SITUACAO'][i]
            )
            material.save()
        except IndexError:
            print(f'Row {i} with invalid data.')
        except Exception as exc:
            print(f'line: {i}')
            print(exc)
