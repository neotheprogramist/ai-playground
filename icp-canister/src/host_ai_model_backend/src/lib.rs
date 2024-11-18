use action::Action;
use constants::{MODEL_FILE, WASI_MEMORY_ID};
use getrandom::register_custom_getrandom;
use ic_stable_structures::{memory_manager::MemoryManager, DefaultMemoryImpl};
use std::cell::RefCell;

mod action;
mod constants;
mod get_random_bypass;
mod onnx;
mod storage;

thread_local! {
    static MEMORY_MANAGER: RefCell<MemoryManager<DefaultMemoryImpl>> =
        RefCell::new(MemoryManager::init(DefaultMemoryImpl::default()));
}

#[ic_cdk::update]
fn clear_model_bytes() {
    storage::clear_bytes(MODEL_FILE);
}

#[ic_cdk::update]
fn append_model_bytes(bytes: Vec<u8>) {
    storage::append_bytes(MODEL_FILE, bytes);
}

#[ic_cdk::init]
fn init() {
    let wasi_memory = MEMORY_MANAGER.with(|m| m.borrow().get(WASI_MEMORY_ID));
    ic_wasi_polyfill::init_with_memory(&[0u8; 32], &[], wasi_memory);
}

#[ic_cdk::post_upgrade]
fn post_upgrade() {
    let wasi_memory = MEMORY_MANAGER.with(|m| m.borrow().get(WASI_MEMORY_ID));
    ic_wasi_polyfill::init_with_memory(&[0u8; 32], &[], wasi_memory);
}

#[ic_cdk::update]
fn setup_model() -> Result<(), String> {
    onnx::setup_model(storage::bytes(MODEL_FILE))
        .map_err(|err| format!("Failed to setup model: {}", err))
}

#[ic_cdk::update]
fn get_action(input: Vec<f32>, portfolio: Vec<f32>) -> Result<Action, String> {
    onnx::get_action(input, portfolio)
        .map_err(|err| format!("Failed to get action: {}", err))
}

register_custom_getrandom!(get_random_bypass::always_fail);
ic_cdk::export_candid!();
