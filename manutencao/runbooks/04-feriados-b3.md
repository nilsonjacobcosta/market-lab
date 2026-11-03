# RB 04 — Calendário de feriados da B3 (`const FERIADOS` em `carteiras/monitor-besst/index.html`)

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Manter na página a lista de dias **sem pregão** da B3. O selo do topo usa essa lista (funções `ehPregao`,
`pregaoAnterior` e `liveLabel`) para saber qual fechamento era esperado. Com feriado faltando, o selo mostra um falso
"⚠ … a atualização automática atrasou" nesse dia; com um dia útil marcado por engano como feriado, o selo deixa de avisar
um atraso real.

## 2. Quando fazer (gatilhos)
- **Anual, em dezembro**: a B3 publica o ofício circular do calendário do ano seguinte no início de dezembro
  (o de 2026 saiu em 04/12/2025). Concluir até ~20/12.
- **Por evento**: errata ou novo ofício da B3 durante o ano; feriado nacional novo criado por lei (ex.: 20/11 virou
  nacional em 2024).
- **Sinal de atraso**: a lista tem só datas provisórias para o ano corrente; ou o comentário da linha ~342 ainda
  diz "provisório" para o ano em curso.

## 3. Arquivos afetados
| Arquivo | Trecho | Quem lê |
|---|---|---|
| `carteiras/monitor-besst/index.html` | linha ~342 (comentário com a fonte) e ~343–344 (`const FERIADOS=new Set([...])`, datas `"AAAA-MM-DD"`) | selo de atualização |

Estado em 03/11/2026: 2026 com 14 datas oficiais; 2027 com 12 datas **provisórias** (feriados nacionais + 24/12 e 31/12).
O comentário cita o Ofício Circular 054/2025-VNC. **Achado desta revisão:** esse ofício foi **revogado** pelo
Ofício Circular 003/2026-VNC (08/01/2026), que por sua vez recebeu **errata** no Ofício Circular 041/2026-VNC
(30/06/2026). A errata **revoga integralmente** o 003/2026-VNC e o republica: o documento vigente para 2026 é o
**041/2026-VNC**. Ela só mexeu em suspensões do mercado de dólar (CSD2: 03/07/2026 saiu da lista); as 14 datas sem
pregão do segmento Listado **não mudaram** (conferidas no PDF da errata em 03/11/2026), então a lista de 2026 continua
correta. Sugestão: na próxima edição, trocar o comentário para
"2026: B3, Ofício Circular 041/2026-VNC (errata que substituiu o 003/2026-VNC, que revogou o 054/2025-VNC)".

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | O que procurar |
|---|---|---|---|
| 1 | **B3 — Ofício Circular "Calendário de feriados em AAAA"** (área VNC) | 2026 original: https://www.b3.com.br/data/files/C2/E3/28/AD/4FAEA9105B12E5A9AC094EA8/OC%20054-2025-VNC%20CALENDARIO%20DE%20FERIADOS%20EM%202026%20E%20FUNCIONAMENTO%20DA%20B3%20EM%2018022026%20QUARTAFEIRA%20DE%20CINZAS_PT.pdf — **verificada** (revogado); vigente — errata 041/2026-VNC, que substitui o 003/2026-VNC: https://www.b3.com.br/data/files/20/57/01/AA/06A1F910ADC36BE9AC094EA8/OC%20041-2026-VNC%20ERRATA%20-%20CALENDARIO%20DE%20FERIADOS%20EM%202026_PT.pdf — **verificada** | "Quadro A" (Listado B3): datas **sem sessão de negociação**; observações sobre 24/12, 31/12 e Quarta-feira de Cinzas |
| 2 | **B3 — página "Feriados"** do calendário de negociação | https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/calendario-de-negociacao/feriados/ — **não verificada nesta sessão** | tabela do ano |
| 3 | Imprensa reconhecida | matérias "B3 divulga calendário de feriados de AAAA" | só para achar o número do ofício |
| — | **Não usar** | calendários de tribunais, prefeituras, bancos (feriado bancário ≠ dia sem pregão; ex.: 09/07 em SP tem pregão) | — |

