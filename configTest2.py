import tekore as tk

conf = tk.config_from_environment(return_refresh=False)

file = 'tekore.cfg'

token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)

tk.config_to_file(file, conf + (token.refresh_token,))
