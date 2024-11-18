import torch.nn as nn


class RecurrentModelWrapper(nn.Module):
    def __init__(self, policy):
        super(RecurrentModelWrapper, self).__init__()
        self.pi_features_extractor = policy.pi_features_extractor.to("cpu")
        self.vf_features_extractor = policy.vf_features_extractor.to("cpu")
        self.mlp_extractor = policy.mlp_extractor.to("cpu")
        self.action_net = policy.action_net.to("cpu")
        self.value_net = policy.value_net.to("cpu")

    def forward(self, prices, portfolio):
        observations = {"prices": prices, "portfolio": portfolio}

        pi_features = self.pi_features_extractor(observations)
        vf_features = self.vf_features_extractor(observations)

        policy_latent = self.mlp_extractor.policy_net(pi_features)
        value_latent = self.mlp_extractor.value_net(vf_features)

        action_logits = self.action_net(policy_latent)
        value = self.value_net(value_latent)

        return action_logits, value
