"""
FASE7/launcher.py — Sistema Integrado de Gestão (Dashboard Streamlit)

Uso:  streamlit run launcher.py
      streamlit run launcher.py --server.port 8500  (evita conflito com FASE4)
"""
import streamlit as st
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.resolve()
ROOT_DIR = BASE_DIR.parent
CONFIG   = BASE_DIR / "config.json"

# Subprocessos das fases devem escrever em UTF-8. No Windows o stdout do filho
# usa cp1252 por padrão e prints com emoji/acento ("✓", "🏆", "°") quebram com
# UnicodeEncodeError. Passamos a codificação via env para todas as fases.
CHILD_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

# ── Config ─────────────────────────────────────────────────────────────────────
def load_config() -> dict:
    """
    Carrega as configurações do config.json.

    Essa função é chamada toda vez que a página do Streamlit recarrega.
    Retorna um dicionário com o nome do projeto, setor, equipe e a
    lista de fases configuradas.
    """
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg: dict):
    """
    Salva o dicionário de configurações de volta no config.json.

    O indent=2 deixa o JSON organizado e legível quando aberto no editor.
    O ensure_ascii=False preserva os acentos em português corretamente.
    """
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

# ── Processos ──────────────────────────────────────────────────────────────────
def _procs() -> dict:
    """
    Retorna o dicionário de processos em execução da sessão do Streamlit.

    O st.session_state funciona como uma variável global que persiste
    enquanto o usuário não fechar ou recarregar a aba. A gente usa
    ele pra lembrar quais fases estão rodando entre as atualizações de página.
    O underscore no nome indica que é uma função de uso interno.
    """
    if "procs" not in st.session_state:
        st.session_state.procs = {}
    return st.session_state.procs

def is_running(pid: str) -> bool:
    """
    Verifica se uma fase está em execução no momento.

    Busca o processo pelo ID da fase e usa poll() para checar o status.
    Se poll() retorna None, o processo ainda está rodando.
    Se retornar um número, é o código de saída — o processo já terminou.
    """
    p = _procs().get(pid)
    return p is not None and p.poll() is None

def _build_cmd(phase: dict) -> tuple[list, str]:
    """
    Monta o comando de execução para uma fase (mesma lógica do run.py).

    Essa função é uma cópia do build_cmd do run.py porque o launcher
    roda de forma independente, sem importar aquele arquivo.
    Dependendo do tipo da fase, o comando gerado é diferente.
    """
    path  = (ROOT_DIR / phase["path"]).resolve()
    cwd   = str(path.parent)
    ptype = phase["type"]
    port  = phase.get("port")

    if ptype == "cli_python":
        cmd = [sys.executable, str(path)]
    elif ptype == "streamlit":
        cmd = [sys.executable, "-m", "streamlit", "run", str(path)]
        if port:
            cmd += ["--server.port", str(port)]
    elif ptype == "r_script":
        cmd = ["Rscript", str(path)]
    elif ptype == "jupyter":
        cmd = ["jupyter", "notebook", str(path)]
    else:
        return [], cwd

    return cmd, cwd

def launch(phase: dict):
    """
    Inicia uma fase em um processo separado em segundo plano.

    Usa subprocess.Popen para não travar o dashboard enquanto a fase roda.
    No Windows, CREATE_NEW_CONSOLE abre uma janela separada no terminal,
    o que facilita ver a saída de scripts CLI diretamente.
    O processo é salvo no session_state para poder ser parado depois.
    """
    cmd, cwd = _build_cmd(phase)
    if not cmd:
        st.error(f"Tipo '{phase['type']}' não suportado.")
        return
    flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    # Fases que encerram (R, Python-CLI) fechariam a janela nova assim que o
    # processo termina, sem o usuário ver o resultado. No Windows, envolvemos
    # com 'cmd /c ... & pause' para a janela aguardar uma tecla antes de fechar.
    # Servidores (streamlit/jupyter) continuam rodando, então ficam de fora —
    # assim o botão Parar continua agindo direto sobre o processo correto.
    if sys.platform == "win32" and phase["type"] in ("cli_python", "r_script"):
        cmd = ["cmd", "/c", *cmd, "&", "pause"]
    proc  = subprocess.Popen(cmd, cwd=cwd, creationflags=flags, env=CHILD_ENV)
    _procs()[str(phase["id"])] = proc

def stop(pid: str):
    """
    Para um processo em execução pelo ID da fase.

    O terminate() manda um sinal de encerramento para o processo filho.
    É mais adequado que kill() porque dá a chance do programa salvar
    dados e fechar recursos antes de encerrar.
    """
    p = _procs().get(pid)
    if p and p.poll() is None:
        p.terminate()

