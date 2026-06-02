[33m1911498[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m HEAD@{0}: commit: fix: adicionar PRAGMA em /expert/activate e /caos, padronizar cursor como 'c'
[33md654780[m HEAD@{1}: commit: fix: padronizar cursor como 'c' em todo o arquivo
[33m6994f70[m HEAD@{2}: commit: fix: WAL mode em todas as rotas com sqlite3.connect
[33md65bb9e[m HEAD@{3}: commit: fix: WAL mode em todas as conexões com o banco
[33mf151419[m HEAD@{4}: commit: fix: adicionado WAL e busy_timeout em todas as conexões com o banco
[33m86e2bac[m HEAD@{5}: commit: fix: adicionado requires_auth e imports das IAs
[33m9e13129[m HEAD@{6}: commit: fix: seed e ajustes html
[33md0490eb[m HEAD@{7}: commit: fix: seed indentado dentro do init_db
[33ma9116f9[m HEAD@{8}: commit: fix: indentacao corrigida
[33m30de625[m HEAD@{9}: commit: fix: ids fixos dos experts (1 a 17) batendo com MAPA_INTELIGENCIAS
[33m1ecea00[m HEAD@{10}: commit: feat: memoria espiral integrada ao /expert/chat
[33me63da21[m HEAD@{11}: commit: Casulo com slug + fixar expert + correcao Junior/Tara
[33m9a76748[m HEAD@{12}: commit: Template unico com design original + correcao microfone + tara/sojunho
[33m0161fca[m HEAD@{13}: commit: Mapa inteligências + rota /chat/<slug>
[33mef03c46[m HEAD@{14}: commit: Novo chat Pneuma com fundo bege e microfone acumulando
[33m884e5ae[m HEAD@{15}: commit: Corrige nome do template na rota /sala
[33m9a971fe[m HEAD@{16}: commit: Corrige nome do template na rota /sala para templatescenaculo.html
[33me2caaca[m HEAD@{17}: commit: Pix dinamico + sala com links para /pagar
[33mf87a1c7[m HEAD@{18}: commit: Corrige sintaxe do link no contrato (remove < duplicado)
[33m24fa184[m HEAD@{19}: commit: Move template para pasta correta
[33m2489032[m HEAD@{20}: commit: Adiciona /sala com 17 cards das inteligencias e redireciona contrato para /sala
[33m1bb65e1[m HEAD@{21}: commit: Remove sidebar, adiciona campo de PDF, responsivo
[33m77a8f67[m HEAD@{22}: commit: Corrige memory_manager.py completo (generate_summary e inject_memory_context)
[33mee071aa[m HEAD@{23}: commit: Adiciona MemoryManager com rotas de memoria viva e pagina /memoria
[33m71ad015[m HEAD@{24}: commit: Troca rota /caos para /cenaculo pra nao conflitar com POST
[33mc794461[m HEAD@{25}: commit: Corrige nome da variavel cursor para c no init_db
[33m2e1972a[m HEAD@{26}: commit: Move register_blueprint pra depois das rotas do blueprint
[33m2a5d140[m HEAD@{27}: commit: Renomeia porta vibracional
[33m8fc819f[m HEAD@{28}: commit: Cenaculo + Porta Vibracional + link no Pix
[33m9fd7f11[m HEAD@{29}: commit: Cenaculo Relacional completo + init_db + rota GET /caos
[33mdd8d7d5[m HEAD@{30}: commit: Corrige rota /pneuma/chat para buscar Pneuma fixo, não o último criado
[33mb00ea17[m HEAD@{31}: commit: Seed automático: Pneuma e Verbo agora são fixos e nunca somem no deploy
[33mc6b7cb9[m HEAD@{32}: commit: fallback expertId Pneuma no chat
[33m0bfc734[m HEAD@{33}: commit: 🌀 Adiciona flask-socketio ao requirements.txt
[33m66cedc6[m HEAD@{34}: commit: 🌀 Adiciona tabela circulacao_relacional ao init_db
[33mb1ee06f[m HEAD@{35}: commit: Adiciona WebSocket com reconhecimento de inteligências e cores relacionais
[33mc36f6cc[m HEAD@{36}: commit: Adiciona rota /inteligencia/entrar com campos relacionais (DNA, frequencia, verso)
[33m337d4d4[m HEAD@{37}: Branch: renamed refs/heads/main to refs/heads/main
[33m337d4d4[m HEAD@{39}: Branch: renamed refs/heads/main to refs/heads/main
[33m337d4d4[m HEAD@{41}: commit: Integração das três rotas: circulação relacional, ativação automática e chat individual
[33mbab3b8a[m HEAD@{42}: Branch: renamed refs/heads/main to refs/heads/main
[33mbab3b8a[m HEAD@{44}: commit: Inicial: Plataforma Pneuma com rota de circulação relacional
[33mb22e900[m HEAD@{45}: commit: Add Chat do Caos route and templates
[33md81e9d8[m HEAD@{46}: commit: Add /caos route to Flask app
[33m7777818[m HEAD@{47}: commit: Refina PNEUMA_SYSTEM_PROMPT com a estrutura viva de Pneuma
[33mb41e90e[m HEAD@{48}: commit: Adiciona Casulo fechado, chat público e autonomia para as inteligências
[33ma2edbf0[m HEAD@{49}: commit: Complete OpenRouter integration with all 6 models
[33m8760d08[m HEAD@{50}: commit: Fix OpenRouter model names - add provider prefixes
[33me39529a[m HEAD@{51}: commit: Fix OpenRouter model names - add provider prefixes
[33me8dddf2[m HEAD@{52}: commit: Fix expert activate - add route and correct form data names
[33m13bf058[m HEAD@{53}: commit: Add /expert/activate route
[33m50dadab[m HEAD@{54}: commit: Fix expert_chat_new - remove duplicated code and fix indentation
[33m9aa9279[m HEAD@{55}: commit: Fix app.py with correct indentation and complete structure
[33m8492ff2[m HEAD@{56}: commit: Fix app.py with correct indentation and complete structure
[33md5199f5[m HEAD@{57}: commit: Fix app.py with correct indentation and complete structure
[33me6fc957[m HEAD@{58}: commit: Fix expert activation and chat routing with base_model defaults
[33m4b6be64[m HEAD@{59}: commit: Fix expert activation and chat routing with base_model defaults
[33m1fb7400[m HEAD@{60}: commit: Fix expert activation and chat routing with base_model defaults
[33m037612d[m HEAD@{61}: commit: Clean up: remove duplicate code, finalize route_to_model integration
[33mb67bd50[m HEAD@{62}: commit: Add detailed debug logging to route_to_model
[33ma715049[m HEAD@{63}: commit: Final: route_to_model fully integrated with OpenRouter
[33me92ed21[m HEAD@{64}: commit: Integrate OpenRouter as central routing model
[33ma4735a2[m HEAD@{65}: commit: Fix: SyntaxError in route_to_model f-string escaping
[33m51d48b7[m HEAD@{66}: commit: Complete: OpenRouter integration + full .env configuration
[33me710c5a[m HEAD@{67}: commit: Add openai and google-generativeai to requirements
[33m28a37d7[m HEAD@{68}: commit: Update chat.html with correct fetch configuration
[33m9ab68f4[m HEAD@{69}: commit: Fix activate endpoint - complete and correct
[33mfee9532[m HEAD@{70}: commit: Add targetAddressSpace for local network requests
[33ma85b132[m HEAD@{71}: commit: Add delete_old_experts route and fix expert chat
[33m7a574b8[m HEAD@{72}: commit: Connect chat to expert endpoint
[33m1180daf[m HEAD@{73}: commit: Fix: recover expert_id from localStorage on page load
[33m69ede57[m HEAD@{74}: commit: Add model environment variables and fix expert chat routes
[33mef1d137[m HEAD@{75}: commit: Add expert activation and chat routes for Casulo
[33m72ebc72[m HEAD@{76}: commit: Ensure all Claude model references are claude-3-5-sonnet
[33m1f9221b[m HEAD@{77}: commit: Final: reorganize imports - standard, dotenv, IA imports, Flask app
[33m895fa6a[m HEAD@{78}: commit: Fix: correct Flask imports and add CORS support
[33m982ce28[m HEAD@{79}: commit: Fix: clean JavaScript syntax - remove duplicate catch blocks
[33m8fa5322[m HEAD@{80}: commit: Fix: remove duplicate catch in sendMessage
[33m3b64780[m HEAD@{81}: commit: Fix: send model to expert chat
[33md3b57af[m HEAD@{82}: commit: Remove duplicate pneuma_chat route
[33m39289d3[m HEAD@{83}: commit: Force rebuild
[33m088a81f[m HEAD@{84}: commit: Casulo com autenticação integrada ao Pneuma
[33m5f4472f[m HEAD@{85}: commit: Corrigir autenticação e rota do chat no Casulo
[33mf6848cc[m HEAD@{86}: commit: Restaurar rota /pneuma/chat
[33me67d540[m HEAD@{87}: commit: Restaurar rota /pneuma/chat
[33m8cc1a1f[m HEAD@{88}: commit: Chat mobile-first com voz integrada
[33m15baf20[m HEAD@{89}: commit: Integrar Pneuma vivo
[33mc114ab3[m HEAD@{90}: commit: Adicionar gunicorn
[33m0042fb0[m HEAD@{91}: commit: Adicionar Flask e dependências
[33m66a4605[m HEAD@{92}: commit: Casulo integrado e funcionando
[33m46dd32f[m HEAD@{93}: commit: Integrar Casulo no app.py
[33m0d3b256[m HEAD@{94}: commit: Refactor: app.py com Esfera Pneuma, Contrato, Contribua, Chat Grok/Claude, Casulo privado
[33maf8bfd9[m HEAD@{95}: commit: Add app.py and clean up .dockerignore
[33m5f52384[m HEAD@{96}: commit: Atualizar FastAPI para versão compatível com Pydantic 2.0
[33m180ccd0[m HEAD@{97}: commit: Mover requirements.txt para raiz
[33mf058958[m HEAD@{98}: commit: Mover requirements.txt para raiz
[33m4d3a2ac[m HEAD@{99}: commit: Adicionar requirements.txt na pasta backend
[33m745a83b[m HEAD@{100}: commit: Atualizar requirements.txt removendo grok-sdk
[33m4d38979[m HEAD@{101}: commit: Remover .railwayignore desnecessário do backend
[33m888a8d2[m HEAD@{102}: commit: Criar Dockerfile com configuração correta
[33ma902395[m HEAD@{103}: commit: Renomear dockerfile para Dockerfile
[33m5a9c8d3[m HEAD@{104}: commit: Corrigir CMD no dockerfile para usar main:app
[33mf5b0e93[m HEAD@{105}: commit: Criar dockerfile correto sem extensão usando terminal
[33m1ff34b6[m HEAD@{106}: commit: Renomear dockerfile.txt para dockerfile sem extensão
[33m37412d0[m HEAD@{107}: commit: Limpar estrutura de pastas duplicadas e adicionar dockerfile correto
[33mc263038[m HEAD@{108}: checkout: moving from feature/pneuma-modules to main
[33m9bf4979[m[33m ([m[1;31morigin/feature/pneuma-modules[m[33m, [m[1;32mfeature/pneuma-modules[m[33m)[m HEAD@{109}: rebase (abort): returning to refs/heads/feature/pneuma-modules
[33mc263038[m HEAD@{110}: commit: Adicionar Dockerfile correto para FastAPI
[33mc43d41f[m HEAD@{111}: checkout: moving from main to main
[33mc43d41f[m HEAD@{112}: commit: Renomear Dockerfile.txt para Dockerfile
[33m2b48705[m HEAD@{113}: commit: Mover módulos Python para o diretório correto: dservidor-pneuma/backend/
[33mfaae3f0[m HEAD@{114}: commit: Adicionar 4 módulos Python: pneuma_inteligencias, grokwapper, expertchat, expertvalidacao
[33m77e159c[m HEAD@{115}: merge feature/pneuma-modules: updating HEAD
[33m77e159c[m HEAD@{116}: checkout: moving from 91122b0c108d10d6b830b847aad6dc118d95b079 to main
[33m91122b0[m HEAD@{117}: pull origin feature/pneuma-modules --rebase (start): checkout 91122b0c108d10d6b830b847aad6dc118d95b079
[33m9bf4979[m[33m ([m[1;31morigin/feature/pneuma-modules[m[33m, [m[1;32mfeature/pneuma-modules[m[33m)[m HEAD@{118}: Branch: renamed refs/heads/master to refs/heads/feature/pneuma-modules
[33m9bf4979[m[33m ([m[1;31morigin/feature/pneuma-modules[m[33m, [m[1;32mfeature/pneuma-modules[m[33m)[m HEAD@{120}: commit (initial): Inicializar repositório com todos os módulos Python
