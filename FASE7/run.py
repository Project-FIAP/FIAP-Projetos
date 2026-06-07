"""
FASE7/run.py — Sistema Integrado de Gestão (Launcher CLI)

Uso:
  python run.py             → menu interativo
  python run.py 4d          → lança a Fase 4d diretamente
  python run.py dashboard   → abre o launcher Streamlit
  python run.py --list      → lista todas as fases disponíveis
"""
import argparse
import os
import subprocess
import sys
import json
import webbrowser
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent.resolve()
ROOT_DIR = BASE_DIR.parent
CONFIG   = BASE_DIR / "config.json"

# Garante que as fases-filhas (subprocessos) escrevam em UTF-8. Sem isso, no
# Windows o stdout do filho usa cp1252 e qualquer print com emoji/acento (ex.:
# "✓", "🏆", "°") quebra com UnicodeEncodeError. O reconfigure acima vale só
# para este processo; os filhos herdam um stream novo, então passamos via env.
CHILD_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def load_config() -> dict:
    """
    Carrega o arquivo config.json com todas as configurações do projeto.

    Retorna um dicionário Python com as informações do setor, equipe
    e a lista de todas as fases cadastradas. Se o arquivo não existir,
    vai dar FileNotFoundError — então não apaga o config.json!
    """
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def build_cmd(phase: dict) -> tuple[list, str]:
    """
    Monta o comando de execução de uma fase com base no seu tipo.

    Cada tipo de fase usa um comando diferente:
    - cli_python  → python arquivo.py
    - streamlit   → python -m streamlit run arquivo.py --server.port X
    - r_script    → Rscript arquivo.R
    - jupyter     → jupyter notebook arquivo.ipynb

    Retorna uma tupla (cmd, cwd):
    - cmd: lista com o comando e seus argumentos (para o subprocess)
    - cwd: diretório de trabalho onde o comando vai rodar
    """
    path  = (ROOT_DIR / phase["path"]).resolve()
    cwd   = str(path.parent)
    ptype = phase["type"]
    port  = phase.get("port")

    if ptype == "cli_python":
        cmd = [sys.executable, str(path)]
    elif ptype == "streamlit":
        # --server.headless=true impede o Streamlit de abrir o navegador sozinho;
        # quem abre a aba (uma só) é o webbrowser.open() em run_phase(). Sem isso,
        # abririam duas abas: a do Streamlit + a nossa.
        cmd = [sys.executable, "-m", "streamlit", "run", str(path),
               "--server.headless=true"]
        if port:
            cmd += ["--server.port", str(port)]
    elif ptype == "r_script":
        cmd = ["Rscript", str(path)]
    elif ptype == "jupyter":
        cmd = ["jupyter", "notebook", str(path)]
    else:
        return [], cwd

    return cmd, cwd


def run_phase(phase: dict):
    """
    Executa uma fase do projeto no terminal.

    Para apps Streamlit, abre o navegador automaticamente e aguarda
    até o usuário pressionar Ctrl+C. Para outros tipos (CLI, R, Jupyter),
    executa e espera o processo terminar normalmente.

    Trata dois erros comuns: executável não encontrado (ex: R não instalado)
    e interrupção do teclado (Ctrl+C).
    """
    cmd, cwd = build_cmd(phase)
    if not cmd:
        print(f"  Tipo '{phase['type']}' não suportado.")
        return

    print(f"\n  ▶  {phase['name']}")
    print(f"     {' '.join(str(x) for x in cmd)}\n")

    try:
        if phase["type"] == "streamlit":
            port = phase.get("port", 8501)
            proc = subprocess.Popen(cmd, cwd=cwd, env=CHILD_ENV)
            print(f"  Dashboard disponível em: http://localhost:{port}")
            print("  Pressione Ctrl+C para encerrar.\n")
            webbrowser.open(f"http://localhost:{port}")
            proc.wait()
        else:
            subprocess.run(cmd, cwd=cwd, env=CHILD_ENV)
    except FileNotFoundError as exc:
        print(f"  Erro: executável não encontrado — {exc}")
        print("  Verifique se o programa está instalado e no PATH.")
    except KeyboardInterrupt:
        print("\n  Serviço encerrado.")


def open_dashboard():
    """
    Abre o painel de controle visual (Fase 7) no navegador.

    Sobe o launcher.py via Streamlit na porta 8501 e abre o navegador
    automaticamente. Pressione Ctrl+C no terminal para encerrar.
    O dashboard permite iniciar e parar qualquer fase com botões.
    """
    launcher = BASE_DIR / "launcher.py"
    print("\n  ▶  Abrindo Dashboard Integrado...")
    print("     Acesse: http://localhost:8501\n")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(launcher),
         "--server.port", "8501", "--server.headless=true"],
        env=CHILD_ENV,
    )
    webbrowser.open("http://localhost:8501")
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\n  Dashboard encerrado.")


