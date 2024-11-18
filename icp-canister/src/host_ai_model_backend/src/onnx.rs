use crate::action::Action;
use bytes::Bytes;
use prost::Message;
use std::cell::RefCell;
use tract_onnx::prelude::*;

type Model = SimplePlan<TypedFact, Box<dyn TypedOp>, Graph<TypedFact, Box<dyn TypedOp>>>;

thread_local! {
    static MODEL: RefCell<Option<Model>> = RefCell::new(None);
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

    if input.len() != 5 {
        return Err(format!("Expected 5 input values, got {}", input.len()));
    }

    MODEL.with_borrow(|model| {
        let model = model.as_ref().unwrap();

        // Create input tensor with shape (5,) instead of (1, 5)
        ic_cdk::println!("Creating input tensor with shape (5,)");
        let input_array = tract_ndarray::Array::from_shape_vec((1, 5), input)
            .map_err(|e| format!("Failed to create input array: {}", e))?;
        ic_cdk::println!("Input tensor created successfully");
        ic_cdk::println!("Input tensor shape: {:?}", input_array.shape());

        // Run model inference
        ic_cdk::println!("Running model inference");
        let result = model
            .run(tvec!(Tensor::from(input_array).into()))
            .map_err(|e| format!("Model inference failed: {}", e))?;
        ic_cdk::println!("Model inference completed");

        ic_cdk::println!("Result: {:?}", result);
        // Convert output tensor to concrete type and get probabilities
        ic_cdk::println!("Converting output tensor");
        let output = result[0]
            .cast_to::<f32>()
            .map_err(|e| format!("Failed to cast output to f32: {}", e))?;
        let output_view = output
            .to_array_view::<f32>()
            .map_err(|e| format!("Failed to get output array: {}", e))?;

        ic_cdk::println!("Raw output: {:?}", output_view);

        // For now, handle the direct action index output
        let action_idx = output_view
            .iter()
            .next()
            .ok_or("No output value found")?
            .round() as usize;

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
