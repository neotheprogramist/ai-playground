import { createActor, canisterId } from '../../../declarations/host_ai_model_backend';

const host = `http://localhost:4943`;


export const anonymousBackend = createActor(canisterId, { agentOptions: { host } });
