#!/usr/bin/env bash

PROJECT_PATH=/workspaces/infra

mkdir -p $PROJECT_PATH/.vscode
cp $PROJECT_PATH/.devcontainer/artifacts/vscode/* $PROJECT_PATH/.vscode

make bootstrap
