use crate::action::Action;
use bytes::Bytes;
use prost::Message;
use std::cell::RefCell;
use tract_onnx::prelude::*;

// Define struct to hold LSTM states
#[derive(Clone)]
pub struct LSTMStates {
    actor_h: Tensor,
    actor_c: Tensor,
    critic_h: Tensor,
    critic_c: Tensor,
}

impl Default for LSTMStates {
    fn default() -> Self {
        // Initialize with zeros - adjust dimensions based on your model
        let shape = [1, 1, 256]; // [num_layers, batch_size, hidden_size]
        Self {
            actor_h: Tensor::zero::<f32>(&shape).unwrap(),
            actor_c: Tensor::zero::<f32>(&shape).unwrap(),
            critic_h: Tensor::zero::<f32>(&shape).unwrap(),
            critic_c: Tensor::zero::<f32>(&shape).unwrap(),
        }
    }
}

type Model = SimplePlan<TypedFact, Box<dyn TypedOp>, Graph<TypedFact, Box<dyn TypedOp>>>;

thread_local! {
    static MODEL: RefCell<Option<Model>> = RefCell::new(None);
    static LSTM_STATES: RefCell<LSTMStates> = RefCell::new(LSTMStates::default());
}

pub fn setup_model(model_bytes: Bytes) -> TractResult<()> {
    let proto: tract_onnx::pb::ModelProto = tract_onnx::pb::ModelProto::decode(model_bytes)?;
    let model = tract_onnx::onnx()
        .model_for_proto_model(&proto)?
        // .into_runnable_with_options(Pla)
        .into_optimized()?
        .into_runnable()?;

    MODEL.with_borrow_mut(|m| {
        *m = Some(model);
    });

    Ok(())
}

pub fn get_action(input: Vec<f32>) -> Result<Action, String> {
    ic_cdk::println!("Received input vector length: {}", input.len());
    ic_cdk::println!("Input values: {:?}", input);

    if input.len() != 8 {  // Adjust expected input size
        return Err(format!("Expected 8 input values, got {}", input.len()));
    }

    MODEL.with_borrow(|model| {
        let model = model.as_ref().unwrap();

        // Get current LSTM states
        let states = LSTM_STATES.with(|s| s.borrow().clone());

        // Prepare input tensors
        let observations = tract_ndarray::Array::from_shape_vec((1, 8), input)
            .map_err(|e| format!("Failed to create input array: {}", e))?;
        let episode_starts = Tensor::zero::<f32>(&[1]).unwrap();

        // Run model inference with all inputs
        let result = model
            .run(tvec!(
                Tensor::from(observations).into(),
                states.actor_h.into(),
                states.actor_c.into(),
                states.critic_h.into(),
                states.critic_c.into(),
                episode_starts.into(),
            ))
            .map_err(|e| format!("Model inference failed: {}", e))?;

        // Extract action logits and update LSTM states
        let action_logits = &result[0];
        let new_states = LSTMStates {
            actor_h: result[2].clone().into_tensor(),
            actor_c: result[3].clone().into_tensor(),
            critic_h: result[4].clone().into_tensor(), 
            critic_c: result[5].clone().into_tensor(),
        };

        // Update stored LSTM states
        LSTM_STATES.with(|s| *s.borrow_mut() = new_states);

        // Convert logits to action
        let output_view = action_logits
            .cast_to::<f32>()
            .map_err(|e| format!("Failed to cast output to f32: {}", e))?;

        let output_view = output_view
            .to_array_view::<f32>()
            .map_err(|e| format!("Failed to get output array: {}", e))?;

        // Get action with highest probability
        let action_idx = output_view
            .iter()
            .enumerate()
            .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
            .map(|(idx, _)| idx)
            .ok_or("No output value found")?;

        let action = match action_idx {
            0 => Action::Hold,
            1 => Action::Buy,
            2 => Action::Sell,
            _ => return Err(format!("Invalid action index: {}", action_idx)),
        };

        ic_cdk::println!("Selected action: {:?}", action);
        Ok(action)
    })
}

// Add function to reset LSTM states
pub fn reset_lstm_states() {
    LSTM_STATES.with(|s| *s.borrow_mut() = LSTMStates::default());
}
