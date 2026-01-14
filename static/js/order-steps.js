const steps = document.querySelectorAll(".step");
const indicators = document.querySelectorAll(".step-indicator span");

let currentStep = 0;

function updateSteps() {
    steps.forEach((step, index) => {
        step.classList.toggle("active", index === currentStep);
        indicators[index].classList.toggle("active", index === currentStep);
    });
}

document.querySelectorAll(".next-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateSteps();
        }
    });
});

document.querySelectorAll(".back-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        if (currentStep > 0) {
            currentStep--;
            updateSteps();
        }
    });
});
