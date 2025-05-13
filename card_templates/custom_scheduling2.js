// console.log(
//     JSON.stringify(states, null, 4)
// );

// have the "good" button adapt the ease to towards 2.5 (avoids ease hell for SM2)
if (states.good.normal && states.good.normal.review && states.current.normal.review) {
    let oldEase = states.good.normal.review.easeFactor;
    let diff = 2.5 - oldEase;
    states.good.normal.review.easeFactor += Math.sign(diff) * Math.min(0.05, Math.abs(diff));
}

const modifiedStates = ["hard", "good"];
const learningSteps = [60, 300, 3600];
const relearningSteps = [300, 3600];

const current = states["current"].normal?.learning;
const re_current = states["current"].normal?.relearning;
if (current){
    const elapsed = current.elapsedSecs;
    for (const [j, state] of Object.entries(modifiedStates)) {
    
        const learning = states[state].normal?.learning;
        if (learning && (learning.remainingSteps > 0)) {
            const scheduled = learning.scheduledSecs;
            let index = learningSteps.indexOf(scheduled);
    
            while ((elapsed > scheduled) && (index < learningSteps.length)){
                learning.remainingSteps -= 1;
    
                if (index < learningSteps.length-1){
                    learning.scheduledSecs = learningSteps[index+1];
                } else if (state === "good") {
                    const new_intv = Math.round(learning.memoryState.stability);
                    const good = states[state].normal;
                    
                    delete good.learning;
                    good.review = {
                        "scheduledDays": new_intv,
                        "elapsedDays": 0,
                        "easeFactor": 2.5,
                        "lapses": 0,
                        "leeched": false,
                        "memoryState": {
                            "stability": learning.memoryState.stability,
                            "difficulty": learning.memoryState.difficulty
                        }
                    }
                }
                index += 1;
            }
        }
    }
} else if (re_current) {
    const elapsed = re_current.learning.elapsedSecs;

    for (const [j, state] of Object.entries(modifiedStates)) {
        if (states[state].normal?.relearning){
            const relearning = states[state].normal?.relearning.learning;
            if (relearning && (relearning.remainingSteps > 0)) {
                const scheduled = relearning.scheduledSecs;
                let index = relearningSteps.indexOf(scheduled);
        
                while ((elapsed > scheduled) && (index < relearningSteps.length)){
                    relearning.remainingSteps -= 1;
        
                    if (index < relearningSteps.length-1){
                        relearning.scheduledSecs = relearningSteps[index+1];
                    } else if (state === "good") {
                        const good = states[state].normal;
                        good.review = good.relearning.review;
                        if (good.relearning){
                            delete good.relearning;
                        }
                    }
                    index += 1;
                }
            }
        }
    }
}