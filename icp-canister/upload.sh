set -e

dfx canister call host_ai_model_backend clear_model_bytes
ic-file-uploader host_ai_model_backend append_model_bytes model.onnx
dfx canister call host_ai_model_backend setup_model
