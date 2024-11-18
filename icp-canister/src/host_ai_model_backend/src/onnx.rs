use crate::action::Action;
use bytes::Bytes;
use prost::Message;
use std::cell::RefCell;
use tract_onnx::prelude::*;
use tract_onnx::prelude::Tensor;

type Model = SimplePlan<TypedFact, Box<dyn TypedOp>, Graph<TypedFact, Box<dyn TypedOp>>>;

thread_local! {
    static MODEL: RefCell<Option<Model>> = RefCell::new(None);
}

pub fn setup_model(model_bytes: Bytes) -> TractResult<()> {
    ic_cdk::println!("Starting model setup with {} bytes", model_bytes.len());
    let proto: tract_onnx::pb::ModelProto = tract_onnx::pb::ModelProto::decode(model_bytes)?;
    ic_cdk::println!("Successfully decoded model proto");
    
    let model = tract_onnx::onnx()
        .model_for_proto_model(&proto)?;
    ic_cdk::println!("Created base model");
    
    let model = model
        .with_input_fact(0, InferenceFact::dt_shape(f32::datum_type(), tvec!(1, 10, 5)))?
        .with_input_fact(1, InferenceFact::dt_shape(f32::datum_type(), tvec!(1, 3)))?;
    ic_cdk::println!("Set input facts");
    
    let model = model
        .into_optimized()?
        .into_runnable()?;
    ic_cdk::println!("Model optimized and made runnable");

    MODEL.with_borrow_mut(|m| {
        *m = Some(model);
        ic_cdk::println!("Model successfully stored in thread local storage");
    });

    Ok(())
}

pub fn get_action(prices: Vec<f32>, portfolio: Vec<f32>) -> Result<Action, String> {
    ic_cdk::println!("=== Starting action inference ===");
    ic_cdk::println!("Input - Prices vector length: {}, values: {:?}", prices.len(), prices);
    ic_cdk::println!("Input - Portfolio vector length: {}, values: {:?}", portfolio.len(), portfolio);

    // Validate inputs
    // Window size is 10 x 5 features so 50
    if prices.len() != 50 {
        let err = format!("Invalid prices length: expected 50, got {}", prices.len());
        ic_cdk::println!("Error: {}", err);
        return Err(err);
    }

    if portfolio.len() != 3 {
        let err = format!("Invalid portfolio length: expected 3, got {}", portfolio.len());
        ic_cdk::println!("Error: {}", err);
        return Err(err);
    }

    MODEL.with_borrow(|model| {
        let model = model.as_ref().ok_or_else(|| {
            let err = "Model not initialized".to_string();
            ic_cdk::println!("Error: {}", err);
            err
        })?;

        // Create input tensors
        ic_cdk::println!("Creating input tensors...");
        let prices_array = tract_ndarray::Array::from_shape_vec((1, 10, 5), prices)
            .map_err(|e| {
                let err = format!("Failed to create prices array: {}", e);
                ic_cdk::println!("Error: {}", err);
                err
            })?;
        let portfolio_array = tract_ndarray::Array::from_shape_vec((1, 3), portfolio)
            .map_err(|e| {
                let err = format!("Failed to create portfolio array: {}", e);
                ic_cdk::println!("Error: {}", err);
                err
            })?;

        // Run model inference
        ic_cdk::println!("Running model inference with shapes - prices: {:?}, portfolio: {:?}", 
            prices_array.shape(), portfolio_array.shape());
        let result = model
            .run(tvec!(
                Tensor::from(prices_array).into(),
                Tensor::from(portfolio_array).into(),
            ))
            .map_err(|e| {
                let err = format!("Model inference failed: {}", e);
                ic_cdk::println!("Error: {}", err);
                err
            })?;
        ic_cdk::println!("Model inference completed successfully");

        // Process results
        let action_logits = result[0]
            .cast_to::<f32>()
            .map_err(|e| {
                let err = format!("Failed to cast output to f32: {}", e);
                ic_cdk::println!("Error: {}", err);
                err
            })?;

        let action_logits = action_logits
            .to_array_view::<f32>()
            .map_err(|e| {
                let err = format!("Failed to get output array: {}", e);
                ic_cdk::println!("Error: {}", err);
                err
            })?;

        ic_cdk::println!("Raw action logits: {:?}", action_logits);

        // Find action with highest logit
        let mut max_idx = 0;
        let mut max_val = action_logits[[0, 0]];
        for i in 1..3 {
            let val = action_logits[[0, i]];
            if val > max_val {
                max_val = val;
                max_idx = i;
            }
        }

        let action = match max_idx {
            0 => Action::Hold,
            1 => Action::Buy,
            2 => Action::Sell,
            _ => {
                let err = format!("Invalid action index: {}", max_idx);
                ic_cdk::println!("Error: {}", err);
                return Err(err);
            }
        };

        ic_cdk::println!("Selected action: {:?} (index: {}, confidence: {})", action, max_idx, max_val);
        ic_cdk::println!("=== Action inference completed ===");
        Ok(action)
    })
}
