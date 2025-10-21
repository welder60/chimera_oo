<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        <meta charset="utf-8" />
        <title>Laboratório de Quimeras</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link
            rel="stylesheet"
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
        />
    </head>
    <body class="bg-light">
        <main class="container py-5">
            <header class="mb-4">
                <h1 class="display-5">Laboratório de Quimeras</h1>
                <p class="text-muted">Bem-vindo, {{jogador._nome}}!</p>
            </header>

            % if mensagem:
            <div class="alert alert-info" role="alert">{{mensagem}}</div>
            % end

            <section class="row g-4 align-items-start">
                <div class="col-12 col-lg-6">
                    <form method="post" class="card shadow-sm">
                        <div class="card-body">
                            <h2 class="h4">Fundir criaturas</h2>
                            <p class="text-muted">
                                Selecione duas ou mais criaturas descobertas para tentar novas combinações.
                            </p>
                            <label class="form-label" for="criaturas">Criaturas descobertas</label>
                            <select
                                class="form-select"
                                id="criaturas"
                                name="criaturas"
                                multiple
                                size="8"
                            >
                                % for nome in descobertas:
                                <option value="{{nome}}" {{'selected' if nome in selecionadas else ''}}>
                                    {{nome}}
                                </option>
                                % end
                            </select>
                        </div>
                        <div class="card-footer text-end bg-white">
                            <button type="submit" class="btn btn-primary">Fundir</button>
                        </div>
                    </form>
                </div>
                <div class="col-12 col-lg-6">
                    <section class="card shadow-sm mb-4">
                        <div class="card-body">
                            <h2 class="h4">Criaturas descobertas</h2>
                            % if descobertas:
                            <ul class="list-unstyled mb-0">
                                % for nome in descobertas:
                                <li>• {{nome}}</li>
                                % end
                            </ul>
                            % else:
                            <p class="text-muted mb-0">Nenhuma criatura descoberta ainda.</p>
                            % end
                        </div>
                    </section>

                    % if novas_criaturas:
                    <section class="card shadow-sm">
                        <div class="card-body">
                            <h2 class="h4">Novas criaturas</h2>
                            <ul class="list-unstyled mb-0">
                                % for entidade in novas_criaturas:
                                <li>
                                    {{entidade._nome}} (tags: {{", ".join(sorted(entidade._tags))}})
                                </li>
                                % end
                            </ul>
                        </div>
                    </section>
                    % end
                </div>
            </section>
        </main>
    </body>
</html>