def print_menu(phases_map: dict, cfg: dict):
    """
    Desenha o menu interativo no terminal com todas as fases ativas.

    Cada fase aparece com:
    - Seu ID entre colchetes (ex: [4d])
    - Um badge do tipo: [CLI], [WEB], [ R ] ou [ NB ]
    - O nome da fase e a porta (se for Streamlit)

    Fases com 'enabled: false' no config.json não aparecem aqui.
    """
    badges = {
        "cli_python": "CLI",
        "streamlit":  "WEB",
        "r_script":   " R ",
        "jupyter":    " NB ",
    }
    width = 58
    print(f"\n  {'═' * width}")
    print(f"  {cfg['project_name']}")
    print(f"  Setor: {cfg['sector']}  |  Equipe: {cfg.get('team', '')}")
    print(f"  {'─' * width}")
    for pid, ph in phases_map.items():
        if not ph.get("enabled", True):
            continue
        badge    = badges.get(ph["type"], "???")
        port_str = f"  (:{ph['port']})" if ph.get("port") else ""
        print(f"  [{pid:>2}]  [{badge}]  {ph['name']}{port_str}")
    print(f"  {'─' * width}")
    print(f"  [ 0]  [WEB]  Dashboard Completo (Fase 7)")
    print(f"  [ q]         Sair")
    print(f"  {'═' * width}")


def interactive(phases_map: dict, cfg: dict):
    """
    Gerencia o loop principal do menu interativo.

    Exibe o menu e fica esperando o usuário digitar uma opção.
    Aceita: ID de uma fase (ex: '4d'), '0' ou 'dashboard' para o painel
    visual, ou 'q' / 'sair' para encerrar. Após cada fase terminar,
    o menu é exibido novamente para o usuário escolher outra opção.
    """
    print_menu(phases_map, cfg)
    while True:
        try:
            choice = input("\n  Opção: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  Saindo...")
            break

        if choice in ("q", "quit", "sair", "exit"):
            print("  Até logo!")
            break
        elif choice in ("0", "dashboard"):
            open_dashboard()
            break
        elif choice in phases_map and phases_map[choice].get("enabled", True):
            run_phase(phases_map[choice])
            print_menu(phases_map, cfg)
        elif choice in phases_map:
            print(f"  Fase '{choice}' está desabilitada em config.json.")
        else:
            print("  Opção inválida. Tente novamente.")


def list_phases(phases_map: dict):
    """
    Lista todas as fases cadastradas no config.json no terminal.

    Mostra o status [on] ou [off], o ID, o tipo e o nome de cada fase.
    Inclui as fases desabilitadas (diferente do menu que as omite).
    Usada quando o usuário passa o argumento --list na linha de comando.
    """
    print("\n  Fases disponíveis:\n")
    for pid, ph in phases_map.items():
        status = "[on] " if ph.get("enabled", True) else "[off]"
        print(f"  {status}  [{pid:>2}]  [{ph['type']:10}]  {ph['name']}")
    print()


def main():
    """
    Ponto de entrada do script — lê os argumentos e decide o que executar.

    Sem argumentos: abre o menu interativo.
    Com ID de fase: executa aquela fase diretamente.
    Com 'dashboard': abre o painel visual no navegador.
    Com '--list': lista todas as fases e sai.

    Exemplos:
      python run.py           → menu interativo
      python run.py 4d        → Dashboard ML (Streamlit)
      python run.py dashboard → Painel completo da Fase 7
      python run.py --list    → lista de fases disponíveis
    """
    parser = argparse.ArgumentParser(
        prog="python run.py",
        description="Sistema Integrado FarmTech — Launcher CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python run.py           → menu interativo\n"
            "  python run.py 1         → Fase 1 (áreas/insumos)\n"
            "  python run.py 4d        → Dashboard ML Streamlit\n"
            "  python run.py dashboard → Launcher visual completo\n"
            "  python run.py --list    → listar todas as fases\n\n"
            "Para adaptar a outro setor, edite config.json."
        ),
    )
    parser.add_argument(
        "fase", nargs="?",
        help="ID da fase ou 'dashboard'",
    )
    parser.add_argument(
        "--list", "-l", action="store_true",
        help="Listar todas as fases e sair",
    )
    args = parser.parse_args()

    cfg        = load_config()
    phases_map = {str(p["id"]): p for p in cfg["phases"]}

    if args.list:
        list_phases(phases_map)
        return

    if args.fase is None:
        interactive(phases_map, cfg)
    elif args.fase in ("0", "dashboard"):
        open_dashboard()
    elif args.fase in phases_map:
        run_phase(phases_map[args.fase])
    else:
        available = [k for k, v in phases_map.items() if v.get("enabled", True)]
        print(f"\n  Fase '{args.fase}' não encontrada.")
        print(f"  IDs disponíveis: {', '.join(available)}")
        print("  Use --list para ver todas.\n")


if __name__ == "__main__":
    main()
