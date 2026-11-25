# Secrets

All secrets are in Git, encrypted with SOPS and age (`.sops.yaml` in infra). The private key is with the owner (and
whoever is listed in `.sops.yaml`) and in the cluster as `flux-system/sops-age`.

- Edit: `sops clusters/prod/apps/auth/secret.sops.yaml` (decrypts in the editor, encrypts on save). Pods read env
  from Secrets at start: restart the Deployment afterwards.
- OpenTofu's: `tofu/secrets.sops.json`, used as `sops exec-env tofu/secrets.sops.json 'tofu -chdir=tofu plan'`.
  CI has the same values as GitHub secrets (`tofu.yml`).
- A value used in two places (an OIDC client secret: in auth's Secret and in the app's) is changed in both, in one PR.
- Add a person: their age public key to `.sops.yaml`, then `find . -name '*.sops.*' -exec sops updatekeys -y {} \;`.
- Rotate the age key: new key in `.sops.yaml`, `sops updatekeys` everywhere, new `sops-age` Secret, remove the old key.
