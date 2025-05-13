// console.log(JSON.stringify(states, null, 4));

// have the "good" button adapt the ease to towards 2.5 (avoids ease hell for SM2)
if (states.good.normal && states.good.normal.review && states.current.normal.review) {
    let oldEase = states.good.normal.review.easeFactor;
    let diff = 2.5 - oldEase;
    states.good.normal.review.easeFactor += Math.sign(diff) * Math.min(0.05, Math.abs(diff));
}

// if the current card is in the review phase, update its "good" value if "again"
// is to be pressed
if (states.current.normal?.review){
    let interval = states.current.normal.review.scheduledDays;
    let scale = 0.1;
    let max_days = 12;
    let y = Math.min((scale * interval), max_days)
    let x = Math.max(1, Math.round(Math.random() * y));
    states.again.normal.relearning.review.scheduledDays = x;
}