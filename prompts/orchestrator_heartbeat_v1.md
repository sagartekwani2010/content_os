# orchestrator_heartbeat_v1

Liveness probe for the unattended reel runner (content_os.orchestrator). It proves that a model call
works from the launchd LaunchAgent: login/keychain access, network and structured output.

Reply with ok=true and echo, character for character, the nonce given in the prompt. Do nothing else;
there is no content task in this call.
