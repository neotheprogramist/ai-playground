use candid::CandidType;


#[derive(CandidType, Debug)]
pub enum Action {
    Hold = 0,
    Buy = 1,
    Sell = 2,
}