Como achar o ofício novo: busque no site da B3 (ou num buscador) por `"Calendário de feriados em 2027" Ofício Circular VNC`.
Os PDFs ficam em `https://www.b3.com.br/data/files/...`. Confirme que o documento é da B3 (cabeçalho "Ofício Circular
NNN/AAAA-VNC") e se há ofício mais novo revogando-o.

## 5. Passo a passo
1. `git pull`.
2. Abra o ofício do ano seguinte. Anote do Quadro A (Listado) **todas** as datas sem pregão, inclusive pontos facultativos
   (Carnaval) e dias sem sessão (24/12, 31/12). Ignore feriados dos EUA e de SP (a B3 opera).
3. Edite a linha ~343–344: substitua as datas provisórias do ano pelas oficiais, em ordem, no formato `"AAAA-MM-DD"`.
4. Acrescente as datas **provisórias** do ano depois (para a virada de ano não ficar sem lista), geradas pelo snippet abaixo.
5. Atualize o comentário da linha ~342 com o número do ofício e "AAAA+1: provisório".
6. Mantenha os anos anteriores ao corrente apenas se ainda forem úteis (o selo só olha hoje e o pregão anterior;
   pode apagar anos já passados há mais de 1 mês).

Datas provisórias de um ano (feriados nacionais móveis pela Páscoa + fixos + 24/12 e 31/12; só dias úteis):
```python
from datetime import date, timedelta
def pascoa(a):  # algoritmo de Meeus/Jones/Butcher (calendário gregoriano)
    b, c = divmod(a, 100); d, e = divmod(b, 4); f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * (a % 19) + b - d - g + 15) % 30; i, k = divmod(c, 4); l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a % 19 + 11 * h + 22 * l) // 451; mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(a, mes, dia + 1)
def provisorios(a):
    p = pascoa(a)
    moveis = [p - timedelta(48), p - timedelta(47), p - timedelta(2), p + timedelta(60)]  # Carnaval (2a e 3a), Sexta Santa, Corpus Christi
    fixos = [date(a, m, d) for m, d in ((1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 24), (12, 25), (12, 31))]
    return sorted(x.isoformat() for x in moveis + fixos if x.weekday() < 5)
print(",".join(f'"{d}"' for d in provisorios(2028)))
```
Conferência (testado em 03/11/2026): `provisorios(2027)` reproduz exatamente as 12 datas de 2027 já na página, e
`provisorios(2026)` reproduz as 14 datas oficiais de 2026. Mesmo assim, a lista provisória **não substitui** o ofício
(a B3 pode incluir ou tirar pontos facultativos).

## 6. Como validar
Compare a lista da página com a do ofício e confira que todas as datas são dias úteis:
```python
import re, datetime
html = open("carteiras/monitor-besst/index.html", encoding="utf-8").read()
fer = re.findall(r'"(\d{4}-\d{2}-\d{2})"', re.search(r"const FERIADOS=new Set\(\[(.*?)\]\)", html, re.S).group(1))
OFICIAL = {"2027": []}          # cole aqui as datas do ofício novo, ex.: ["2027-01-01", ...]
for d in fer:
    if datetime.date.fromisoformat(d).weekday() > 4:
        print("fim de semana na lista:", d)
for ano, lista in OFICIAL.items():
    if not lista:
        continue
    pag = sorted(d for d in fer if d.startswith(ano))
    print(ano, "falta na página:", sorted(set(lista) - set(pag)), "| sobra na página:", sorted(set(pag) - set(lista)))
```
Teste no navegador (o script da página não é módulo, então as funções são globais): abra o painel, abra o console
(F12) e simule um feriado à noite e o dia útil seguinte:
```js
window.__AGORA__ = Date.parse("2027-02-08T23:00:00Z"); liveLabel(); document.getElementById("live-t").textContent
ehPregao("2027-02-08")   // false se for feriado
```
O selo não deve mostrar "atrasou" num dia sem pregão. Recarregue a página para voltar ao normal.

## 7. Como publicar (commit)
```bash
git add carteiras/monitor-besst/index.html manutencao/registro.md
git commit -m "Manutenção: feriados B3 <ano> oficiais (Ofício Circular NNN/AAAA-VNC) e <ano+1> provisório"
git pull --rebase && git push
```
O GitHub Pages republica sozinho em 1–2 minutos (rotina "pages-build-deployment" na aba Actions).

## 8. Se a fonte mudar ou falhar
- Ofício ainda não publicado em 20/12: mantenha as provisórias (o snippet acima) e repita a busca na 1ª semana de janeiro
  (em 2026 houve ofício reeditado em 08/01).
- PDF da B3 fora do ar: página "Feriados" da B3 (fonte 2); imprensa só para achar o número do ofício.
- Mudança de lei (feriado nacional novo): só entra na lista quando a B3 confirmar em ofício.

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- A rotina de coleta (`monitor-besst.yml`) **não** lê esta lista: em feriado ela roda, não acha preço novo, mas
  **faz commit mesmo assim** (`gerado_em` e `coletado_em_utc` do `painel.json` mudam a cada execução; preços e
  `pregao_referencia` ficam iguais). A lista só afeta o selo da página.
- Dias com horário especial (Quarta-feira de Cinzas abre às 13h) **têm** pregão: não entram na lista.
- O selo usa Brasília fixo em UTC−3 (sem horário de verão desde 2019). Se o horário de verão voltar, revisar `brt()`
  na linha ~345.
