# Pythonバージョン、上げるタイミングが見当たらない。
# ライブラリビルド用ステージ
FROM python:3.10.7 as build_stage

# 作業用ディレクトリ
WORKDIR /app

# venvを作る
RUN python -m venv /venv
# PATHの設定
ENV PATH="/venv/bin:$PATH"

# ライブラリの準備
COPY requirements.txt .
RUN pip3 install --upgrade -r  requirements.txt

# 実行ステージ
FROM python:3.10.7-slim AS run_stage
WORKDIR /app
# これをしないとターミナルへの出力が出ない現象が起こる。
ENV PYTHONUNBUFFERED="1"
# venvをビルドステージから移植
COPY --from=build_stage /venv /venv
# PATHの設定
ENV PATH="/venv/bin:$PATH"


#　ソース追加
COPY __init__.py .
COPY botclass.py .
COPY main.py .
COPY run.py .

# 実行はこ↑こ↓
CMD ["python3", "run.py"]