# ── Página ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sistema Integrado",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

cfg = load_config()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    with st.form("cfg_form"):
        sector  = st.text_input("Setor",     value=cfg["sector"])
        project = st.text_input("Projeto",   value=cfg["project_name"])
        team    = st.text_input("Equipe",    value=cfg.get("team", ""))
        desc    = st.text_area("Descrição",  value=cfg.get("description", ""), height=70)

        st.markdown("**Módulos ativos:**")
        toggles = {
            str(ph["id"]): st.checkbox(
                f"Fase {ph['id']} — {ph['name']}",
                value=ph.get("enabled", True),
                key=f"cb_{ph['id']}",
            )
            for ph in cfg["phases"]
        }

        if st.form_submit_button("💾 Salvar configurações", use_container_width=True):
            cfg.update({"sector": sector, "project_name": project,
                        "team": team, "description": desc})
            for ph in cfg["phases"]:
                ph["enabled"] = toggles[str(ph["id"])]
            save_config(cfg)
            st.success("Configurações salvas!")
            st.rerun()

    st.markdown("---")
    st.info(
        "Para adaptar a outro setor, edite `config.json` trocando "
        "os caminhos e descrições das fases."
    )

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a5c1a,#2d8a2d);
            padding:1.8rem 2rem;border-radius:12px;color:white;margin-bottom:1.2rem;">
  <h1 style="margin:0;font-size:2rem;">🌱 {cfg['project_name']}</h1>
  <p style="margin:.4rem 0 0;opacity:.9;">
    <strong>Setor:</strong> {cfg['sector']} &nbsp;|&nbsp;
    <strong>Equipe:</strong> {cfg.get('team','')}
  </p>
  <p style="margin:.3rem 0 0;opacity:.75;font-size:.9rem;">{cfg.get('description','')}</p>
</div>
""", unsafe_allow_html=True)

# ── Métricas ───────────────────────────────────────────────────────────────────
enabled   = [p for p in cfg["phases"] if p.get("enabled", True)]
n_running = sum(1 for p in enabled if is_running(str(p["id"])))

c1, c2, c3, c4 = st.columns(4)
c1.metric("📦 Fases no sistema", len(cfg["phases"]))
c2.metric("✅ Módulos ativos",   len(enabled))
c3.metric("🟢 Rodando agora",    n_running)
c4.metric("🕐 Atualizado",       datetime.now().strftime("%H:%M:%S"))

st.markdown("---")
st.subheader("🚀 Módulos do Sistema")

# ── Cards por tipo ─────────────────────────────────────────────────────────────
TYPE_BADGE = {
    "cli_python": ("#0066cc", "💻 CLI Python"),
    "streamlit":  ("#e74c3c", "📊 Streamlit"),
    "r_script":   ("#276dc3", "📈 R Script"),
    "jupyter":    ("#f37626", "📓 Jupyter"),
}
PHASE_ICON = {
    "1":  "🌾", "2a": "🌱", "2b": "🌤️", "2c": "📊",
    "3":  "🤖", "4t": "⚙️", "4d": "📊",
    "5":  "☁️", "6":  "👁️",
}

for row_start in range(0, len(enabled), 3):
    row  = enabled[row_start:row_start + 3]
    cols = st.columns(3)

    for col, ph in zip(cols, row):
        pid          = str(ph["id"])
        icon         = PHASE_ICON.get(pid, "⚙️")
        color, badge = TYPE_BADGE.get(ph["type"], ("#666", "⚙️ Script"))
        running      = is_running(pid)
        port_info    = f" · porta {ph['port']}" if ph.get("port") else ""

        with col:
            with st.container(border=True):
                st.markdown(
                    f"<span style='font-size:1.6rem'>{icon}</span>&nbsp;"
                    f"<span style='background:{color}22;color:{color};"
                    f"border-radius:4px;padding:2px 8px;font-size:.75rem;"
                    f"font-weight:600'>{badge}{port_info}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Fase {ph['id']} — {ph['name']}**")
                st.caption(ph["description"])
                st.markdown("🟢 **Rodando**" if running else "⚪ Parado")

                label    = "⏹ Parar" if running else "▶ Iniciar"
                btn_type = "secondary" if running else "primary"
                if st.button(label, key=f"btn_{pid}",
                             use_container_width=True, type=btn_type):
                    stop(pid) if running else launch(ph)
                    st.rerun()

st.markdown("---")
st.caption(
    f"Sistema Integrado v1.0 · FIAP ON · {cfg.get('team','IA_Underground')} · 2025"
    "  —  Generalizável para qualquer setor via `config.json`"
)
