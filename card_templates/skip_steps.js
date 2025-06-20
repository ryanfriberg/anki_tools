/* 
w0: w_learn -> initial stability for newly learned card (good)
w1: w_relearn -> initial stability for a relearned card (good)
w2: w_grad -> initial stability for a graduating card (good from learning)
w3: w_easy -> the initial stability for an easy answer in learning
w4: w_stability_difficulty -> how difficulty affects stability gain
w5: w_stability_retrievability -> how retrievabilty affects stability gain
w6: w_stability_prev -> how previous stability affects stability gain
w7: w_difficulty_difficulty -> how difficulty affects future difficulty
w8: w_difficulty_retrievability -> how retrievability affects difficulty range
w9: w_difficulty_prev -> how prior difficulty affects new difficulty
w10: w_difficulty_good -> baseline difficulty change for good answers
w11: w_difficulty_hard -> ... for hard answers
w12: w_difficulty_easy -> ... for easy answers
w13: w_relearn_stability -> used in relearning stability updates
w14: w_decay -> decay constant in interval formula
w15: w_interval_factor -> scale factor in the same interval_formula
w16: w_recall_penalty -> stability penality when failing a review
*/

// console.log(
//     JSON.stringify(states, null, 4)
// );

function skipSteps(elapsed, path, steps) {
    let graduate = false;

    for (let i = 1; i < steps.length; i++) {
        if (elapsed > steps[i]) {
            path.scheduledSecs = elapsed - steps[i];
            let rem = path.remainingSteps ?? steps.length;
            path.remainingSteps = Math.max(0, rem - 1);
            graduate = (i >= (steps.length - 1));
        }
    }

    if (graduate) {
        let memState = path.memoryState;
        let stability = memState?.stability ?? 1;
        let interval = Math.round(((9 * stability) * ((1/0.93)-1)));

        return {
            scheduledDays: Math.max(1, interval),
            elapsedDays: 0,
            easeFactor: 2.5,
            lapses: 0,
            leeched: false,
            memoryState: memState,
        };
    }
    return null;
}

const learningSteps = [60, 300, 7200]; 
const relearningSteps = [300, 3600];

const goodLearning = states?.good?.normal?.learning;
let LearningElapsed = states.current.normal?.learning?.elapsedSecs;

const goodRelearning = states?.good?.normal?.relearning?.learning;
let ReLearningElapsed = states.current.normal?.relearning?.learning?.elapsedSecs;


if (states.current.normal?.learning) {
    const result = skipSteps(LearningElapsed, goodLearning, learningSteps);

    if (result) {
        states.good.normal = { review: result };
    }
}

if (states.current.normal?.relearning) {
    const result = skipSteps(ReLearningElapsed, goodRelearning, relearningSteps);

    if (result) {
        states.good.normal = { review: states.good.normal?.relearning?.review };
    }
}

// console.log(
//     JSON.stringify(states, null, 4)
// );